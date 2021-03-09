"""
    Hadar Shahar
    Network constants file.
"""

# the parameter for socket.listen()
NUMBER_OF_WAITING_CONNECTIONS = 100

# MSG_LEN = 4  # 8
CHUNK_SIZE = 1024
EOF = b'-1'
EXIT_SIGN = b'EXIT'

# '>' for big-endian (network byte order is always big-endian)
# 'I' for unsigned int which takes 4 bytes
NETWORK_BYTES_FORMAT = '>I'
# The number of bytes each number takes (according to NETWORK_BYTES_FORMAT)
NETWORK_BYTES_PER_NUM = 4

# "For best match with hardware and network realities, the value of bufsize
# should be a relatively small power of 2, for example, 4096."
UDP_SOCKET_BUFFER_SIZE = 4096

# when a udp client connects to the meeting, it sends this message
# to the udp server to inform it that it has connected
UDP_NEW_CLIENT_MSG = b'HELLO'
