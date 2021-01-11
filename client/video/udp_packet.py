"""
    Hadar Shahar
    UdpPacket.
"""
import struct
from constants import NETWORK_BYTES_PER_NUM


class UdpPacket:
    """ Definition of the class UdpPacket. """

    # The numbers of numbers in each header
    NUMS_IN_HEADER = 4
    HEADER_SIZE = NUMS_IN_HEADER * NETWORK_BYTES_PER_NUM  # in bytes

    # '>' for big-endian (network byte order is always big-endian)
    # 'I' for unsigned int which takes 4 bytes
    BYTES_FORMAT = f'>{NUMS_IN_HEADER}I'

    # The max data size in each packet.
    # Must be less than constants.UDP_SOCKET_BUFFER_SIZE
    MAX_DATA_SIZE = 2048

    def __init__(self, frame_index: int, packet_index: int,
                 num_packets: int, data: bytes):
        """ Constructor. """
        self.frame_index = frame_index    # The current frame index
        self.packet_index = packet_index  # The current packet index
        self.num_packets = num_packets    # The total number of packets
        self.data_size = len(data)        # The data size in bytes

        self.data = data  # The data buffer

        header_format = (self.frame_index, self.packet_index,
                         self.num_packets, self.data_size)
        self.header = struct.pack(UdpPacket.BYTES_FORMAT, *header_format)

    @staticmethod
    def decode(packet: bytes):
        """
        Decodes a given packet and returns a UdpPacket.
        """
        raw_header = packet[:UdpPacket.HEADER_SIZE]
        frame_index, packet_index, num_packets, data_size = \
            struct.unpack(UdpPacket.BYTES_FORMAT, raw_header)

        data = packet[UdpPacket.HEADER_SIZE: UdpPacket.HEADER_SIZE + data_size]
        p = UdpPacket(frame_index, packet_index, num_packets, data)
        return p

    def encode(self):
        """ Encodes the packet. """
        return self.header + self.data
