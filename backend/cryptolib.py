import getpass
import hashlib

class cryptolib:
    def __init__(self, salt) -> None:
        self.salt = salt

    def enter_password(self):
        password = "pass"
        repassword = "repass"
        flag = False
        while password != repassword:
            password = getpass.getpass(prompt="Please Enter Password: ")
            if password is "":
                print("At leaset one character")
                continue
            repassword = getpass.getpass(prompt="Retype: ")
            flag = True
            if flag and password != repassword:
                print("Incorrect retype password")

        cryptopass = self.__stretching(password)
        return cryptopass

    def __stretching(self, passphrase):
        bytes_password = bytes(passphrase, 'utf-8')
        stretching_password = hashlib.sha256(self.salt + bytes_password).hexdigest()
        for _ in range(1000):
            stretching_password = hashlib.sha256(bytes(stretching_password, 'utf-8')).hexdigest()
        return stretching_password

    def correct_check(self, password_column):
        password = getpass.getpass(prompt="Please Enter Password: ")
        bytes_password = bytes(password, 'utf-8')
        stretching_password =  hashlib.sha256(self.salt + bytes_password).hexdigest()
        for _ in range(1000):
            stretching_password = hashlib.sha256(bytes(stretching_password, 'utf-8')).hexdigest()
        if stretching_password == password_column:
            return True
        else:
            return False

    @classmethod
    def salt_generate(self):
        import random
        ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        chars = []
        for i in range(16):
            chars.append(random.choice(ALPHABET))
        salt = "".join(chars)
        return bytes(salt, 'utf-8')
