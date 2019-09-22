# https://uefi.org/sites/default/files/resources/UEFI%20Spec%202_6.pdf
# N.2.2 Section Descriptor

section_types = {
    "9876ccad47b44bdbb65e16f193c4f3db": {
        "name": "Processor Generic",
        "error_record_reference": {}
    },
    "dc3ea0b0a1444797b95b53fa242b6e1d": {
        "name": "Processor Specific - IA32/X64",
        "error_record_reference": {}
    },
    "e429faf13cb711d4bca70080c73c8881": {
        "name": "Processor Specific - IPF",
        "error_record_reference": {}
    },
    "e19e3d16bc1111e49caac2051d5d46b0": {
        "name": "Processor Specific - ARM",
        "error_record_reference": {}
    },
    "a5bc11146f644edeb8633e83ed7c83b1": {
        "name": "Platform Memory",
        "error_record_reference": {}
    },
    "d995e954bbc1430fad91b44dcb3c6f35": {
        "name": "PCIe",
        "error_record_reference": {}
    },
    "81212a9609ed499694718d729c8e69ed": {
        "name": "Firmware Error Record Reference",
        "error_record_reference": {
            "firmware_error_record_type": (0, 1, "byte"),
            "reserved": (1, 7, "hex"),
            "record_identifier": (8, 8, "hex")
        }
    },
    "c57539633b844095bf78eddad3f9c9dd": {
        "name": "PCI/PCI-X Bus",
        "error_record_reference": {}
    },
    "eb5e4685ca664769b6a226068b001326": {
        "name": "DMAr Generic",
        "error_record_reference": {}
    },
    "71761d3732b245cda7d0b0fedd93e8cf": {
        "name": "Intel® VT for Directed I/O specific DMAr section",
        "error_record_reference": {}
    },
    "036f84e17f37428ca79e575fdfaa84ec": {
        "name": "IOMMU specific DMAr section",
        "error_record_reference": {}
    }
}

error_severity = [
    "Recoverable (also called non-fatal uncorrected)",
    "Fatal",
    "Corrected",
    "Informational"
]

