import nfc
from nfc.tag.tt3 import Type3TagCommandError

class nfc_module:
    def __init__(self) -> None:
        self.clf = nfc.ContactlessFrontend('usb')
        self.discover_tag = None

    def connection(self):
        print("Please touch student ID card")
        self.clf.connect(rdwr={'on-connect': self.connected})

    def connected(self, tag):
        self.discover_tag = tag

    def student_info(self, tag):
        service_code = 0x100B

        sc = nfc.tag.tt3.ServiceCode(service_code >> 6 ,service_code & 0x3f)
        student_number_bc = nfc.tag.tt3.BlockCode(0,service=0)
        student_name1_bc = nfc.tag.tt3.BlockCode(4,service=0)
        student_name2_bc = nfc.tag.tt3.BlockCode(5,service=0)

        try:
            student_number = tag.read_without_encryption([sc],[student_number_bc])
            student_name = tag.read_without_encryption([sc],[student_name1_bc, student_name2_bc])
            data = {"student_number": student_number[0:9].decode(),
                    "student_name": student_name.partition(b"\x00")[0].decode()}
        except (Type3TagCommandError, AttributeError):
            print("This tag is not a student ID card")
        else:
            return data
