from modules.commands import handle_input
from socket import error as SocketError
import errno
import socket
import select
import config

class Server():
    def __init__(self, config, worker):
        self.config = config
        self.is_running = True
        self.port = config['port']
        self.host = config['host']
        self.inputs = []
        self.outputs = []
        self.authorized = []
        self.BUFFER_SIZE = 1024
        self.worker = worker
        self.hello = "### Python Manager\nHello !\n(password)\n#>"
        self.socket = None
        
    def start(self):
        print("Server starting")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        self.inputs.append(self.socket)
        while self.is_running:
            _in, _out, exception = select.select(self.inputs,
                                                 self.outputs,
                                                 [])
            for sock in _in:
                if sock == self.socket:
                    client, address = sock.accept()
                    print(address)
                    self.inputs.append(client)
                    client.send(self.hello.encode())
                else:
                    try:    
                        data = sock.recv(self.BUFFER_SIZE)
                        if data:
                            if sock not in self.authorized:
                                pwd = data.decode("UTF-8").strip()
                                if pwd != config.daemon['password']:
                                    output = "Invalid password.\n(password)"
                                else:
                                    self.authorized.append(sock)
                                    output = "\033[H\033[2J"
                            else:
                                command = data.decode("UTF-8")
                                success, output = handle_input(command, self.worker, self)
                            sock.send(output.encode()+b"\n#> ")
                        else:
                            if sock in self.outputs:
                                self.outputs.remove(sock)
                            if sock in self.inputs:
                                self.inputs.remove(sock)
                            if sock not in self.outputs:
                                self.outputs.append(sock)                    
                    except SocketError as e:
                        if e.errno != errno.ECONNRESET:
                            raise
                        self.inputs.remove(sock)

    def stop(self):    
        print("Exiting...")
        if self.socket is not None:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except OSError as e:
                pass
            self.socket.close()

    def restart(self):
        print("Restarting...")
        if self.socket is not None:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
        self.__init__(self.config, self.worker)
        self.stop()
