"""
UAF-81.83: Sliding ACK Bitfield and Packet Acknowledgement Manager.
"""

from __future__ import annotations

from typing import Tuple
from .sequence import sequence_diff, sequence_greater_than


class AckManager:
    """
    Manages 32-bit sliding ACK bitfields for packet confirmation across unreliable networks.
    Tracks latest received sequence and previous 32 sequence bits.
    """

    def __init__(self, max_sequence: int = 65536):
        self.max_sequence = max_sequence
        self.latest_ack: int = 0
        self.ack_bits: int = 0
        self._initialized: bool = False

    def register_received_sequence(self, seq: int) -> None:
        """Update sliding ACK bitmask upon receiving incoming packet sequence."""
        if not self._initialized:
            self.latest_ack = seq
            self.ack_bits = 0
            self._initialized = True
            return

        if sequence_greater_than(seq, self.latest_ack, self.max_sequence):
            shift = sequence_diff(seq, self.latest_ack, self.max_sequence)
            if shift >= 32:
                self.ack_bits = 0
            else:
                self.ack_bits = ((self.ack_bits << shift) | (1 << (shift - 1))) & 0xFFFFFFFF
            self.latest_ack = seq
        else:
            diff = sequence_diff(self.latest_ack, seq, self.max_sequence)
            if 1 <= diff <= 32:
                self.ack_bits |= (1 << (diff - 1))

    def is_acknowledged(self, seq: int, ack: int, ack_bits: int) -> bool:
        """Check if seq is acknowledged given (ack, ack_bits) from remote header."""
        if seq == ack:
            return True
        diff = sequence_diff(ack, seq, self.max_sequence)
        if 1 <= diff <= 32:
            return bool(ack_bits & (1 << (diff - 1)))
        return False

    def get_ack_info(self) -> Tuple[int, int]:
        """Return (latest_ack, ack_bits) for outgoing packet headers."""
        return (self.latest_ack, self.ack_bits)
