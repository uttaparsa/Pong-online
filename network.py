import socket
from constants import DEFAULT_PORT, SYMMETRIC , ASYMMETRIC , SERVER_NAME
from MyCrypt import *
keyf = open('key.key' , 'rb')
key = keyf.read()
cipher = Symmetric(key)

class ClientNetwork:

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = SERVER_NAME # For this to work on your machine this must be equal to the ipv4 address of the machine running the server
                                    # You can find this address by typing ipconfig in CMD and copying the ipv4 address. Again this must be the servers
                                    # ipv4 address. This feild will be the same for all your clients.
        self.port = DEFAULT_PORT
        self.addr = (self.host, self.port)
        initial_data = self.connect()
        self.id = initial_data.split('|')[0]
        # if ASYMMETRIC:
        #     server_public_key = initial_data.split('|')[1]

    def connect(self):
        self.client.connect(self.addr)
        return self.client.recv(2048).decode()
    
    def prepareData(self,data):
        if SYMMETRIC:
            data = cipher.encrypt(data)
            print(f'client: encrypted message with AES : {data}')
        else:
            data = str.encode(data)
        return data
        
    def send(self, data):
        """
        :param data: str
        :return: str
        """
        try:
            self.client.send(self.prepareData(data))
            data = self.client.recv(2048)
            if SYMMETRIC:
                reply = cipher.decrypt(data)
                print(f'client: decrypted message : {reply}')
            else:
                reply = data.decode('utf-8')
            return reply
        except socket.error as e:
            print("sockettt error")
            return str(e)
