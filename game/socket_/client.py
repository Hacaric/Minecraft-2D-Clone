import socket
import sys
import threading
import os
import random
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
from protocol import *

ip = "127.0.0.1"
port = 5555
encoding_type = "utf-8"
SPLIT_CHR = "\x01"

class SocketClient:
    def __init__(self, host=ip, port=port, encoding_type=encoding_type, logger=lambda *args: None):
        self.running = False
        self.log = logger
        self.serverHost = host
        self.serverPort = port
        self.encoding_type = encoding_type
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.authToken = None
    def connect(self, name=None, host=None, port=None):
        self.authToken = str(random.randint(10**5, 10**6-1))
        print(f"Auth token is: {self.authToken}")

        self.serverHost = host if host else self.serverHost
        self.serverPort = port if port else self.serverPort
        self.nickname = name if name else f"Guest{random.randint(1000, 9999)}"
        try:
            self.sendUDP(ProtocolUDP.ToServer.requestConnection, name.encode(self.encoding_type), )
        except Exception as e:
            print("[Error:SocektClient.connect:udp.connect] in client.py:", e)
            raise e
        try:
            self.tcp.connect((ip, port))
            self.sendTCP(ProtocolTCP.ToServer.requestConnection, self.nickname, self.authToken)
        except Exception as e:
            print("[Error:SocektClient.connect:tcp.connect] in client.py:", e)
            raise e
    def sendUDP(self, m_type, *message):
        if not self.running:
            self.log("[Error:SocketClient.sendUDP] SocketClient is not running.")
            return
        """
        Sends message through udp socket module.
        - m_type(str[2]): says to server what to do with data given in message. 
            Note: use protocol.ProtocolUDP.ToServer constants
        - message(list[any]): data will be divided with SPLIT_CHR and sent to server.
        """
        message = f"{m_type}{SPLIT_CHR.join(list(map(str, message)))}"
        encoded_message = message.encode(encoding_type)
        self.udp.sendto(encoded_message, (self.serverHost, self.serverPort))
    def sendTCP(self, m_type, *message):
        if not self.running:
            self.log("[Error:SocketClient.sendTCP] SocketClient is not running.")
            return
        """
        Sends message through tcp socket module.
        - m_type(str[2]): says to server what to do with data given in message.
            Note: use protocol.ProtocolTCP.ToServer constants
        - message(list[any]): data will be divided with SPLIT_CHR and sent to server.
        """
        message = f"{m_type}{SPLIT_CHR.join(list(map(str, message)))}"
        encoded_message = message.encode(self.encoding_type)
        self.tcp.send(encoded_message)
    def listen(self, handlerTCP, handlerUDP):
        self.running = True
        """
        Starts listening on sockets using threads.
        :param
            - handlerTCP and handlerUDP: all data received with TCP and UDP sockets modules will be passed to these functions.
            - all data received will be passed to these fuctions in format:\n
                func(message_type:str[2], *messages),\n
                where message_type are first two characters of received message and *messages is message splitted with SPLIT_CHR
        """
        def listenTCP(self, handler):
            buffer_size = 1024
            while self.running:
                try:
                    message = self.client.recv(buffer_size).decode(self.encoding_type)
                    if message:
                        handler(message)
                except Exception as e:
                    self.log("[Error:SocketClient.listenTCP] line in client.py:", e)
        def listenUDP(self, handler):
            buffer_size = 1024
            while self.running:
                try:
                    data, addr = self.sock.recvfrom(buffer_size)
                    if (self.serverHost, self.serverPort) != addr:
                        self.log(f"[Warning:SocketClient.listenUDP] Got message, not from server, ignoring. Address:{addr} Data: {data}")
                        continue
                    if data:
                        handler(data.decode(encoding_type))
                except Exception as e:
                    self.log("[Error:SocketClient.listenUDP] line in client.py:", e)
    
        threadTCP = threading.Thread(target=listenTCP, args=(self, handlerTCP))
        threadUDP = threading.Thread(target=listenUDP, args=(self, handlerUDP))
        threadTCP.start()
        threadUDP.start()
    def close(self):
        try:
            self.sendUDP(ProtocolUDP.ToServer.requestDisconnection)
            self.udp.close()
            self.sendTCP(ProtocolTCP.ToServer.requestDisconnection)
            self.tcp.close()
        except Exception as e:
            self.log("[Error:SocketClient.close] in client.py:", e)
class ClientUDP:
    def __init__(self, host=ip, port=port, process_function=None, logger=lambda *args: None):
        self.log = logger
        self.host = host
        self.port = port
        self.encoding_type = encoding_type
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if process_function == None:
            self.process = self.process_default
        else:
            self.process = process_function
    def process_default(self, message):
        pass

    def send(self, m_type:str, *message:str):
        message = f"{m_type}{SPLIT_CHR.join(list(map(str, message)))}"
        self.log("Sending mesdsage: ", message)
        encoded_message = message.encode(encoding_type)
        self.log("encoded message:", encoded_message)
        #self.sock.sendto(message.encode(encoding_type), (self.host, self.port))
        self.sock.sendto(encoded_message, (self.host, self.port))
    def connect(self, ip, port, name, auth=None):
        host = ip
        self.host = host
        self.port = port
        try:
            self.log(f"Connecting UDP (sending auth:{auth})...")
            if auth == None:
                self.send(ProtocolUDP.ToServer.requestConnection, name)
            else:
                self.send(ProtocolUDP.ToServer.requestConnection, name, auth)
        except Exception as e:
            self.log("[Error:33] line in client.py:", e)
    def receive(self, buffer_size=1024):
        #TODO: add while true
        data, addr = self.sock.recvfrom(buffer_size)
        if data:
            self.process(data.decode(encoding_type))
        #return data.decode(encoding_type), addr
    def recvfrom(self, buffer_size):
        return self.sock.recvfrom(buffer_size)
    def close(self):
        self.sock.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
class ClientTCP:
    def __init__(self, process_function=None, logger=lambda *args: None):
        self.log = logger
        self.encoding_type = encoding_type
        self.ip = ip
        self.port = port
        self.nickname = None
        self.nicknames = []
        self.client = None
        self.encoding_type = encoding_type
        if process_function == None:
            self.process = self.defaultprocess
        else:
            self.process = process_function

    def defaultprocess(self, message):
        data_type = message[:2]
        message = message[2:].split(SPLIT_CHR)
        match data_type:
            case ProtocolTCP.ToClient.connected:
                self.log("Connection established!")
                self.nicknames = message
            case ProtocolTCP.ToClient.disconnected:
                self.log("Disconected.")
                self.log("Exiting.")
                self.client.close()
                threading._shutdown()
                exit()
            case ProtocolTCP.ToClient.renamedClient:
                self.log(f"{message[0]} changed their nickname to {message[1]}")
                try:
                    self.nicknames[self.nicknames.index(message[0])] = message[1]
                except ValueError:
                    pass
            case _:
                self.log("Invalid message type.")
                self.log(data_type, message)
    
    def receive(self):
        while True:
            try:
                message = self.client.recv(1024).decode(self.encoding_type)
                if message:
                    self.process(message)
            except OSError as e:
                if e.errno == 9:
                    self.log("Quittig multiplayer.")
                    self.client.close()
                    return
            except Exception as e:
                #self.log("An error occured:", e)
                self.client.close()

    def send(self, msg_type:str, *message):
        # if (msg_type == "03" or msg_type == "02") and not message:
        #     self.log("Invalid message.")
        #     return
        if msg_type == ProtocolTCP.ToServer.renameClient:
            self.nickname = message[0]
        try:
            message = f"{msg_type}{SPLIT_CHR.join(list(map(str, message)))}"
        except Exception as e:
            self.log("Error :P", e)
        self.client.send(message.encode(self.encoding_type))
    def connect(self, ip, port, UDPport, nickname, auth=None):
        self.nickname = nickname
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.log("Connecting in socket client module...", f"\nConnecting to: {ip}:{port}")
        self.client.connect((ip, port))
        self.log("Sending auth...")
        if auth is None: 
            self.client.send(f"00{self.nickname}{SPLIT_CHR}{UDPport}".encode(self.encoding_type))
        else:
            self.client.send(f"00{self.nickname}{SPLIT_CHR}{UDPport}{SPLIT_CHR}{auth}".encode(self.encoding_type))
    def close(self):
        self.send(ProtocolTCP.ToServer.requestDisconnection)
        self.client.close()
# class SocketClient:
#     def __init__(self):
#         self.encoding_type = encoding_type
#         self.ip = ip
#         self.port = port
#         self.nickname = None
#         self.SockStream = SockStreamClient()
#         self.DgramClient = DgramClient()
#     def connect(self, nickname, ip=ip, port=port):
#         self.nickname = nickname
#         self.SockStream.connect(ip, port, nickname)
#         self.DgramClient.send("00", nickname)
#         threading.Thread(target=self.SockStream.receive).start()
#         threading.Thread(target=self.DgramClient.receive).start()
def debug_mode() -> None:
    print("Debug mode activated. Write \x27!\x27 to change mode or \x27exit\x27 to exit.")
    client_dgram = ClientUDP()
    client_sock = ClientTCP()
    client_both = SocketClient()
    #debug mode,
    #simple input mode

    mode = "sock_stream"
    while True:
        input_ = input("> ")
        if input_ == "exit":
            client_sock.send(ProtocolTCP.ToServer.requestDisconnection)
            client_both.close()
            client_sock.client.close()
            client_dgram.close()
            exit()
        if input_=="!":
            if mode == "sock_stream":
                mode = "dgram"
            else:
                mode = "sock_stream"
            print(f"Mode changed to {mode}")
            continue
        if mode == "dgram":
            client_both.sendUDP(input_[0:2], input_[2:])
        elif mode == "sock_stream":
            if input_[0:2] == ProtocolTCP.ToServer.requestConnection and input_[2:]:
                client_both.connect(host=ip, port=port, name=input_[2:])
            elif input_[0:2] == ProtocolTCP.ToServer.requestDisconnection:
                client_both.close()
            else:
                client_both.sendTCP(input_[0:2], input_[2:])
        else:
            print("Invalid input. Format for sock_stream: <message_type:2><message:*> or ! to switch mode")
if __name__ == "__main__":
    try:
        debug_mode()
    except Exception as e:
        print("[Client_module:error] Error occured, shutting down:", e)
        sys.exit()