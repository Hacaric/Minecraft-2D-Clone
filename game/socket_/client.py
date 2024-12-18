import socket
import threading

ip = "127.0.0.1"
port = 5555
encoding_type = "utf-8"

class DgramClient:
    def __init__(self, host=ip, port=port, process_function=None):
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

    def send(self, m_type, *message):
        message = f"{m_type}{'\x00'.join(list(map(str, message)))}"
        encoded_message = message.encode(encoding_type)
        #self.sock.sendto(message.encode(encoding_type), (self.host, self.port))
        self.sock.sendto(encoded_message, (self.host, self.port))
    def connect(self, name, host=ip, port=port):
        self.host = host
        self.port = port
        try:
            self.sock.send("00", name.encode(self.encoding_type))
        except Exception as e:
            print("Error line 30 in client.py:", e)
    def receive(self, buffer_size=1024):
        #TODO: add while true
        data, addr = self.sock.recvfrom(buffer_size)
        if data:
            self.process(data.decode(encoding_type))
        #return data.decode(encoding_type), addr
    
    def close(self):
        self.sock.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
class SockStreamClient:
    def __init__(self, process_function=None):
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
        message = message[2:].split("\x01")
        match data_type:
            case "00":
                print("Connection established!")
                self.nicknames = message
            case "01":
                print("Disconected.")
                print("Exiting.")
                self.client.close()
                threading._shutdown()
                exit()
            case "02":
                print(f"{message[0]} connected!")
                self.nicknames.append(message[0])
            case "03":
                print(f"{message[0]} disconnected!")
                self.nicknames.remove(message[0])
            case "04":
                print(f"{message[0]} changed their nickname to {message[1]}")
                try:
                    self.nicknames[self.nicknames.index(message[0])] = message[1]
                except ValueError:
                    pass
            case "05":
                if message[0] != self.nickname:
                    print(f"{message[0]} >>  {message[1]}")
            case "06":
                pass
            case _:
                print("Invalid message type.")
                print(data_type, message)
    
    def receive(self):
        while True:
            try:
                message = self.client.recv(1024).decode(self.encoding_type)
                if message:
                    self.process(message)
            except OSError as e:
                if e.errno == 9:
                    print("Quittig multiplayer.")
                    self.client.close()
                    return
            except Exception as e:
                #print("An error occured:", e)
                self.client.close()

    def send(self, *message):
        #print("Attempting to send:", *message)
        if type(list(message)) == tuple:
            print("message's tuple", message)
        if len(message) > 1:
            msg_type = message[0]
            message = message[1:]
        else:
            msg_type = message[0]
            message = []
        if (msg_type == "03" or msg_type == "02") and not message:
            print("Invalid message.")
            return
        #print("I like debug with print statements :D.")
        if msg_type == "02":
            self.nickname = message
        try:
            message = f"{msg_type}{'\x01'.join(message)}"
        except Exception as e:
            print("Error :P", e)
        #print("Message passed sending process.")
        self.client.send(message.encode(self.encoding_type))
    def connect(self, ip, port, nickname):
        self.nickname = nickname
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((ip, int(port)))
        self.client.send(f"00{self.nickname}".encode(self.encoding_type))
    def close(self):
        self.send("01")
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
    client_dgram = DgramClient()
    client_sock = SockStreamClient()

    #debug mode,
    #simple input mode

    mode = "sock_stream"
    while True:
        input_ = input("> ")
        if input_ == "exit":
            client_sock.send("01")
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
            client_dgram.send(input_[0:2], input_[2:])
        elif mode == "sock_stream":
            if input_[0:2] == "00" and input_[2:]:
                client_sock.connect(ip, port, input_[2:])
            else:
                client_sock.send(input_[0:2], input_[2:])
        else:
            print("Invalid input. Format for sock_stream: <message_type:2><message:*> or ! to switch mode")
if __name__ == "__main__":
    debug_mode()