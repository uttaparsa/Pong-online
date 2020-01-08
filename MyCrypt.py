#!/usr/bin/python3

from cryptography.fernet import Fernet
# from Crypto import Random
# from Crypto.PublicKey import RSA
import base64
class Symmetric:
    def __init__(self, key):
        self.key = key

    def encrypt(self , message):
        f = Fernet(self.key)
        encoded = message.encode()
        encrypted = f.encrypt(encoded)
        return encrypted

    def decrypt(self,encrypted):
        f2 = Fernet(self.key)
        decrypted = f2.decrypt(encrypted)
        originalStringMessage =  decrypted.decode('utf-8')
        return originalStringMessage

# class Assymetric:
    
#     def __init__(self):
#         # RSA modulus length must be a multiple of 256 and >= 1024
#         modulus_length = 256*4 # use larger value in production
#         self.privatekey = RSA.generate(modulus_length, Random.new().read)
#         self.publickey = privatekey.publickey()




#     def encrypt(self,a_message , publickey):
#         encrypted_msg = publickey.encrypt(a_message.encode(), 32)[0]
#         encoded_encrypted_msg = base64.b64encode(encrypted_msg) # base64 encoded strings are database friendly
#         return encoded_encrypted_msg

#     def decrypt(self,encoded_encrypted_msg, privatekey):
#         decoded_encrypted_msg = base64.b64decode(encoded_encrypted_msg)
#         decoded_decrypted_msg = privatekey.decrypt(decoded_encrypted_msg)
#         return decoded_decrypted_msg.decode('utf-8')



