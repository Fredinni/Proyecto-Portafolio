import asyncio
import base64
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
import time
import uuid
import websockets

ROOT = Path(__file__).resolve().parents[1]
for name in ('ai_voice_agent', 'pfsense_pfctl_engine', 'asterisk_pbx'):
    sys.path.insert(0, str(ROOT / 'src' / name))
from audio_activity import AudioActivityGate
from gemini_live_client import GeminiLiveVoiceClient
from incident_store import save_identity, read_identity
from pfctl_wrapper import PfctlWrapper
from soar_tools_executor import SoarToolsExecutor
from voice_ssh_command import validate_command
from live_audio_server import MicrophoneBuffer, handle_call, packet, read_packet


class SpeechBoundaryTests(unittest.TestCase):
    def test_silence_does_not_stream_or_trigger_a_false_turn(self):
        gate = AudioActivityGate()
        for _ in range(100):
            self.assertEqual(gate.feed(b'\0' * 640), ([], False))
        self.assertLessEqual(gate.prefix_size, 320 * 9)

    def test_voice_prefix_silence_flush_and_next_utterance(self):
        gate = AudioActivityGate()
        quiet = b'\x01\x00' * 320
        voice = b'\x00\x04' * 320
        for _ in range(6):gate.feed(quiet)
        chunks, end = gate.feed(voice)
        self.assertFalse(end)
        self.assertEqual(chunks[-1], voice)
        self.assertIn(quiet, chunks)
        endings = [gate.feed(quiet)[1] for _ in range(60)]
        self.assertEqual(sum(endings), 1)
        chunks, end = gate.feed(voice)
        self.assertTrue(chunks)
        self.assertEqual(chunks[-1], voice)
        self.assertFalse(end)


class EvidenceTests(unittest.TestCase):
    def test_store_reads_only_allowlisted_identity_and_rejects_traversal(self):
        incident = {'attacker_ip':'93.184.216.34', 'target_ip':'192.168.20.50', 'timestamp':'2026-11-16',
                    'attacker_public_ip':'93.184.216.34','http_endpoint':'/?password=not-a-real-secret'}
        with tempfile.TemporaryDirectory() as directory:
            identifier = save_identity(directory, incident)
            result = read_identity(directory, identifier)
            self.assertEqual(result['source'], 'PFSENSE_EVE')
            self.assertEqual(result['incident']['attacker_public_ip'], incident['attacker_ip'])
            self.assertNotIn('http_endpoint', result['incident'])
            for invalid in ('../../config.xml', 'a'*63, 'a'*64+';id'):
                with self.assertRaises(ValueError):read_identity(directory, invalid)

    def test_wrapper_and_tool_query_the_specific_pfsense_incident(self):
        identifier = 'a'*64
        incident = {'incident_id':identifier,'attacker_ip':'93.184.216.34','target_ip':'192.168.20.50'}
        row = {**incident,'attacker_public_ip':incident['attacker_ip'],'victim_private_ip':incident['target_ip']}
        fw = PfctlWrapper({'simulation_mode':False})
        fw._exec_command = Mock(return_value=subprocess.CompletedProcess([],0,json.dumps(
            {'success':True,'source':'PFSENSE_EVE','incident':row}),''))
        result = SoarToolsExecutor(incident=incident,pfctl=fw).execute_tool_call('get_incident_details',{})
        self.assertTrue(result['identity_query_verified'])
        self.assertEqual(result['source'],'PFSENSE_EVE')
        fw._exec_command.assert_called_once_with(['kronos-incident-identity',identifier])

    def test_remote_reader_command_has_fixed_script_and_validated_identifier(self):
        result = validate_command('kronos-incident-identity '+'a'*64,'snort2c')
        self.assertEqual(result[0],'/usr/local/bin/python3.11')
        self.assertTrue(result[1].endswith('incident_store.py'))
        with self.assertRaises(ValueError):validate_command('kronos-incident-identity ../../config.xml','snort2c')

    def test_conflicting_remote_identity_never_overwrites_call_target(self):
        incident={'incident_id':'a'*64,'attacker_ip':'93.184.216.34','target_ip':'192.168.20.50'}
        fw=Mock()
        fw.get_incident_identity.return_value={'success':True,'incident':{'attacker_ip':'1.1.1.1','target_ip':'192.168.20.50'}}
        result=SoarToolsExecutor(incident=incident,pfctl=fw).execute_tool_call('get_incident_details',{})
        self.assertFalse(result['identity_query_verified'])
        self.assertEqual(result['incident']['attacker_ip'],incident['attacker_ip'])


class StartupRetryTests(unittest.IsolatedAsyncioTestCase):
    def test_opening_asks_a_specific_confirmation_only_for_a_verified_mutable_block(self):
        incident={'attacker_ip':'203.0.113.45','firewall_state_at_call':{'verified':True,'is_blocked':True}}
        self.assertIn('¿Quieres que desbloquee esta IP?',GeminiLiveVoiceClient.opening_instruction(incident))
        self.assertNotIn('¿Quieres que desbloquee esta IP?',GeminiLiveVoiceClient.opening_instruction({**incident,'source_protected':True}))
        self.assertNotIn('¿Quieres que desbloquee esta IP?',GeminiLiveVoiceClient.opening_instruction({'attacker_ip':'203.0.113.45'}))

    async def test_contextual_yes_executes_once_even_if_model_only_asks_again(self):
        ip='203.0.113.45'
        fw=Mock(simulation_mode=False,table_name='test_table')
        fw.unblock_ip.return_value=True
        fw.get_ip_status.return_value={'success':True,'verified':True,'is_blocked':False}
        tools=SoarToolsExecutor({'authorized_extensions':['1004']},{'attacker_ip':ip,'operator_extension':'1004'},pfctl=fw)
        receipts=[]
        async def fake(ws):
            await ws.recv();await ws.send('{"setupComplete":{}}');await ws.recv()
            await ws.send(json.dumps({'serverContent':{'outputTranscription':{'text':'¿Quieres que desbloquee esta IP?'},'generationComplete':True}}))
            while True:
                message=json.loads(await ws.recv())
                if 'audio' in message.get('realtimeInput',{}):break
            await ws.send(json.dumps({'serverContent':{'inputTranscription':{'text':'Sí, por favor.','finished':True}}}))
            while True:
                message=json.loads(await ws.recv())
                if 'clientContent' in message:break
            self.assertIn('KRONOS_ACTION_RESULT',message['clientContent']['turns'][0]['parts'][0]['text'])
            await ws.send(json.dumps({'toolCall':{'functionCalls':[{'id':'duplicate','name':'unblock_ip','args':{'ip':ip}}]}}))
            while True:
                message=json.loads(await ws.recv())
                if 'toolResponse' in message:
                    receipts.extend(message['toolResponse']['functionResponses']);break
            await ws.send(json.dumps({'serverContent':{'outputTranscription':{'text':'Cambio confirmado.'},'generationComplete':True}}))
        async def mic():
            i=0
            while True:
                yield (b'\x00\x04' if i<8 else b'\0\0')*320;i+=1;await asyncio.sleep(.02)
        async def sink(*args):pass
        async with websockets.serve(fake,'127.0.0.1',0) as server:
            url='ws://127.0.0.1:'+str(server.sockets[0].getsockname()[1])
            client=GeminiLiveVoiceClient(api_key='test',connect=lambda _,**kw:websockets.connect(url,**kw))
            await asyncio.wait_for(client.start_voice_session({},mic(),sink,tools,sink),5)
        fw.unblock_ip.assert_called_once_with(ip)
        self.assertTrue(receipts[0]['response']['already_executed'])

    def test_current_live_model_uses_blocking_tools_to_preserve_voice_authorization(self):
        client=GeminiLiveVoiceClient(api_key='test',model='gemini-3.8-live')
        tools=client.setup_message({})['setup']['tools'][0]['functionDeclarations']
        self.assertTrue(all(tool['behavior']=='BLOCKING' for tool in tools))

    async def test_silent_initial_session_recovers_on_the_same_audiosocket_call(self):
        attempts = []
        async def fake(ws):
            attempts.append(1)
            number=len(attempts)
            await ws.recv()
            await ws.send('{"setupComplete":{}}')
            await ws.recv()
            if number == 1:
                await asyncio.sleep(.8)
                return
            await ws.send(json.dumps({'serverContent':{'modelTurn':{'parts':[{'inlineData':{
                'mimeType':'audio/pcm;rate=24000','data':base64.b64encode(b'\x00\x04'*2400).decode()}}]},'turnComplete':True}}))
            await asyncio.sleep(.2)
        async with websockets.serve(fake,'127.0.0.1',0) as mock:
            url='ws://127.0.0.1:'+str(mock.sockets[0].getsockname()[1])
            factory=lambda:GeminiLiveVoiceClient(api_key='test',connect=lambda _,**kw:websockets.connect(url,**kw))
            with tempfile.TemporaryDirectory() as directory:
                sid=str(uuid.uuid4())
                (Path(directory)/(sid+'.json')).write_text(json.dumps({'created_at':time.time(),'operator_extension':'1004','mode':'DIRECT_CALL'}))
                with patch('gemini_live_client.INITIAL_AUDIO_TIMEOUT_SECONDS',.05):
                    server=await asyncio.start_server(lambda r,w:handle_call(r,w,{},directory,factory),'127.0.0.1',0)
                    async with server:
                        reader,writer=await asyncio.open_connection('127.0.0.1',server.sockets[0].getsockname()[1])
                        writer.write(packet(1,uuid.UUID(sid).bytes));await writer.drain()
                        heard=False
                        while True:
                            kind,payload=await asyncio.wait_for(read_packet(reader),2)
                            if kind==0:break
                            heard=heard or any(payload)
                        self.assertTrue(heard)
                        self.assertEqual(len(attempts),2)
                        writer.close();await writer.wait_closed()

    async def test_audio_setup_buffer_discards_stale_frames_without_stopping_listening(self):
        buffered = MicrophoneBuffer(max_frames=3)
        for frame in (b'old-1',b'old-2',b'fresh-1',b'fresh-2'):
            buffered.push(frame)
        self.assertEqual(buffered.dropped,1)
        stream=buffered.stream()
        self.assertEqual(await anext(stream),b'old-2')
        self.assertEqual(await anext(stream),b'fresh-1')
        self.assertEqual(await anext(stream),b'fresh-2')
        buffered.push(None)
        with self.assertRaises(StopAsyncIteration):await anext(stream)

    async def test_transient_setup_timeout_is_retried_before_any_call_content(self):
        class Socket:
            def __init__(self, fail):self.fail=fail;self.closed=False;self.sent=[]
            async def send(self, value):self.sent.append(json.loads(value))
            async def recv(self):
                if self.fail:raise TimeoutError()
                return '{"setupComplete":{}}'
            async def close(self):self.closed=True
        first, second = Socket(True), Socket(False)
        sockets=iter((first,second))
        async def connect(*args,**kwargs):return next(sockets)
        client=GeminiLiveVoiceClient(api_key='test',connect=connect)
        async with client.open_session('unused',{'session_id':'test'}) as socket:
            self.assertIs(socket,second)
            self.assertTrue(first.closed)
            self.assertEqual(len(second.sent),1)
        self.assertTrue(second.closed)
