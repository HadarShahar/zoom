"""
    Hadar Shahar
    Network protocol utils.
"""
import socket
import struct
from network.constants import NETWORK_BYTES_FORMAT, NETWORK_BYTES_PER_NUM


def create_packet(data: bytes) -> bytes:
    """
    Creates a packet of data prefixed with its length
    (padded according to NETWORK_BYTES_FORMAT).
    """
    padded_length = struct.pack(NETWORK_BYTES_FORMAT, len(data))
    return padded_length + data


def recv_packet(sock: socket.socket) -> bytearray:
    """
    Receives a packet of data from a given socket,
    each packet is prefixed with its length.
    """
    raw_size = recvall(sock, NETWORK_BYTES_PER_NUM)
    # struct.unpack always returns a tuple
    data_size = struct.unpack(NETWORK_BYTES_FORMAT, raw_size)[0]
    data = recvall(sock, int(data_size))
    return data


def send_packet(sock: socket.socket, data: bytes):
    """
    Sends a packet of data to a given socket.
    """
    sock.sendall(create_packet(data))


def recvall(sock: socket.socket, n: int) -> bytearray:
    """
    Receives n bytes from a given socket
    (the method socket.recv(n) receives maximum n bytes).
    """
    buffer = bytearray()
    while len(buffer) < n:
        data = sock.recv(n - len(buffer))
        buffer.extend(data)
    return buffer

# def send_data(sock: socket.socket, data: bytes):
#     packet = create_packet(data)
#     send_packet(sock, packet)


# def valid_info_msg(msg):
#     """
#     checks if a given message between the InfoClient and InfoServer is valid,
#     meaning consists of a known name (from VALID_MESSAGES)
#     and a parameter (can be any type).
#     """
#     return len(msg) == 2 and msg[0] in VALID_MESSAGES


# def create_packet(data: bytes) -> bytes:
#     """
#     creates a packet of data prefixed
#     with its length (filled with zeroes)
#     """
#     msg_len = str(len(data)).zfill(MSG_LEN)
#     return msg_len.encode() + data
#
#
# def recv_packet(sock: socket.socket) -> bytearray:
#     """
#     receives a packet of data from a given socket,
#     each packet is prefixed with its length
#     """
#     raw_size = recvall(sock, MSG_LEN)
#     data_size = raw_size.decode()
#     data = recvall(sock, int(data_size))
#     return data