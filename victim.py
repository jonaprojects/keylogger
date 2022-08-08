import socket
import json
import random
import sys
import selectors
import types

SHELL_ARGUMENTS = sys.argv

# the ip and port shell arguments (but they have default values)
IP = '0.0.0.0' if len(SHELL_ARGUMENTS) < 2 else SHELL_ARGUMENTS[1]  # TODO: modify this
PORT = 5000 if len(SHELL_ARGUMENTS) < 3 else SHELL_ARGUMENTS[2]


class Victim:
    """
    This class represents the victim's socket. It is a server, as it serves sensitive information
    to the attacker.
    """

    def __init__(self, ip=IP, port=PORT):
        self._ip = ip
        self._port = port
        self._sel = selectors.DefaultSelector()
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sel.register(self._socket, selectors.EVENT_READ, data=None)

    @property
    def ip(self):
        return self._ip

    @property
    def port(self):
        return self._port

    def bind(self):
        self._socket.bind((self._ip, self._port))

    def listen(self):
        self._socket.listen()
        self._socket.setblocking(False)

    def initialize(self):
        """ bind to the ip and port, and then listen for new connections"""
        self.bind()
        self.listen()

    def accept(self, sock):
        conn, addr = sock.accept()  # Should be ready to read
        print(f"Accepted connection from {addr}")
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")  # represents the data that will be read or written
        # when communicating with the client.
        events = selectors.EVENT_READ | selectors.EVENT_WRITE  # we want to know when the sockets are ready
        # for reading or writing
        self._sel.register(conn, events, data=data)

    def service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:  # if we can read data from the client
            recv_data = sock.recv(1024)  # Should be ready to read
            if recv_data.decode('utf-8'):
                data.outb += recv_data
            else:
                print(f"Closing connection to {data.addr}")
                self._sel.unregister(sock)
                sock.close()
        if mask & selectors.EVENT_WRITE:
            if data.outb.decode('utf-8'):
                print(f"Echoing {data.outb!r} to {data.addr}")
                sent = sock.send(data.outb)  # Should be ready to write
                print(f"{sent=}")
                data.outb = data.outb[sent:]

    def run(self):
        try:
            while True:
                events = self._sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        self.accept(key.fileobj)
                    else:
                        self.service_connection(key, mask)
        except KeyboardInterrupt:
            print("Caught keyboard interrupt, exiting")
        finally:
            self._sel.close()

def main():
    victim_server = Victim()
    victim_server.bind()
    print("binded server!")
    print("server is listening....")
    victim_server.listen()
    victim_server.run()


if __name__ == '__main__':
    main()
