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
import glob
import struct
import uuid
import sys
from tables import Bert, Hest, GenericErrorStatusBlock
import predefined_values

def print_table_data(table):
    '''
    Prints table data.
    '''
    print('===========')
    print(f'''{table.data['header_signature']} Table:''')
    print('===========')
    print(f'Filename: {table.filename}')
    for key, data in table.data.items():
        if key == 'hex':
            print_hex_data(data)
        else:
            print(key.replace('_', ' ').capitalize() + ':', data)
    print()

def print_data_entry(name, entry):
    '''
    Prints data entry.
    '''
    print('-----------')
    print(f'{name}:')
    print('-----------')
    if entry.filename:
        print(f'Filename: {entry.filename}')
    for key, data in entry.data.items():
        if key == 'hex':
            print_hex_data(data)
        else:
            print(key.replace('_', ' ').capitalize() + ':', data)
    print()

def print_hex_data(data):
    '''
    Prints hex data fromatted in columns and rows.
    '''
    print('HEX data:')
    hexdata = [data[i:i+48] for i in range(0, len(data), 48)]
    for number, line in enumerate(hexdata):
        print(str(number * 16) + '.:\t' + line)

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


def main(args):
    '''
    Main function.
    '''
    # Exit if location is not a valid dir
    if not os.path.isdir(args.acpi_location):
        print('ERROR: Not a valid directory')
        parser.print_help()
        sys.exit(1)
    # Find all BERT files
    bert_files = glob.glob(args.acpi_location + '/BERT*')
    if len(bert_files) > 0:
        # Iterate through BERT Table files
        for bert_file in bert_files:
            bert_table = Bert(bert_file)
            print_table_data(bert_table)
    else:
        print(f'ERROR: No BERT file in {args.acpi_location}')
        parser.print_help()
        sys.exit(1)
    # Read HEST file
    hest_table = Hest(args.acpi_location + '/HEST')
    print_table_data(hest_table)
    # Read BERT data file
    generic_error_status_block = GenericErrorStatusBlock(
        os.path.join(args.acpi_location, 'data', 'BERT')
    )
    print_data_entry('Generic Error Status Block', generic_error_status_block)
    #filename = args.acpi_location + "/data/BERT"
    #bert_table_data_binary = read_bert_table(filename)
    #if bert_table_data_binary:
    #    print_bert_table_data(
    #        get_bert_table_data(bert_table_data_binary),
    #        filename
    #    )

if __name__ == "__main__":
    # Parsing args
    parser = argparse.ArgumentParser(
        description='Decodes ACPI BERT tables and BERT Data Table'
    )
    parser.add_argument('acpi_location', metavar='directory', type=str,
                    help='acpi tables location')
    main(parser.parse_args())
