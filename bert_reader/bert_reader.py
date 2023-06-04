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
import sys
from tables import Bert
import predefined_values


# https://uefi.org/sites/default/files/resources/ACPI_6_3_final_Jan30.pdf
# Table 18-381 Boot Error Record Table (BERT) Table
def get_bert_table(bert_table_binary):
    """Returns a BERT Table dict from raw binary data"""
    return bert_table

# https://uefi.org/sites/default/files/resources/UEFI_Spec_2_8_final.pdf
# Table 18-381 Generic Error Status Block
# Table 18-382 Generic Error Data Entry
def get_bert_table_data(bert_table_data_binary):
    """
    Returns a BERT Table Data dict from raw binary data.
    """
    bert_table_data = {
        "block_status": bert_table_data_binary[0:4].hex(),
        "raw_data_offset": bert_table_data_binary[4:8].hex(),
        "raw_data_lenght": bert_table_data_binary[8:12].hex(),
        "data_lenght": binary_to_int(bert_table_data_binary, 12),
        "error_severity": binary_to_int(bert_table_data_binary, 16),
        "generic_error_data_entries": binary_to_int(
            bert_table_data_binary, 16),
        "generic_error_data_entry": []
    }
    # cut header from binary data
    bert_table_data_binary = bert_table_data_binary[20:]
    for i in range(0, bert_table_data["generic_error_data_entries"]):
        data_entry = {
            "section_type": binary_to_guid(bert_table_data_binary, 0, 16),
            "error_severity": binary_to_int(bert_table_data_binary, 16),
            "revision": bert_table_data_binary[20:22].hex(),
            "validation_bits": bert_table_data_binary[22:23].hex(),
            "flags": bert_table_data_binary[23:24].hex(),
            "error_data_length": binary_to_int(bert_table_data_binary, 24),
            "fru_id": bert_table_data_binary[28:44].hex(),
            "fru_text": binary_to_string(bert_table_data_binary, 44, 20),
            "timestamp": bert_table_data_binary[64:72].hex(),
        }
        data_entry["generic_error_data"] = binary_to_hex(
            bert_table_data_binary, 72, data_entry["error_data_length"]
        )
        bert_table_data["generic_error_data_entry"].append(data_entry)
        bert_table_data["decoded_data_entry"] = get_bert_table_data_entry(
            data_entry["section_type"],
            bert_table_data_binary[72:data_entry["error_data_length"]]
        )
        # shorten binary data with this generic error data
        bert_table_data_binary = bert_table_data_binary[72 + data_entry["error_data_length"]:]
    return bert_table_data

def get_bert_table_data_entry(section_type, data_entry):
    """
    Decodes section type and generic error data entry and returns it as a dict.
    """
    decoded_data_entry = {}
    #try:
    section_type = predefined_values.section_types[section_type]
    for key, value in section_type["error_record_reference"].items():
        decoded_data_entry[key] = globals()[value[2]](
            data_entry, value[0], value[1]
        )

    #print(decoded_data_entry)

    #except:
    #    section_type = "Unknown"
    return decoded_data_entry

def read_bert_table(file):
    """
    Reads BERT Table and BERT Table Data binary files and returns as a
    binary object.
    """
    try:
        with open(file, "rb") as bert_file:
            bert_table_binary = bert_file.read()
            bert_file.close()
    except OSError as err:
        print(f'OS error: {err}')
        return None
    return bert_table_binary

def print_bert_table(bert_table, filename):
    """
    Prints the BERT Table human readable.
    """
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
    """
    Prints the BERT Table Data human readable.
    """
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
        elif key == "decoded_data_entry":
            print_decoded_data_entries(data)
        else:
            print(key)
            print(key.replace("_", " ").capitalize() + ":", data)
    print()

def print_decoded_data_entries(decoded_data_entries):
    for key, value in decoded_data_entries.items():
        print(key.replace("_", " ").capitalize() + ":", value)

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
                    section_type = predefined_values.section_types[data]["name"]
                except:
                    section_type = "Unknown"
                print(key.replace("_", " ").capitalize() + ":", data, "(" + section_type + ")")
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

def main(args):
    """
    Main function.
    """
    # Exit if location is not a valid dir
    if not os.path.isdir(args.acpi_location):
        print("ERROR: Not a valid directory")
        parser.print_help()
        sys.exit(1)
    # Iterate through BERT Table files
    for i in range(1,3):
        filename = args.acpi_location + "/BERT" + str(i)
        bert_table_binary = read_bert_table(filename)
        if bert_table_binary:
            bert_table = Bert(bert_table_binary)
            print_bert_table(bert_table.data, filename)
    # Read BERT data file
    filename = args.acpi_location + "/data/BERT"
    bert_table_data_binary = read_bert_table(filename)
    if bert_table_data_binary:
        print_bert_table_data(
            get_bert_table_data(bert_table_data_binary),
            filename
        )

if __name__ == "__main__":
    # Parsing args
    parser = argparse.ArgumentParser(
        description='Decodes ACPI BERT tables and BERT Data Table'
    )
    parser.add_argument('acpi_location', metavar='directory', type=str,
                    help='acpi tables location')
    main(parser.parse_args())
