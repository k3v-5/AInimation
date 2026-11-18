"""
UAF-81.83: Deterministic Packet Serialization, Header Packing, and Checksum Validation.
"""

from __future__ import annotations

import json
import struct
import zlib
from typing import Tuple

from ..models.definition import (
    ChannelType,
    Packet,
    PacketHeader,
    PacketValidationError,
)

# Header format:
# protocol_version: H (uint16)
# channel: B (uint8)
# sequence: H (uint16)
# ack: H (uint16)
# ack_bits: I (uint32)
# server_tick: I (uint32)
# payload_size: I (uint32)
# checksum: I (uint32)
HEADER_FORMAT = "!H B H H I I I I"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)


class PacketSerializer:
    """Encodes and decodes network packets with integrity validation and checksumming."""

    @staticmethod
    def encode(packet: Packet) -> bytes:
        """Serialize Packet into binary bytes."""
        payload_bytes = packet.payload
        payload_len = len(payload_bytes)

        chan_id = 0 if packet.header.channel == ChannelType.RELIABLE_ORDERED else 1

        # Checksum of payload + metadata
        crc = zlib.crc32(payload_bytes) & 0xFFFFFFFF

        header_bytes = struct.pack(
            HEADER_FORMAT,
            packet.header.protocol_version,
            chan_id,
            packet.header.sequence & 0xFFFF,
            packet.header.ack & 0xFFFF,
            packet.header.ack_bits & 0xFFFFFFFF,
            packet.header.server_tick & 0xFFFFFFFF,
            payload_len,
            crc,
        )

        # Prepend session_id and connection_id as prefixed strings
        sess_bytes = packet.header.session_id.encode("utf-8")
        conn_bytes = packet.header.connection_id.encode("utf-8")

        prefix = struct.pack("!B B", len(sess_bytes), len(conn_bytes))
        return prefix + sess_bytes + conn_bytes + header_bytes + payload_bytes

    @staticmethod
    def decode(data: bytes, expected_protocol: int = 1) -> Packet:
        """Parse raw bytes into Packet, raising PacketValidationError if corrupted."""
        if len(data) < 2:
            raise PacketValidationError("Data truncated: missing ID prefix.")

        sess_len, conn_len = struct.unpack("!B B", data[:2])
        offset = 2

        if len(data) < offset + sess_len + conn_len + HEADER_SIZE:
            raise PacketValidationError("Data truncated: packet smaller than header size.")

        session_id = data[offset : offset + sess_len].decode("utf-8", errors="replace")
        offset += sess_len
        connection_id = data[offset : offset + conn_len].decode("utf-8", errors="replace")
        offset += conn_len

        header_bytes = data[offset : offset + HEADER_SIZE]
        offset += HEADER_SIZE

        proto, chan_id, seq, ack, ack_bits, srv_tick, payload_len, crc = struct.unpack(
            HEADER_FORMAT, header_bytes
        )

        if proto != expected_protocol:
            raise PacketValidationError(f"Protocol version mismatch: expected {expected_protocol}, got {proto}")

        payload_bytes = data[offset : offset + payload_len]
        if len(payload_bytes) != payload_len:
            raise PacketValidationError(f"Payload size mismatch: expected {payload_len}, got {len(payload_bytes)}")

        # Validate CRC
        expected_crc = zlib.crc32(payload_bytes) & 0xFFFFFFFF
        if crc != expected_crc:
            raise PacketValidationError(f"Packet checksum mismatch: header {crc} vs calculated {expected_crc}")

        chan = ChannelType.RELIABLE_ORDERED if chan_id == 0 else ChannelType.UNRELIABLE_SEQUENCED

        header = PacketHeader(
            protocol_version=proto,
            session_id=session_id,
            connection_id=connection_id,
            channel=chan,
            sequence=seq,
            ack=ack,
            ack_bits=ack_bits,
            server_tick=srv_tick,
            payload_size=payload_len,
        )

        return Packet(header=header, payload=payload_bytes)
