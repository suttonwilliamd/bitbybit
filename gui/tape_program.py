"""Deterministic eight-bit teaching programs for the relay cabinet's demo tape.

No gameplay, clocks, randomness or saved state. Every punched row is the result
of a completed demo job, never a player-currency or production measurement.
"""
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import math

PROGRAMS = ('COUNT', 'ADD', 'MULT', 'XOR', 'SHIFT', 'FIB', 'ASCII', 'PARITY')
JOB_PHASE = 6.0
TEXT = 'HELLO RELAY WORLD! '
MESSAGE_ODDS = 65536
_SECRET_MESSAGE = 'STAY CURIOUS.'
FIBONACCI = (0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233)


@dataclass(frozen=True)
class TapeJob:
    name: str
    tag: str
    inputs: tuple[int, ...]
    result: int
    prompt: str
    answer: str


def _message_starts(index, seed):
    # One of 65,536 equally likely hashes. No per-frame random draws or timers.
    key = f'{seed}:{index}'.encode('ascii')
    return hashlib.blake2s(key, digest_size=2).digest() == b'\xb1\x7b'


def _message_offset(index, seed):
    for offset in range(min(index, len(_SECRET_MESSAGE) - 1) + 1):
        if _message_starts(index - offset, seed):
            return offset
    return None


@lru_cache(maxsize=128)
def tape_job(index, seed=0):
    """Vary operands on each pass, rather than repeating four decorative bytes."""
    if index < 0:
        raise ValueError('Demo job index must be nonnegative')
    message = _message_offset(index, seed)
    if message is not None:
        character = _SECRET_MESSAGE[message]
        byte = ord(character)
        return TapeJob('ASCII', '?', (byte,), byte, repr(character), f'{character!r}={byte}')
    name = PROGRAMS[index % len(PROGRAMS)]
    turn = index // len(PROGRAMS)
    if name == 'COUNT':
        a = turn & 255
        inputs, result, prompt, tag = (a,), (a + 1) & 255, f'{a}+1', 'C'
    elif name == 'ADD':
        a, b = (13 + turn * 17) % 160, (7 + turn * 11) % 96
        inputs, result, prompt, tag = (a, b), a + b, f'{a}+{b}', '+'
    elif name == 'MULT':
        a, b = 3 + turn * 3 % 13, 2 + turn * 5 % 14
        inputs, result, prompt, tag = (a, b), a * b, f'{a}x{b}', '*'
    elif name == 'XOR':
        a, b = (0x55 ^ (turn * 29)) & 255, (0x3C + turn * 13) & 255
        inputs, result, prompt, tag = (a, b), a ^ b, f'{a}^{b}', '^'
    elif name == 'SHIFT':
        a = (0x81 + turn * 13) & 255
        inputs, result, prompt, tag = (a,), (a << 1) & 255, f'{a}<<1', '<'
    elif name == 'FIB':
        i = (turn + 1) % 12
        a, b = FIBONACCI[i:i + 2]
        inputs, result, prompt, tag = (a, b), a + b, f'{a}+{b}', 'F'
    elif name == 'ASCII':
        character = TEXT[turn % len(TEXT)]
        inputs, result, prompt, tag = (ord(character),), ord(character), repr(character), 'T'
    else:
        a = (0x55 + turn * 37) & 255
        inputs, result, prompt, tag = (a,), a.bit_count() & 1, f'{a}: {a.bit_count()} ONES', 'P'
    answer = f'{inputs[0]}: {"ODD" if result else "EVEN"}' if name == 'PARITY' else f'{prompt}={result}'
    return TapeJob(name, tag, inputs, result, prompt, answer)


@dataclass(frozen=True)
class TapeFrame:
    index: int
    job: TapeJob
    stage: str
    scan_phase: float | None
    position: float  # Tape rows, not pixels.

    @property
    def result_ready(self):
        return self.stage in ('PUNCH', 'HOLD')

    @property
    def last_printable(self):
        return self.index if self.result_ready else self.index - 1


def tape_frame(phase, seed=0):
    """READ -> one complete relay RUN -> PUNCH/feed -> readable result HOLD.

    Only PUNCH advances the paper. Position is continuous at job boundaries;
    rows don't rearrange or reveal results before the computation has finished.
    """
    phase = max(0.0, phase)
    index = math.floor(phase / JOB_PHASE)
    local = phase - index * JOB_PHASE
    if local < .5:
        stage, scan = 'READ', None
    elif local < 4.5:
        stage, scan = 'RUN', local - .5
    elif local < 5:
        stage, scan = 'PUNCH', None
    else:
        stage, scan = 'HOLD', None
    feed = max(0.0, min(1.0, (local - 4.5) / .5))
    feed = feed * feed * (3 - 2 * feed)
    return TapeFrame(index, tape_job(index, seed), stage, scan, index + feed)
