'''
Table definitions
'''

import struct
import uuid

############################
# Conversion helper funcions
############################



class GenericTable:
    '''
    Generic Table class
    '''
    data = {}

    def binary_to_string(self, binary_data, byte_offset, length):
        '''
        Converts binary data chunk to string.
        '''
        return binary_data[byte_offset:byte_offset + length].decode('utf-8')

    def binary_to_int(self, binary_data, byte_offset, length=4):
        '''
        Converts binary data chunk to integer.
        '''
        return struct.unpack(
            'i', binary_data[byte_offset:byte_offset + length]
        )[0]

    def binary_to_byte(self, binary_data, byte_offset, length=1):
        '''
        Converts binary data chunk to byte.
        '''
        return struct.unpack(
            'B', binary_data[byte_offset:byte_offset + length]
        )[0]

    def binary_to_hex(self, binary_data, byte_offset, length):
        '''
        Converts binary data chunk to hex.
        '''
        hex_data = binary_data[byte_offset:byte_offset + length].hex()
        return ' '.join(a+b for a,b in zip(hex_data[::2], hex_data[1::2]))

    def binary_to_guid(self, binary_data, byte_offset, length):
        '''
        Converts binary data to guid.
        '''
        return uuid.UUID(
            bytes=binary_data[byte_offset:byte_offset + length]
        ).bytes_le.hex()

    def check_header_signature(self, signature):
        '''
        Checks header signature and raises an exception if its wrong
        '''
        if self.data['header_signature'] != signature:
            raise Exception(
                f'Wrong header signature: {self.data["header_signature"]}'
            )

    def read_table(self, filename):
        '''
        Reads data tabe file and returns as a binary data.
        '''
        with open(filename, "rb") as file:
            binary_data = file.read()
        return binary_data

class Bert(GenericTable):
    '''
    Bert (Boot Error Record Table) class
    '''
    def __init__(self, filename):
        data = self.read_table(filename)
        self.data = {
            'header_signature': self.binary_to_string(data, 0, 4),
            'lenght': self.binary_to_int(data, 4),
            'revision': self.binary_to_byte(data, 8),
            'checksum': self.binary_to_byte(data, 9),
            'oem_id': self.binary_to_string(data, 10, 6),
            'oem_revision': self.binary_to_int(data, 24),
            'creator_id': self.binary_to_string(data, 28, 4),
            'creator_revision': self.binary_to_int(data, 32),
            'boot_error_region_length': self.binary_to_int(data, 36),
            'boot_error_region': self.binary_to_hex(data, 40, 8),
            'hex': self.binary_to_hex(data, 0, 48)
        }
