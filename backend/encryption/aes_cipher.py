import base64
import os
import json
import sys



from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from decouple import config


class AESCipher:
    def __init__(self, *args, **kwargs):
        self.secret_key = self.get_secret_key()

    @staticmethod
    def get_secret_key():
        key = config('ENCRYPTION_KEY')
        if key is None:
            raise ValueError('ENCRYPTION_KEY not found')
        key_bytes = base64.b64decode(key)
        if len(key_bytes) != 32:
            raise ValueError('ENCRYPTION_KEY must be 32 bytes')
        return key_bytes

    def encrypt_value(self, value):
        if value is None:
            return None
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        value = str(value).encode()

        iv = os.urandom(16)
        cipher = AES.new(self.secret_key, AES.MODE_CBC, iv)
        encrypted_bytes = cipher.encrypt(pad(value, AES.block_size))

        return base64.b64encode(iv + encrypted_bytes).decode()

    def decrypt_value(self, value):
        if not value:
            return value
        try:
            raw_data = base64.b64decode(value)
            iv, encrypted_bytes = raw_data[:16], raw_data[16:]

            cipher = AES.new(self.secret_key, AES.MODE_CBC, iv)
            decrypted_bytes = unpad(cipher.decrypt(encrypted_bytes), AES.block_size)
            decrypted_str = decrypted_bytes.decode()

            try:
                return json.loads(decrypted_str)
            except json.JSONDecodeError:
                return decrypted_str
        except Exception as e:
            print(f'Exception occured: {e}')
            return value