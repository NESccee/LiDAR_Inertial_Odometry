#!/usr/bin/env python3
"""Send DJI T100's work_tgt_mode=SAMPLING command.

The T100 accepts the Livox command envelope on UDP/60000, but its data and
data ports are not the standard Mid-360 ports.  This helper intentionally
only sends the known-compatible command and does not attempt to parse replies.
"""

import argparse
import socket
import struct
import time
import zlib


def crc16_ccitt(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc


def sampling_packet(sequence: int) -> bytes:
    # One key/value: work_tgt_mode (0x001a) = SAMPLING (0x01).
    data = struct.pack("<HHHB", 1, 0x001A, 1, 0x01)
    length = 24 + len(data)
    header = struct.pack(
        "<BBHIHBB6s", 0xAA, 0, length, sequence, 0x0100, 0, 0, b"\0" * 6
    )
    crc16 = crc16_ccitt(header)
    crc32 = zlib.crc32(data) & 0xFFFFFFFF
    return header + struct.pack("<HI", crc16, crc32) + data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lidar-ip", default="192.168.1.10")
    parser.add_argument("--host-ip", default="192.168.1.20")
    parser.add_argument("--port", type=int, default=60000)
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--interval", type=float, default=0.2)
    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Selecting the source address matters when the host has more than one
        # interface.  It also makes the intended T100 network explicit.
        try:
            sock.bind((args.host_ip, 0))
        except OSError as exc:
            print(f"[T100] warning: cannot bind {args.host_ip}: {exc}; using default route")
        for sequence in range(1, max(1, args.count) + 1):
            packet = sampling_packet(sequence)
            sock.sendto(packet, (args.lidar_ip, args.port))
            print(f"[T100] sent SAMPLING ({len(packet)} bytes) to {args.lidar_ip}:{args.port}")
            if sequence != args.count:
                time.sleep(max(0.0, args.interval))
    except OSError as exc:
        # The driver can still attach if the lidar is already sampling.  Keep
        # launch usable and report the failure clearly instead of aborting ROS.
        print(f"[T100] warning: SAMPLING command failed: {exc}")
    finally:
        sock.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
