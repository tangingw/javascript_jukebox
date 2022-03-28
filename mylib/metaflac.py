import io
import re
import struct

from numpy import block

# https://xiph.org/flac/format.html#metadata_block
# All numbers used in a FLAC bitstream are integers; there are no floating-point representations. 
# All numbers are big-endian coded. All numbers are unsigned unless otherwise specified.
class NotFlacHeaderError(Exception):

    def __init__(self, block):

        self.block = block
        Exception.__init__()
    
    def __str__(self):
        return f"{self.block} is not valid flac header"


class MetaFlac:
    def __init__(self, filename):
        self._block_streaminfo = None
        self._block_application = None
        self._block_seektable = None
        self._block_vorbis_comment = None
        self._block_cuesheet = None
        self._block_picture = None
        
        self._attribute_pointer = {
            0: "_block_streaminfo",
            2: "_block_application",
            3: "_block_seektable",
            4: "_block_vorbis_comment",
            5: "_block_cuesheet",
            6: "_block_picture"
        }
        
        with io.open(filename, 'rb') as file:
            self.__parse_marker(file.read(4))
            
            last = 0
            while not last:
                last, block_type, size = self.__parse_block_header(file.read(4))
                if block_type in self._attribute_pointer:
                    setattr(self, self._attribute_pointer[block_type], file.read(size))
                    
                elif block_type == 1:
                    file.read(size)

                elif block_type > 6 and block_type < 127:
                    raise NotImplementedError('reserved')
                    
                else:
                    raise NotImplementedError('invalid, to avoid confusion with a frame sync code')
    
    
    def __parse_marker(self, block):
        # "fLaC", the FLAC stream marker in ASCII
        if block != b'fLaC':
            raise NotFlacHeaderError(block)

    def __parse_block_header(self, block):
        unpacked = struct.unpack('>I', block)[0]
        return (
            unpacked >> 31, # Last-metadata-block flag: '1' if this block is the last metadata block before the audio blocks, '0' otherwise. last
            unpacked >> 24 & 0x7f, #block_type
            unpacked & 0x00ffffff, # Length (in bytes) of metadata to follow., size
        )
 
    def get_streaminfo(self):
        if self._block_streaminfo:
            block = self._block_streaminfo

            streaminfo = {
                "minimum_blocksize": struct.unpack('>H', block[0:2])[0], # 16bits The minimum block size (in samples) used in the stream.
                "maximum_blocksize": struct.unpack('>H', block[2:4])[0], # 16bits The maximum block size (in samples) used in the stream.
                "minimum_framesize": struct.unpack('>I', b'\x00' + block[4:7])[0], # 24bits The minimum frame size (in bytes) used in the stream.
                "maximum_framesize": struct.unpack('>I', b'\x00' + block[7:10])[0] # 24bits The maximum frame size (in bytes) used in the stream.
            }

            unpacked = struct.unpack('>Q', block[10:18])[0]
            streaminfo['total_samples_in_stream'] = unpacked & 0xfffffffff # (36bits) Total samples in stream.
            
            unpacked = unpacked >> 36
            streaminfo['bits_per_sample'] = (unpacked & 0x1f) + 1 # (5bits) Bits per sample.
            
            unpacked = unpacked >> 5
            streaminfo.update(
                {
                    "number_of_channels": (unpacked & 0x7) + 1, # (3bits) Number of channels.
                    "sample_rate": unpacked >> 3, # (20bits) Sample rate in Hz.
                    "md5": block[18:34] # (128bits) MD5 signature of the unencoded audio data.
                }
            )
            return streaminfo
    
        return self._block_streaminfo

    def get_application(self):
        # The ID request should be 8 hexadecimal digits        
        if self._block_application:
            return {
                "registered_id": hex(struct.unpack('>I', self._block_application[0:4])[0]), # (32bits) Registered application ID.
                "data": self._block_application[4:]
            }
    
        return self._block_application

    def get_seektable(self):
        if self._block_seektable:
            return [
                (
                    struct.unpack('>Q', self._block_seektable[i:i+8])[0], # (64bits) Sample number of first sample in the target frame, or 0xFFFFFFFFFFFFFFFF for a placeholder point.
                    struct.unpack('>Q', self._block_seektable[i+8:i+16])[0], # (64bits) Offset (in bytes) from the first byte of the first frame header to the first byte of the target frame's header.
                    struct.unpack('>H', self._block_seektable[i+16:i+18])[0] # (16bits) Number of samples in the target frame.
                ) for i in range(0, len(self._block_seektable), 18)
            ]

        return self._block_seektable

    def get_picture(self):
        if self._block_picture:
            block = self._block_picture
            length = struct.unpack('>I', block[4:8])[0] # (32bits) The length of the MIME type string in bytes.
            picture = {
                'mime': block[8:8+length], # (n*8bites) The MIME type string.
                'picture_type': struct.unpack('>I', block[0:4])[0] # (32bits) The picture type according to the ID3v2 APIC frame.
            }

            block = block[8+length:]
            length = struct.unpack('>I', block[0:4])[0] # (32bits) The length of the description string in bytes.
            picture['description'] = block[4:4+length].decode('utf-8') # (n*8bites) The description of the picture, in UTF-8.
            
            block = block[4+length:]
            picture.update(
                {
                    'width': struct.unpack('>I', block[0:4])[0],  # (32bits) The width of the picture in pixels.
                    'height': struct.unpack('>I', block[4:8])[0], # (32bits) The height of the picture in pixels.
                    'depth': struct.unpack('>I', block[8:12])[0], # (32bits) The color depth of the picture in bits-per-pixel.
                    'nOfcolors': struct.unpack('>I', block[12:16])[0] # (32bits) For indexed-color pictures (e.g. GIF), the number of colors used, or 0 for non-indexed pictures.
                }
            )

            length = struct.unpack('>I', block[16:20])[0] # (32bits) The length of the picture data in bytes.
            picture['data'] = block[20:20+length] # (n*8bites) The binary picture data.
            return picture

        return self._block_picture
    
    def get_vorbis_comment(self):
        # https://www.xiph.org/vorbis/doc/v-comment.html
        # note that the 32-bit field lengths are little-endian coded according to the vorbis spec, as opposed to the usual big-endian coding of fixed-length integers in the rest of FLAC.
        if self._block_vorbis_comment:
            vorbis_comment = dict()
            block = self._block_vorbis_comment
            vendor_length = struct.unpack('I', block[0:4])[0] # (32bits) vendor_length

            block = block[4+vendor_length:]
            user_comment_list_length = struct.unpack('I', block[0:4])[0] # (32bits) user_comment_list_length
            block = block[4:]

            regex_filter_string = r"[A-Fa-f0-9]{8}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{12}"

            for _ in range(user_comment_list_length):
                length = struct.unpack('I', block[0:4])[0]
                user_comment = block[4:4+length].decode('utf-8')

                block = block[4+length:]
                if '=' in user_comment:
                    key, value = user_comment.split('=')

                    if not re.search(regex_filter_string, key):
                        vorbis_comment[key.lower()] = value
            return vorbis_comment

        return self._block_vorbis_comment

