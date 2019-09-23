#!/usr/bin/env python3
# usage: bert_reader.py [-h] directory
#
# Decodes ACPI BERT tables and BERT Data Table
#
# positional arguments:
#   directory   acpi tables location
#
# optional arguments:
#   -h, --help  show this help message and exit
#

import argparse
import os
import struct
import uuid
import predefined_values

############################
# Conversion helper funcions
############################


def binary_to_string(binary_data, byte_offset, length):
    """Converts binary data chunk to string"""
    return binary_data[byte_offset:byte_offset + length].decode("utf-8")

def binary_to_int(binary_data, byte_offset):
    """Converts binary data chunk to integer"""
    return struct.unpack("i", binary_data[byte_offset:byte_offset + 4])[0]

def binary_to_byte(binary_data, byte_offset):
    """Converts binary data chunk to byte"""
    return struct.unpack("B", binary_data[byte_offset:byte_offset + 1])[0]

def binary_to_hex(binary_data, byte_offset, length):
    """Converts binary data chunk to hex"""
    hex_data = binary_data[byte_offset:byte_offset + length].hex()
    return ' '.join(a+b for a,b in zip(hex_data[::2], hex_data[1::2]))

def binary_to_guid(binary_data, byte_offset, length):
    """Converts binary data to guid"""
    return uuid.UUID(bytes=binary_data[byte_offset:byte_offset + length]).bytes_le.hex()

# https://uefi.org/sites/default/files/resources/ACPI_6_3_final_Jan30.pdf
# Table 18-381 Boot Error Record Table (BERT) Table
def get_bert_table(bert_table_binary):
    """Returns a BERT Table dict from raw binary data"""
    bert_table = {}
    bert_table["header_signature"] = binary_to_string(bert_table_binary, 0, 4)
    bert_table["lenght"] = binary_to_int(bert_table_binary, 4)
    bert_table["revision"] = binary_to_byte(bert_table_binary, 8)
    bert_table["checksum"] = binary_to_byte(bert_table_binary, 9)
    bert_table["oem_id"] = binary_to_string(bert_table_binary, 10, 6)
    bert_table["oem_revision"] = binary_to_int(bert_table_binary, 24)
    bert_table["creator_id"] = binary_to_string(bert_table_binary, 28, 4)
    bert_table["creator_revision"] = binary_to_int(bert_table_binary, 32)
    bert_table["boot_error_region_length"] = binary_to_int(bert_table_binary, 36)
    bert_table["boot_error_region"] = binary_to_hex(bert_table_binary, 40, 8)
    bert_table["hex"] = binary_to_hex(bert_table_binary, 0, 48)
    return bert_table

# https://uefi.org/sites/default/files/resources/UEFI_Spec_2_8_final.pdf
# Table 18-381 Generic Error Status Block
# Table 18-382 Generic Error Data Entry
def get_bert_table_data(bert_table_data_binary):
    """Returns a BERT Table Data dict from raw binary data"""
    bert_table_data = {}
    bert_table_data["block_status"] = bert_table_data_binary[0:4].hex()
    bert_table_data["raw_data_offset"] = bert_table_data_binary[4:8].hex()
    bert_table_data["raw_data_lenght"] = bert_table_data_binary[8:12].hex()
    bert_table_data["data_lenght"] = binary_to_int(bert_table_data_binary, 12)
    bert_table_data["error_severity"] = binary_to_int(bert_table_data_binary, 16)
    bert_table_data["generic_error_data_entries"] = binary_to_int(bert_table_data_binary, 16)
    bert_table_data["generic_error_data_entry"] = []
    # cut header from binary data
    bert_table_data_binary = bert_table_data_binary[20:]
    for i in range(0,bert_table_data["generic_error_data_entries"]):
        data_entry = {}
        data_entry["section_type"] = binary_to_guid(bert_table_data_binary, 0, 16)
        data_entry["error_severity"] = binary_to_int(bert_table_data_binary, 16)
        data_entry["revision"] = bert_table_data_binary[20:22].hex()
        data_entry["validation_bits"] = bert_table_data_binary[22:23].hex()
        data_entry["flags"] = bert_table_data_binary[23:24].hex()
        data_entry["error_data_lenght"] = binary_to_int(bert_table_data_binary, 24)
        data_entry["fru_id"] = bert_table_data_binary[28:44].hex()
        data_entry["fru_text"] = binary_to_string(bert_table_data_binary, 44, 20)
        data_entry["timestamp"] = bert_table_data_binary[64:72].hex()
        data_entry["generic_error_data"] = binary_to_hex(bert_table_data_binary, 72, data_entry["error_data_lenght"])
        bert_table_data["generic_error_data_entry"].append(data_entry)
        # shorten binary data with this generic error data
        bert_table_data_binary = bert_table_data_binary[72 + data_entry["error_data_lenght"]:]
    return bert_table_data

def read_bert_table(file):
    """Reads BERT Table and BERT Table Data binary files and returns as a binary object"""
    try:
        with open(file, "rb") as f:
            bert_table_binary = f.read()
            f.close()
    except OSError as err:
        print("OS error: {0}".format(err))
        return None

    return bert_table_binary

def print_bert_table(bert_table, filename):
    """Prints the BERT Table human readable"""
    print("===========")
    print("BERT Table:")
    print("===========")
    print("Filename:", filename)
    for key, data in bert_table.items():
        if key == "hex":
            print_hex_data(data)
        else:
            print(key.replace("_", " ").capitalize() + ":", data)
    print()

def print_bert_table_data(bert_table_data, filename):
    """Prints the BERT Table Data human readable"""
    print("===========")
    print("BERT Table Data:")
    print("===========")
    print("Filename:", filename)
    for key, data in bert_table_data.items():
        if key == "generic_error_data_entry":
            print_error_data_entries(data)
        elif key == "error_severity":
            severity = predefined_values.error_severity[int(data)]
            print(key.replace("_", " ").capitalize() + ":", data, "(" + severity + ")")
        else:
            print(key.replace("_", " ").capitalize() + ":", data)
    print()

def print_error_data_entries(error_data_entries):
    """Prints the BERT Table Data Entry human readable
    TODO: implement all the available sections from UEFI specification
    """
    for error_data_entry in range(len(error_data_entries)):
        print()
        print(str(error_data_entry + 1) + ". error data entry")
        print("-------------------")
        for key, data in error_data_entries[error_data_entry].items():
            if key == "generic_error_data":
                print_hex_data(data)
            elif key == "section_type":
                try:
                    severity = predefined_values.section_types[data]["name"]
                except:
                    severity = "Unknown"
                print(key.replace("_", " ").capitalize() + ":", data, "(" + severity + ")")

            elif key == "error_severity":
                severity = predefined_values.error_severity[int(data)]
                print(key.replace("_", " ").capitalize() + ":", data, "(" + severity + ")")
            else:
                print(key.replace("_", " ").capitalize() + ":", data)

def print_hex_data(data):
    """Print hex data fromatted in columns and rows"""
    print("HEX data:")
    hexdata = [data[i:i+48] for i in range(0, len(data), 48)]
    for line in range(len(hexdata)):
        print(str(line * 16) + ".:\t" + hexdata[line])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Decodes ACPI BERT tables and BERT Data Table')
    parser.add_argument('acpi_location', metavar='directory', type=str,
                    help='acpi tables location')
    args = parser.parse_args()
    if not os.path.isdir(args.acpi_location):
        print("ERROR: Not a valid directory")
        parser.print_help()
        exit(1)
    for i in range(1,3):
        filename = args.acpi_location + "/BERT" + str(i)
        bert_table_binary = read_bert_table(filename)
        if bert_table_binary: print_bert_table(get_bert_table(bert_table_binary), filename)

    filename = args.acpi_location + "/data/BERT"
    bert_table_data_binary = read_bert_table(filename)
    if bert_table_data_binary: print_bert_table_data(
            get_bert_table_data(bert_table_data_binary), filename
    )

