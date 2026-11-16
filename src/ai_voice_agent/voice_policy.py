"""Authorize mutations from the current operator utterance, never model prose."""

import ipaddress
import re
import threading
import time
import unicodedata


def normalize(text):
    return "".join(c for c in unicodedata.normalize("NFD", text.lower())
                   if unicodedata.category(c) != "Mn")


def mentioned_ips(text):
    result = set()
    for token in re.findall(r"[0-9a-fA-F:.]+", text):
        try:
            result.add(str(ipaddress.ip_address(token.rstrip("."))))
        except ValueError:
            pass
    return result


class VoiceActionPolicy:
    def __init__(self, incident, authorized_extensions):
        self.incident = incident
        self.authorized = str(incident.get("operator_extension", "")) in authorized_extensions
        self.focus_ip = incident.get("attacker_ip") or None
        self.pending_unblock = None
        self.input_text = ""
        self.output_text = ""
        self.updated_at = 0
        self.lock = threading.Lock()

    def observe_input(self, text):
        with self.lock:
            self.input_text = (self.input_text + text)[-4000:]
            self.updated_at = time.monotonic()

    def observe_output(self, text):
        with self.lock:
            self.output_text = (self.output_text + text)[-4000:]

    def finish_turn(self):
        with self.lock:
            output = normalize(self.output_text)
            # A bare yes is meaningful only after the agent actually asked.
            self.pending_unblock = self.focus_ip if (
                re.search(r"\b(quieres|deseas|autorizas|confirmas)\b", output)
                and re.search(r"\b(desbloque\w*|liber\w*|habilit\w*)\b", output)
            ) else None
            self.output_text = ""
            self.input_text = ""
            self.updated_at = 0

    def authorize(self, action, ip):
        with self.lock:
            if not self.authorized:
                return False, "El anexo autenticado no está autorizado para acciones."
            text = normalize(self.input_text)
            if not text or time.monotonic() - self.updated_at > 30:
                return False, "No hay una orden de voz reciente verificable; pide confirmación explícita."
            if re.search(r"\b(no|nunca|jamas|espera|cancela\w*|manten\w*|dejala|dejalo)\b", text):
                return False, "La orden contiene una negativa o solicita mantener el bloqueo."
            if re.search(r"\b(como|quien|cuando|se puede|que pasa|que pasaria)\b", text):
                return False, "Es una consulta o solicitud ambigua; pide una orden explícita."
            # A direct call must identify its target before using a pronoun.
            if ip != self.focus_ip and ip not in mentioned_ips(text):
                return False, "La IP no corresponde al incidente ni fue indicada por el operador."
            if action == "unblock_ip":
                explicit = bool(re.search(r"\b(desbloquea(?:r|la|lo|me|nos|s|rla|rlo)?|desbloquee(?:s|la|lo|me)?|libera(?:r|la|lo|me|nos|rla|rlo)?|habilita(?:r|la|lo|me|rla|rlo)?|quita(?:le|me)? el bloqueo)\b", text))
                yes = bool(re.fullmatch(r"[\s¿?¡!.,]*(si|dale|adelante|confirmo|autorizo)([\s,]+por favor)?[\s.!]*", text))
                allowed = explicit or (yes and self.pending_unblock == ip)
            else:
                allowed = bool(re.search(r"\b(bloquea(?:r|la|lo|me|nos|rla|rlo)?|bloquee(?:s|la|lo|me)?)\b", text))
            if not allowed:
                return False, "No se identificó autorización explícita para esta acción; pregunta al operador."
            self.input_text = ""  # Consume once, including failed remote operations.
            self.pending_unblock = None
            self.focus_ip = ip
            return True, "Autorización de voz recibida."
