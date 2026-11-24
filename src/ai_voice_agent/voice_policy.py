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


AFFIRMATIVE_REPLY = re.compile(
    r"[\s¿?¡!.,]*(?:(?:bueno|ya|claro|ok|okey|obvio|perfecto|porfa|por\s+favor)[\s,]+)*"
    r"(?:si|claro|dale|adelante|confirmo|autorizo|hazlo|procede)"
    r"(?:[\s,]+(?:por\s+favor|porfa|claro|nomas|obvio|ya|si|dale|gracias|hazlo|perfecto))*"
    r"[\s.!]*$"
)

UNBLOCK_EXPLICIT = re.compile(
    r"\b("
    r"desbloque(?:a(?:r?(?:me|nos|le)?(?:la|lo|s)?)?|e(?:s|n)?(?:me|nos|le)?(?:la|lo|s)?)"
    r"|libera(?:r?(?:me|nos|le)?(?:la|lo|s)?)?|libere(?:s|n)?(?:me|nos|le)?(?:la|lo|s)?"
    r"|(?:re)?habilita(?:r?(?:me|nos|le)?(?:la|lo|s)?)?|(?:re)?habilite(?:s|n)?(?:me|nos|le)?(?:la|lo|s)?"
    r"|desbane(?:a(?:r?(?:me|nos|le)?(?:la|lo)?)?|e(?:s)?(?:me|nos|le)?(?:la|lo)?)"
    r"|(?:quita|saca|levanta|retira)(?:r?(?:me|nos|le)?)?\s+(?:el\s+|ese\s+|este\s+|del\s+|de\s+la\s+)?bloqueo"
    r"|(?:quita|saca|retira)(?:r?(?:me|nos|le)?)?\s+(?:la\s+|esa\s+|mi\s+|esta\s+)?ip"
    r")\b"
)

NEGATION_GUARD = re.compile(r"\b(no|nunca|jamas|espera|cancela\w*|manten\w*|dejala|dejalo)\b")
QUESTION_GUARD = re.compile(
    r"\b(como\s+(?:se|puedo|hacen|funciona|es|fue|esta)|"
    r"quien\s+(?:fue|ataco|puede|desbloquea|bloquea|es)|"
    r"cuando\s+(?:se|fue|lo|la|puedo|bloqueo|desbloquea)|"
    r"se\s+puede|que\s+pasa|que\s+pasaria)\b"
)


class VoiceActionPolicy:
    def __init__(self, incident, authorized_extensions):
        self.incident = incident
        self.authorized = str(incident.get("operator_extension", "")) in authorized_extensions
        self.focus_ip = incident.get("attacker_ip") or None
        self.pending_unblock = None
        self.offered_ips = set()
        self.input_text = ""
        self.output_text = ""
        self.updated_at = 0
        self.last_turn_input = ""
        self.last_turn_at = 0
        self.lock = threading.Lock()

    def observe_input(self, text):
        with self.lock:
            self.input_text = (self.input_text + text)[-4000:]
            self.updated_at = time.monotonic()
            # Drop any stashed prior order as soon as a refusal arrives.
            if NEGATION_GUARD.search(normalize(self.input_text)):
                self.last_turn_input = ""
                self.last_turn_at = 0

    def observe_output(self, text):
        with self.lock:
            self.output_text = (self.output_text + text)[-4000:]

    def record_offered_ips(self, ips):
        with self.lock:
            self.offered_ips.update(ips)

    def _offer_target(self, output):
        if not (re.search(r"\b(quieres|deseas|autorizas|confirmas|prefieres|gusta(?:ria)?|procedo|te\s+la\s+desbloqueo|la\s+desbloqueo)\b", output)
                and re.search(r"\b(desbloque\w*|liber\w*|habilit\w*|quit\w+\s+el\s+bloqueo)\b", output)):
            return None
        if self.focus_ip:
            return self.focus_ip
        named = [ip for ip in mentioned_ips(output) if ip in self.offered_ips]
        return named[0] if len(named) == 1 else None

    def finish_turn(self):
        with self.lock:
            output = normalize(self.output_text)
            # A bare yes is meaningful only after the agent actually asked.
            target = self._offer_target(output)
            self.pending_unblock = target
            if target:
                self.focus_ip = target
            current_norm = normalize(self.input_text).strip()
            if current_norm and not NEGATION_GUARD.search(current_norm) and not QUESTION_GUARD.search(current_norm):
                self.last_turn_input = self.input_text
                self.last_turn_at = self.updated_at or time.monotonic()
            else:
                self.last_turn_input = ""
                self.last_turn_at = 0
            self.output_text = ""
            self.input_text = ""
            self.updated_at = 0

    def interrupt_output(self):
        """Discard an unfinished question without losing fresh operator input."""
        with self.lock:
            self.output_text = ""
            self.pending_unblock = None

    def _effective_input(self):
        now = time.monotonic()
        if self.input_text.strip() and now - self.updated_at <= 30:
            return self.input_text, now - self.updated_at
        if self.last_turn_input.strip() and now - self.last_turn_at <= 12:
            return self.last_turn_input, now - self.last_turn_at
        return "", None

    def confirmed_unblock_target(self):
        """A contextual yes confirms the question already asked, without another LLM decision."""
        with self.lock:
            raw_text, age = self._effective_input()
            if not self.authorized or not self.pending_unblock or not raw_text or age is None or age > 30:
                return None
            text = normalize(raw_text)
            if NEGATION_GUARD.search(text) or QUESTION_GUARD.search(text):
                return None
            if AFFIRMATIVE_REPLY.fullmatch(text):
                return self.pending_unblock
            if UNBLOCK_EXPLICIT.search(text) and (self.pending_unblock == self.focus_ip or self.pending_unblock in mentioned_ips(text)):
                return self.pending_unblock
            return None

    def authorize(self, action, ip):
        with self.lock:
            if not self.authorized:
                return False, "El anexo autenticado no está autorizado para acciones."
            raw_text, age = self._effective_input()
            text = normalize(raw_text)
            if not text or age is None or age > 30:
                return False, "No hay una orden de voz reciente verificable; pide confirmación explícita."
            if NEGATION_GUARD.search(text):
                return False, "La orden contiene una negativa o solicita mantener el bloqueo."
            if QUESTION_GUARD.search(text):
                return False, "Es una consulta o solicitud ambigua; pide una orden explícita."
            # A direct call must identify its target before using a pronoun.
            if ip != self.focus_ip and ip not in mentioned_ips(text):
                return False, "La IP no corresponde al incidente ni fue indicada por el operador."
            if action == "unblock_ip":
                explicit = bool(UNBLOCK_EXPLICIT.search(text))
                yes = bool(AFFIRMATIVE_REPLY.fullmatch(text))
                allowed = explicit or (yes and self.pending_unblock == ip)
            else:
                allowed = bool(re.search(r"\b(bloquea(?:r|la|lo|me|nos|rla|rlo)?|bloquee(?:s|la|lo|me)?)\b", text))
            if not allowed:
                return False, "No se identificó autorización explícita para esta acción; pregunta al operador."
            self.input_text = ""  # Consume once, including failed remote operations.
            self.last_turn_input = ""
            self.last_turn_at = 0
            self.pending_unblock = None
            self.focus_ip = ip
            return True, "Autorización de voz recibida."
