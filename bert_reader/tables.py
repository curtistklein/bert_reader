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
        self.filename = filename
        data = self.read_table(self.filename)
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

class Hest(GenericTable):
    '''
    Hest (Hardware Error Source Table) class
    '''
    def __init__(self, filename):
        self.filename = filename
        data = self.read_table(self.filename)
        self.data = {
            'header_signature': self.binary_to_string(data, 0, 4),
            'lenght': self.binary_to_int(data, 4),
            'revision': self.binary_to_byte(data, 8),
            'checksum': self.binary_to_byte(data, 9),
            'oem_id': self.binary_to_string(data, 10, 6),
            'oem_revision': self.binary_to_int(data, 24),
            'creator_id': self.binary_to_string(data, 28, 4),
            'creator_revision': self.binary_to_int(data, 32),
            'error_source_count': self.binary_to_int(data, 36),
            'error_source_structure': data[40:],
            'hex': self.binary_to_hex(data, 0, len(data))
        }

class GenericHardwareErrorSourceStructure(GenericTable):
    '''
    Generic Hardware Error Source Structure class

    Section 18.3.2.7 in ACPI Specification.
    '''
    def __init__(self, filename):
        self.filename = filename
        data = self.read_table(self.filename)
        self.data = {
            'type': self.binary_to_int(data, 0, length=2),
            'source_id': self.binary_to_int(data, 2, length=2),
            'related_source_id': self.binary_to_int(data, 4),
            'flags': self.binary_to_byte(data, 6),
            'enabled': self.binary_to_byte(data, 7),
            'number_of_records_to_preallocate': self.binary_to_int(data, 8),
            'max_sections_per_record': self.binary_to_int(data, 12),
            'max_raw_data_length': self.binary_to_int(data, 16),
            'error_status_address': self.binary_to_hex(data, 20, 12),
            'notification_structure': data[28:60],
            'error_status_block_length': self.binary_to_hex(data, 60, 4),
            'hex': self.binary_to_hex(data, 0, len(data))
        }

class GenericErrorStatusBlock(GenericTable):
    '''
    Generic Error Status Block

    Section 18.3.2.7.1 in ACPI Specification.
    '''
    def __init__(self, filename):
        self.filename = filename
        data = self.read_table(self.filename)
        self.data = {
            'block_status': data[0:4].hex(),
            'raw_data_offset': self.binary_to_hex(data, 4, 4),
            'raw_data_length': self.binary_to_int(data, 8, 4),
            'data_length': self.binary_to_int(data, 12, 4),
            'error_severity': self.get_severity(data, 16, 4),
            'hex': self.binary_to_hex(data, 0, len(data))
        }

    def get_severity(self, data, start, length=4):
        '''
        Get error severity from data.
        '''
        severity = self.binary_to_int(data, start, length)
        severity_text = [
            'Recoverable',
            'Fatal',
            'Correctable',
            'None']
        if severity < len(severity_text):
            return f'{severity_text[severity]}({severity})'
        return f'unknown({severity})'
