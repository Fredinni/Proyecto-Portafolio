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


class UnblockReliabilityRegressionTests(unittest.IsolatedAsyncioTestCase):
    def test_chilean_explicit_and_contextual_phrases_authorize_unblock(self):
        ip = '181.42.184.12'
        for phrase in [
            'Sí, desbloquéamela por favor',
            'Oye, como estaba probando yo, desbloquéame la IP',
            'Quítame el bloqueo de esa IP',
            'Sácame del bloqueo por favor',
            'Levanta el bloqueo de la IP',
        ]:
            with self.subTest(phrase=phrase):
                fw = Mock(simulation_mode=False, table_name='snort2c')
                fw.unblock_ip.return_value = True
                fw.get_ip_status.return_value = {'success': True, 'verified': True, 'is_blocked': False}
                tools = SoarToolsExecutor({'authorized_extensions': ['1004']},
                                          {'attacker_ip': ip, 'operator_extension': '1004'}, pfctl=fw)
                tools.observe_input(phrase)
                res = tools.execute_tool_call('unblock_ip', {'ip': ip, 'reason': 'QA'})
                self.assertTrue(res['verified'])
                fw.unblock_ip.assert_called_once_with(ip)

        for yes_phrase in ['Sí, claro, porfa', 'Ya, dale', 'Sí, dale nomás', 'Claro, por favor']:
            with self.subTest(yes_phrase=yes_phrase):
                fw = Mock(simulation_mode=False, table_name='snort2c')
                fw.unblock_ip.return_value = True
                fw.get_ip_status.return_value = {'success': True, 'verified': True, 'is_blocked': False}
                tools = SoarToolsExecutor({'authorized_extensions': ['1004']},
                                          {'attacker_ip': ip, 'operator_extension': '1004'}, pfctl=fw)
                tools.observe_output('¿Quieres que desbloquee esta IP?')
                tools.finish_turn()
                tools.observe_input(yes_phrase)
                self.assertEqual(tools.policy.confirmed_unblock_target(), ip)
                res = tools.execute_tool_call('unblock_ip', {'ip': ip, 'reason': 'QA'})
                self.assertTrue(res['verified'])

    def test_interim_filler_turn_preserves_unconsumed_order_but_never_leaks_refusal(self):
        ip = '181.42.184.12'
        fw = Mock(simulation_mode=False, table_name='snort2c')
        fw.unblock_ip.return_value = True
        fw.get_ip_status.return_value = {'success': True, 'verified': True, 'is_blocked': False}
        tools = SoarToolsExecutor({'authorized_extensions': ['1004']},
                                  {'attacker_ip': ip, 'operator_extension': '1004'}, pfctl=fw)
        tools.observe_input('Desbloquéame la IP por favor')
        tools.observe_output('Un momento, reviso el firewall.')
        tools.finish_turn()
        res = tools.execute_tool_call('unblock_ip', {'ip': ip})
        self.assertTrue(res['verified'])
        # Single consumption remains enforced after stashed order is used.
        self.assertFalse(tools.execute_tool_call('unblock_ip', {'ip': ip})['success'])

        fw2 = Mock(simulation_mode=False, table_name='snort2c')
        tools2 = SoarToolsExecutor({'authorized_extensions': ['1004']},
                                   {'attacker_ip': ip, 'operator_extension': '1004'}, pfctl=fw2)
        tools2.observe_input('No la desbloquees')
        tools2.observe_output('Entendido.')
        tools2.finish_turn()
        self.assertFalse(tools2.execute_tool_call('unblock_ip', {'ip': ip})['success'])
        fw2.unblock_ip.assert_not_called()

    def test_direct_call_lists_blocked_ip_and_allows_confirmed_unblock(self):
        ip = '181.42.184.12'
        fw = Mock(simulation_mode=False, table_name='snort2c')
        fw.list_blocked_ips_status.return_value = {
            'success': True, 'verified': True, 'table': 'snort2c', 'blocked_ips': [ip], 'count': 1
        }
        fw.unblock_ip.return_value = True
        fw.get_ip_status.return_value = {'success': True, 'verified': True, 'is_blocked': False}
        tools = SoarToolsExecutor({'authorized_extensions': ['1004'], 'protected_ips': ['192.168.99.10']},
                                  {'mode': 'DIRECT_CALL', 'operator_extension': '1004'}, pfctl=fw)
        listed = tools.execute_tool_call('list_blocked_ips', {})
        self.assertEqual(listed['blocked_ips'], [ip])
        tools.observe_output(f'Veo bloqueada la IP {ip} en snort2c. ¿Quieres que desbloquee esta IP?')
        tools.finish_turn()
        tools.observe_input('Sí, por favor.')
        self.assertEqual(tools.policy.confirmed_unblock_target(), ip)
        res = tools.execute_tool_call('unblock_ip', {'ip': ip})
        self.assertTrue(res['verified'])
        fw.unblock_ip.assert_called_once_with(ip)

    async def test_pre_greeting_noise_does_not_emit_early_stream_end_and_allows_recovery(self):
        events = []
        ip = '181.42.184.12'
        fw = Mock(simulation_mode=False, table_name='snort2c')
        fw.unblock_ip.return_value = True
        fw.get_ip_status.return_value = {'success': True, 'verified': True, 'is_blocked': False}
        tools = SoarToolsExecutor({'authorized_extensions': ['1004']},
                                  {'attacker_ip': ip, 'operator_extension': '1004'}, pfctl=fw)

        async def fake(ws):
            await ws.recv()
            await ws.send('{"setupComplete":{}}')
            await ws.recv()
            # Wait briefly before greeting audio while early mic click+silence runs.
            await asyncio.sleep(.25)
            await ws.send(json.dumps({
                'serverContent': {'outputTranscription': {'text': '¿Quieres que desbloquee esta IP?'},
                                  'generationComplete': True}
            }))
            # Model prematurely asks for unblock before valid input -> local rejection only.
            await ws.send(json.dumps({'toolCall': {'functionCalls': [{'id': 't1', 'name': 'unblock_ip', 'args': {'ip': ip}}]}}))
            while True:
                msg = json.loads(await ws.recv())
                events.append(msg)
                if 'toolResponse' in msg:
                    self.assertFalse(msg['toolResponse']['functionResponses'][0]['response']['verified'])
                    break
            # Operator then confirms via ASR finished without needing AudioActivityGate end.
            await ws.send(json.dumps({'serverContent': {'inputTranscription': {'text': 'Sí, porfa', 'finished': True}}}))
            while True:
                msg = json.loads(await ws.recv())
                events.append(msg)
                if 'clientContent' in msg and 'KRONOS_ACTION_RESULT' in msg['clientContent']['turns'][0]['parts'][0]['text']:
                    break

        async def mic():
            # Early click + quiet before greeting finishes, then keep channel open.
            for frame in ([b'\x00\x04' * 320] * 2 + [b'\x00\x00' * 320] * 45):
                yield frame
                await asyncio.sleep(.002)
            while True:
                yield b'\x00\x00' * 320
                await asyncio.sleep(.05)

        async def sink(*args):
            pass

        async with websockets.serve(fake, '127.0.0.1', 0) as server:
            url = 'ws://127.0.0.1:' + str(server.sockets[0].getsockname()[1])
            client = GeminiLiveVoiceClient(api_key='test', connect=lambda _, **kw: websockets.connect(url, **kw))
            await asyncio.wait_for(client.start_voice_session({'attacker_ip': ip, 'operator_extension': '1004'}, mic(), sink, tools, sink), 6)
        # Early click+silence before greeting must NOT have emitted audioStreamEnd.
        early_ends = [m for m in events if m.get('realtimeInput', {}).get('audioStreamEnd')]
        self.assertEqual(early_ends, [])
        fw.unblock_ip.assert_called_once_with(ip)

    async def test_burst_greeting_without_turn_complete_does_not_false_stall_after_speech(self):
        ip = '181.42.184.12'
        fw = Mock(simulation_mode=False, table_name='snort2c')
        fw.unblock_ip.return_value = True
        fw.get_ip_status.return_value = {'success': True, 'verified': True, 'is_blocked': False}
        tools = SoarToolsExecutor({'authorized_extensions': ['1004']}, {'attacker_ip': ip, 'operator_extension': '1004'}, pfctl=fw)

        async def fake(ws):
            await ws.recv()
            await ws.send('{"setupComplete":{}}')
            await ws.recv()
            # Greeting audio chunk arrives without turnComplete/generationComplete.
            await ws.send(json.dumps({'serverContent': {'modelTurn': {'parts': [{'inlineData': {
                'mimeType': 'audio/pcm;rate=24000', 'data': base64.b64encode(b'\x00\x04' * 480).decode()}}]},
                'outputTranscription': {'text': '¿Quieres que desbloquee la IP 181.42.184.12?'}}}))
            # User speaks across patched MODEL_AUDIO_STALL_SECONDS=0.35; watchdog must not kill session.
            await asyncio.sleep(0.20)
            await ws.send(json.dumps({'serverContent': {'inputTranscription': {'text': 'Sí, desbloquéala', 'finished': True}}}))
            await asyncio.sleep(0.25)
            await ws.send(json.dumps({'toolCall': {'functionCalls': [{'id': 'c1', 'name': 'unblock_ip', 'args': {'ip': ip}}]}}))
            while True:
                msg = json.loads(await ws.recv())
                if 'toolResponse' in msg:
                    self.assertTrue(msg['toolResponse']['functionResponses'][0]['response']['verified'])
                    break

        async def mic():
            while True:
                yield b'\x00\x00' * 320
                await asyncio.sleep(0.02)

        async def sink(*args):
            pass

        with patch('gemini_live_client.MODEL_AUDIO_STALL_SECONDS', 0.35):
            async with websockets.serve(fake, '127.0.0.1', 0) as server:
                url = 'ws://127.0.0.1:' + str(server.sockets[0].getsockname()[1])
                client = GeminiLiveVoiceClient(api_key='test', connect=lambda _, **kw: websockets.connect(url, **kw))
                await asyncio.wait_for(
                    client.start_voice_session({'attacker_ip': ip, 'operator_extension': '1004'}, mic(), sink, tools, sink),
                    5,
                )
        fw.unblock_ip.assert_called_once_with(ip)
