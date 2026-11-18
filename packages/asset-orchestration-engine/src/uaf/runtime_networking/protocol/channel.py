"""
UAF-81.83: Reliable Ordered and Unreliable Sequenced Network Channels.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple
from ..models.definition import ChannelType, Packet, PacketHeader
from .ack import AckManager
from .sequence import sequence_diff, sequence_greater_than


class ReliableOrderedChannel:
    """
    Guarantees ordered, acknowledged, retransmitted delivery without duplicates.
    Maintains a transmission retry queue and incoming reassembly buffer.
    """

    def __init__(self, rto_ticks: int = 5, max_sequence: int = 65536):
        self.rto_ticks = rto_ticks
        self.max_sequence = max_sequence

        # Transmission state
        self.next_send_sequence: int = 1
        self.unacked_packets: Dict[int, Tuple[Packet, int]] = {}  # seq -> (packet, sent_tick)

        # Reception state
        self.expected_receive_sequence: int = 1
        self.receive_buffer: Dict[int, Packet] = {}  # seq -> packet
        self.ack_manager = AckManager(max_sequence)

    def prepare_send(
        self,
        session_id: str,
        connection_id: str,
        server_tick: int,
        payload: bytes,
        current_tick: int,
    ) -> Packet:
        """Create and queue an outgoing reliable packet."""
        seq = self.next_send_sequence
        self.next_send_sequence = (self.next_send_sequence + 1) % self.max_sequence

        ack, ack_bits = self.ack_manager.get_ack_info()
        header = PacketHeader(
            protocol_version=1,
            session_id=session_id,
            connection_id=connection_id,
            channel=ChannelType.RELIABLE_ORDERED,
            sequence=seq,
            ack=ack,
            ack_bits=ack_bits,
            server_tick=server_tick,
            payload_size=len(payload),
        )
        pkt = Packet(header=header, payload=payload)
        self.unacked_packets[seq] = (pkt, current_tick)
        return pkt

    def process_incoming_acks(self, ack: int, ack_bits: int) -> List[int]:
        """Acknowledge sent packets matching the remote header's ACK info."""
        acked_seqs: List[int] = []
        for seq in list(self.unacked_packets.keys()):
            if self.ack_manager.is_acknowledged(seq, ack, ack_bits):
                acked_seqs.append(seq)
                del self.unacked_packets[seq]
        return acked_seqs

    def collect_retransmissions(self, current_tick: int) -> List[Packet]:
        """Collect unacknowledged packets that exceeded retransmission timeout (RTO)."""
        retransmits: List[Packet] = []
        for seq in sorted(self.unacked_packets.keys()):
            pkt, sent_tick = self.unacked_packets[seq]
            if current_tick - sent_tick >= self.rto_ticks:
                retransmits.append(pkt)
                self.unacked_packets[seq] = (pkt, current_tick)
        return retransmits

    def receive_packet(self, packet: Packet) -> List[Packet]:
        """
        Process incoming reliable packet.
        Registers ACK, buffers out-of-order packets, and delivers strictly contiguous ordered packets.
        """
        seq = packet.header.sequence
        self.ack_manager.register_received_sequence(seq)
        self.process_incoming_acks(packet.header.ack, packet.header.ack_bits)

        # Check if already delivered (duplicate)
        if not sequence_greater_than(seq, self.expected_receive_sequence, self.max_sequence) and seq != self.expected_receive_sequence:
            return []  # Drop duplicate or old packet

        # Buffer future packet
        if seq != self.expected_receive_sequence:
            self.receive_buffer[seq] = packet
            return []

        # Deliver contiguous sequence
        delivered: List[Packet] = [packet]
        self.expected_receive_sequence = (self.expected_receive_sequence + 1) % self.max_sequence

        while self.expected_receive_sequence in self.receive_buffer:
            next_pkt = self.receive_buffer.pop(self.expected_receive_sequence)
            delivered.append(next_pkt)
            self.expected_receive_sequence = (self.expected_receive_sequence + 1) % self.max_sequence

        return delivered


class UnreliableSequencedChannel:
    """
    Loss-tolerant, sequenced delivery channel.
    Accepts newest packets and silently drops old or duplicate packets.
    """

    def __init__(self, max_sequence: int = 65536):
        self.max_sequence = max_sequence
        self.next_send_sequence: int = 1
        self.highest_received_sequence: int = 0
        self._first_received: bool = False
        self.ack_manager = AckManager(max_sequence)

    def prepare_send(
        self,
        session_id: str,
        connection_id: str,
        server_tick: int,
        payload: bytes,
    ) -> Packet:
        """Create outgoing unreliable packet."""
        seq = self.next_send_sequence
        self.next_send_sequence = (self.next_send_sequence + 1) % self.max_sequence

        ack, ack_bits = self.ack_manager.get_ack_info()
        header = PacketHeader(
            protocol_version=1,
            session_id=session_id,
            connection_id=connection_id,
            channel=ChannelType.UNRELIABLE_SEQUENCED,
            sequence=seq,
            ack=ack,
            ack_bits=ack_bits,
            server_tick=server_tick,
            payload_size=len(payload),
        )
        return Packet(header=header, payload=payload)

    def receive_packet(self, packet: Packet) -> Optional[Packet]:
        """
        Process incoming unreliable packet.
        Delivers if packet is newer than highest received; drops if out-of-order or duplicate.
        """
        seq = packet.header.sequence
        self.ack_manager.register_received_sequence(seq)

        if not self._first_received:
            self._first_received = True
            self.highest_received_sequence = seq
            return packet

        if sequence_greater_than(seq, self.highest_received_sequence, self.max_sequence):
            self.highest_received_sequence = seq
            return packet

        return None  # Dropped old or duplicate
