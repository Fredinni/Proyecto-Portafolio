"""Keep live listening and flush speech ends without streaming endless silence."""
import audioop
from collections import deque


class AudioActivityGate:
    def __init__(self, threshold=140, silence_ms=800, prefix_ms=160):
        self.threshold = threshold
        self.silence_samples = silence_ms * 16
        self.prefix_samples = prefix_ms * 16
        self.prefix = deque()
        self.prefix_size = 0
        self.active = False
        self.quiet_samples = 0

    def feed(self, pcm):
        if not pcm or len(pcm) % 2:
            return [], False
        count = len(pcm) // 2
        voiced = audioop.rms(pcm, 2) >= self.threshold
        if not self.active:
            self.prefix.append(pcm)
            self.prefix_size += count
            while self.prefix and self.prefix_size > self.prefix_samples + count:
                self.prefix_size -= len(self.prefix.popleft()) // 2
            if not voiced:
                return [], False
            self.active = True
            self.quiet_samples = 0
            chunks = list(self.prefix)
            self.prefix.clear()
            self.prefix_size = 0
            return chunks, False
        self.quiet_samples = 0 if voiced else self.quiet_samples + count
        if self.quiet_samples >= self.silence_samples:
            self.active = False
            self.quiet_samples = 0
            return [pcm], True
        return [pcm], False
