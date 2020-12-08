import io
import time

data = b'\x9e\xf5\x15\xb9\xa2\xa3\xa3\x7f?\xd0q\xbb\xd2\xe3 +\x12\x93\x1c[K\x0eFI\xfc)\xa8\xc6g\xf2^\x0c\x1e\xd5!\x8c\xba\xf9f0\xa7\x1d\xb9\xcf\x14\x82\xe1!>[G\x82{\x91JN\x9c\x15\x9e\x97\xfcL\xec\x9a#h"\x81\xc8\xf3\xb8e\xc3s\xdb\x14\xcd\xb1\x84$!-\xdb\x9c\xd3\xf3\x91\xe6;\x02=1L\xfbAV\xdc\xad\x8fJ\xcf\xda\x7f\xcb\xbb-{+\xfea\x18E\x90\xdb\xc2\x0c\x9b\xd7 \xf5\xc1\x14\xe9\x11\x9b;\xfa\xe7\x8a\x9dL*\x86]\xc3q5RI\xc9\x19\xfc\xe9\xa9\xd1\xc0\xc1A\xb7g\xe7\xb1O\x9aN\xd7"\x9d\xa5+\x801\x902qQ\xa7\xc8\x9b$\xf9\xb3\xc0=\xeak\x86\x02<\x8c\n\xac\xee\xe8\xa4\x84\x18\x1d+5\x8c\x8c\xa4\xd5\xed\xd9\xbf\xebS7\rw\x12fA\x1e|\xac\x11U$\xf3\xdaa3\x02rz\n\x9ei\xdeP:d\xf6\xa5\x8d\x0f\x92VQ\x8cz\x8a\xea\xa4\xa5\x88z-\xba\xed\xa9.\xc8\xafp\xd1\xcc\x826\x90\x8cw\xa8c\x11\x8c\xa8\x19\x03\x1d\xb9\xa7\xca#S\x80\xe1\xba\x8c\x8a\x15R&\x00\x03\xc9\xcfZ\xbc4c:\x8eSiy\xdbS*\x91\x9b\xb7b\xab\xa4n\xfb\\6\x0fm\xb5]\xe3.\xc5X\x923\xf2\x8fZ\xbdsp\xcaHU\x1b\xbbsU3\x17\x9b\xe7\x13\xf3\x7f\x16\x05gU\xd3\x8c\xf9S\xe6\xfc-\xfed*s\x9a\xb3\x7f"\xbf\x94\xa02,[[\xb6\xe1U\xaeP\xa4x<\x1f\xe1\x00V\x83\xb1\x99\x0c\x8b\xf7\x87\xdd\x00f\xa9\x8f2\xeab\x93!\x03\xd4V\xd4\xa5I\xcdZMs\x18\xd5R\x8e\x91*LO\x90\\\xfc\xcd\xcfA\x92*\xb4\xb3L\x88Y\xe2*W\x83\x95\xc6*\xed\xca\xc7\x03\xf9G\r\xf8T\x0c\xa6F\xdb\xbbi\x1c\xf09\xa7?g\xcde&\xbah\xff\x00;\x98Y\xa4\xd3Dk\x1b\xb7\xcaq\x83T\xae\xe5E\x05%@\xcc\xac0v\x8e\x0e;V\x81\x95#|c\x8e\x9c\xd5)\n\xbc\xac\xeb\xb4\xfa\x93Z\xdf\x0f\xcc\xe3\tY\xfa\x85E(\xa4\xd9\x04.\xf3e&@\xc9\xd4\x82\xf8\xf6\xe9UdUI\x04\xb10\xda\xa7\x90{\x8f\xe9S\xbd\xb4\x8f\xbc,\xe0n\xe9\x8e\xd5\x13\x19\x11\xcc\x93\xaa\xf2z\x1e\xd5\xd3Nj\xabQ\x9c\xad\xead\xa4\xd3\xd1X\xafx-\x1a2\\\x16\xdf\xd3p\x04)\xff\x00>\xb5@\xd8\x84v1|\xaa>\xe8\xc9\xe2\xaf\xb2,\xec\xd2\x12\x10\x1f\xba\x00\xe9U\x99\x94\xab$\xd9VC\x83]\tA\xc7\xf7\x96\xb7Kn)EK[\x9e\xcb\x99D\xa1 \x07`<-]\x9a\xd8\xb4J\xea\xa7w9\x02\x8f2=\xfek\x90Fz\x93U\xf5\rQ,"\x17\x97w\t\x1c`\xe1\x9c\xf4\x1c\xfa\x0eI\xe4\x0c\x00O5\xd3\xfb\xe8^\\\xcd\xfa\xed\xf29\xe4\xe3\x08\\\xb9\x01\x10\xb0Y\x061\xd7"\x9c\xe4\xc5\x9f\xd0\x81\xd2\xbc\xef\xc6\xff\x00\xb5\'\xc0?\x01*\xc9\xe3\x9f\x8a\xfa^\x9aHS\x1a\xddoS `H#r\x8e=\xfa~c<6\xa7\xff\x00\x054\xfd\x89\xf4\x15\x91o\xfe7i\xd7N\x83\x98\xf4\xe53\xb0\x1c\x8c\x95\x00\x11\xcf\xd7\xd6\xb5\x86W\x98\xe2c\xcd\x1c<\xe5\xd9\xa5/\xf25\x85E4\xad\xf9\x1f@\xda[\xcb\xb3\xccYF\xc7$\xb0#\xa9\xcf\xff\x00Z\x9c\xbb\x87\xcc\xd1\xf3\xbb\x04\x83\xc1\xff\x00<W\xc7~+\xff\x00\x82\xd0~\xcb\xde\x1e\x8a\xe6\xdfG\xb1\xd7\xb5\x19"r\x90\xec\xd3\xcch\xe78\'\x97\xca\xf7\xeb\xd0\xf5\xf7\xf3\xdb\xef\xf8.w\x85fv:7\xc2\xe9\xd1G\xfa\xb9A\x13\x13\xf8n$\x7f\x9fz\xd2\x87\x0c\xe7\xb8\x898\xbc3\x8f\xf8\xb4\x7f\x89\xaa\xa5\x88\xfeF~\x87\xac\xe9\x18UG\x04\x9e\xa0v\xa5HX9c\x93\xda\xbf6.\xff\x00\xe0\xbb\xda\xe5\xb9W\xb1\xf8\r\x05\xcc}\xe5\x9af\x86O\xc1A\xc7\xaf\xe9V\xf4?\xf8/\xcf\x88\xc4H\xde(\xfd\x9a \xbbP~ae\xab\x18\xe4\xeb\xee\xb8\xfd{\xfb\n\xe9|%\xc42\xa4\xe4\xa8^\xdd9\xa2\xbf6\x8d\xa1K\x13\x08\xfc:\x9f\xa4\xf0\xe1\x18\x00\x07\xb9&\x9eT\xb9%\xb1\xd7\xad|\ri'
END_RANGE = 100000

begin = time.time()
buffer = io.BytesIO()
for i in range(0, END_RANGE):
    buffer.write(data)
end = time.time()
seconds = end - begin
print("BytesIO:", seconds)

begin = time.time()
buffer = bytearray()
for i in range(0, END_RANGE):
    buffer += data
end = time.time()
seconds = end - begin
print("bytearray +=", seconds)

begin = time.time()
buffer = bytearray()
for i in range(0, END_RANGE):
    buffer.extend(data)
end = time.time()
seconds = end - begin
print("bytearray.extend:", seconds)


