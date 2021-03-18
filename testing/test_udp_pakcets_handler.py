import cv2
import random
from client.video.udp_packet import UdpPacket
from client.video.udp_packets_handler import UdpPacketsHandler
from client.video.video_encoder import VideoEncoder


def received_new_packet(packets_handler: UdpPacketsHandler, packet: UdpPacket):
    data = packets_handler.process_packet(packet)
    if data is not None:
        print('Got a frame!')
        frame = VideoEncoder.decode_frame_buffer(data)
        cv2.imshow('frame', frame)
        cv2.waitKey()


def main():
    frame = cv2.imread('space.jpg')
    encoded_frame = VideoEncoder.encode_frame(frame)
    # print(len(frame.tobytes()) / len(encoded_frame))

    packets = UdpPacketsHandler.create_packets(0, encoded_frame)
    print('num_of_packets:', len(packets))
    random.shuffle(packets)

    removed_packet = packets.pop(50)
    print(removed_packet.__dict__)

    packets_handler = UdpPacketsHandler()
    for p in packets:
        received_new_packet(packets_handler, p)

    # simulate a packet from the next frame
    received_new_packet(packets_handler, UdpPacket(1, 0, 100, b''))


if __name__ == '__main__':
    main()
