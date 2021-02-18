"""
    Hadar Shahar
    UdpPacketsHandler.
"""
import math
from client.video.udp_packet import UdpPacket


class UdpPacketsHandler:
    """ Definition of the class UdpPacketsHandler. """

    RECEIVED_PACKETS_THRESHOLD = 0.9  # in percent

    def __init__(self):
        """ Constructor. """
        self.current_frame_index = None
        self.packets_data = []
        self.remaining_packets = None

    def process_packet(self, p: UdpPacket):
        """
        Processes a given packet.
        If all the packets were collected, returns the full frame.
        Otherwise, returns None.
        """
        full_frame = b''

        # if it's the first packet, or just a more recent packet,
        # drop all the packets collected so far, or fill the missing packets
        is_first_packet = self.current_frame_index is None
        if is_first_packet or p.frame_index > self.current_frame_index:

            if not is_first_packet and self.remaining_packets != 0:
                full_frame = self.handle_missing_packets()

            self.current_frame_index = p.frame_index
            self.packets_data = [b''] * p.num_packets
            self.remaining_packets = p.num_packets

        # if the packet is too old, drop it
        if p.frame_index < self.current_frame_index:
            print('Frame is too old, dropping it.')
            return None

        # place the packet at the right place
        self.packets_data[p.packet_index] = p.data
        self.remaining_packets -= 1

        if self.remaining_packets == 0:
            full_frame = b''.join(self.packets_data)

        return full_frame if full_frame else None

    def handle_missing_packets(self) -> bytes:
        """

        :return:
        """
        num_packets = len(self.packets_data)
        received = num_packets - self.packets_data.count(b'')
        received_percent = received / num_packets
        print_percent = f'{received}/{num_packets} ({received_percent:.2f})'

        if received_percent > self.RECEIVED_PACKETS_THRESHOLD:
            self.fill_missing_packets()
            print(f'Received {print_percent} packets, filling the rest.')
            return b''.join(self.packets_data)

        print(f'A more recent packet received, dropping '
              f'{print_percent} packets.')
        return b''

    def fill_missing_packets(self):
        for i in range(1, len(self.packets_data)):
            if self.packets_data[i] == b'':
                self.packets_data[i] = self.packets_data[i-1]

    @staticmethod
    def create_packets(frame_index: int, data: bytes) -> list:
        """
        Returns a list of UdpPacket ready to be sent.
        """
        chunk_size = UdpPacket.MAX_DATA_SIZE - UdpPacket.HEADER_SIZE
        num_packets = math.ceil(len(data) / chunk_size)
        packets = []

        # # build a memory view to a get 0 copy
        # dataview = memoryview(data)

        for i in range(num_packets):
            chunk = data[i * chunk_size: (i + 1) * chunk_size]
            packets.append(UdpPacket(frame_index, i, num_packets, chunk))
        return packets
