import cv2
import base64
import requests
import numpy as np
import random
import hashlib
from urllib.parse import *
import time
import json


class PuzzleSolver:
    def __init__(self, base64puzzle, base64piece):
        self.puzzle = base64puzzle
        self.piece = base64piece

    def get_position(self):
        puzzle = self.__background_preprocessing()
        piece = self.__piece_preprocessing()
        matched = cv2.matchTemplate(puzzle, piece, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(matched)
        return max_loc[0]

    def __background_preprocessing(self):
        img = self.__img_to_grayscale(self.piece)
        background = self.__sobel_operator(img)
        return background

    def __piece_preprocessing(self):
        img = self.__img_to_grayscale(self.puzzle)
        template = self.__sobel_operator(img)
        return template

    def __sobel_operator(self, img):
        scale = 1
        delta = 0
        ddepth = cv2.CV_16S

        img = cv2.GaussianBlur(img, (3, 3), 0)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        grad_x = cv2.Sobel(
            gray,
            ddepth,
            1,
            0,
            ksize=3,
            scale=scale,
            delta=delta,
            borderType=cv2.BORDER_DEFAULT,
        )
        grad_y = cv2.Sobel(
            gray,
            ddepth,
            0,
            1,
            ksize=3,
            scale=scale,
            delta=delta,
            borderType=cv2.BORDER_DEFAULT,
        )
        abs_grad_x = cv2.convertScaleAbs(grad_x)
        abs_grad_y = cv2.convertScaleAbs(grad_y)
        grad = cv2.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)

        return grad

    def __img_to_grayscale(self, img):
        return cv2.imdecode(self.__string_to_image(img), cv2.IMREAD_COLOR)

    def __string_to_image(self, base64_string):

        return np.frombuffer(base64.b64decode(base64_string), dtype="uint8")

class Xgorgon:
    def __init__(self, params: str, data: str, cookies: str) -> None:

        self.params = params
        self.data = data
        self.cookies = cookies

    def hash(self, data: str) -> str:
        _hash = str(hashlib.md5(data.encode()).hexdigest())

        return _hash

    def get_base_string(self) -> str:
        base_str = self.hash(self.params)
        base_str = (
            base_str + self.hash(self.data) if self.data else base_str + str("0" * 32)
        )
        base_str = (
            base_str + self.hash(self.cookies)
            if self.cookies
            else base_str + str("0" * 32)
        )

        return base_str

    def get_value(self) -> json:
        base_str = self.get_base_string()

        return self.encrypt(base_str)

    def encrypt(self, data: str) -> json:
        unix = int(time.time())
        len = 0x14
        key = [
            0xDF,
            0x77,
            0xB9,
            0x40,
            0xB9,
            0x9B,
            0x84,
            0x83,
            0xD1,
            0xB9,
            0xCB,
            0xD1,
            0xF7,
            0xC2,
            0xB9,
            0x85,
            0xC3,
            0xD0,
            0xFB,
            0xC3,
        ]

        param_list = []

        for i in range(0, 12, 4):
            temp = data[8 * i : 8 * (i + 1)]
            for j in range(4):
                H = int(temp[j * 2 : (j + 1) * 2], 16)
                param_list.append(H)

        param_list.extend([0x0, 0x6, 0xB, 0x1C])

        H = int(hex(unix), 16)

        param_list.append((H & 0xFF000000) >> 24)
        param_list.append((H & 0x00FF0000) >> 16)
        param_list.append((H & 0x0000FF00) >> 8)
        param_list.append((H & 0x000000FF) >> 0)

        eor_result_list = []

        for A, B in zip(param_list, key):
            eor_result_list.append(A ^ B)

        for i in range(len):

            C = self.reverse(eor_result_list[i])
            D = eor_result_list[(i + 1) % len]
            E = C ^ D

            F = self.rbit_algorithm(E)
            H = ((F ^ 0xFFFFFFFF) ^ len) & 0xFF
            eor_result_list[i] = H

        result = ""
        for param in eor_result_list:
            result += self.hex_string(param)

        return {"X-Gorgon": ("0404b0d30000" + result), "X-Khronos": str(unix)}

    def rbit_algorithm(self, num):
        result = ""
        tmp_string = bin(num)[2:]

        while len(tmp_string) < 8:
            tmp_string = "0" + tmp_string

        for i in range(0, 8):
            result = result + tmp_string[7 - i]

        return int(result, 2)

    def hex_string(self, num):
        tmp_string = hex(num)[2:]

        if len(tmp_string) < 2:
            tmp_string = "0" + tmp_string

        return tmp_string

    def reverse(self, num):
        tmp_string = self.hex_string(num)

        return int(tmp_string[1:] + tmp_string[:1], 16)

class Solver:
    def __init__(self, did, iid):
        self.__host = "verification-va.tiktokv.com"
        self.__device_id = did
        self.__install_id = iid
        self.__cookies = ""
        self.__client = requests.Session()

    def __params(self):
        params = {
            "lang": "en",
            "app_name": "musical_ly",
            "h5_sdk_version": "2.26.17",
            "sdk_version": "1.3.3-rc.7.3-bugfix",
            "iid": self.__install_id,
            "did": self.__device_id,
            "device_id": self.__device_id,
            "ch": "beta",
            "aid": "1233",
            "os_type": "0",
            "mode": "",
            "tmp": f"{int(time.time())}{random.randint(111, 999)}",
            "platform": "app",
            "webdriver": "false",
            "verify_host": f"https://{self.__host}/",
            "locale": "en",
            "channel": "beta",
            "app_key": "",
            "vc": "18.2.15",
            "app_verison": "18.2.15",
            "session_id": "",
            "region": ["va", "US"],
            "use_native_report": "0",
            "use_jsb_request": "1",
            "orientation": "1",
            "resolution": ["900*1552", "900*1600"],
            "os_version": ["25", "7.1.2"],
            "device_brand": "samsung",
            "device_model": "SM-G973N",
            "os_name": "Android",
            "challenge_code": "1105",
            "app_version": "18.2.15",
            "subtype": "",
        }

        return urlencode(params)

    def __headers(self) -> dict:

        headers = {
            "passport-sdk-version": "19",
            "sdk-version": "2",
            "x-ss-req-ticket": f"{int(time.time())}{random.randint(111, 999)}",
            "cookie": self.__cookies,
            "content-type": "application/json; charset=utf-8",
            "host": self.__host,
            "connection": "Keep-Alive",
            "user-agent": "okhttp/3.10.0.1",
        }

        return headers

    def __get_challenge(self) -> dict:

        params = self.__params()

        req = self.__client.get(
            url=("https://" + self.__host + "/captcha/get?" + params),
            headers=self.__headers(),
        )

        return req.json()

    def __solve_captcha(self, url_1: str, url_2: str) -> dict:
        puzzle = base64.b64encode(
            self.__client.get(
                url_1,
            ).content
        )
        piece = base64.b64encode(
            self.__client.get(
                url_2,
            ).content
        )

        solver = PuzzleSolver(puzzle, piece)
        maxloc = solver.get_position()
        randlength = round(random.random() * (100 - 50) + 50)
        time.sleep(1)  # don't remove delay or it will fail
        return {"maxloc": maxloc, "randlenght": randlength}

    def __post_captcha(self, solve: dict) -> dict:
        params = self.__params()

        body = {
            "modified_img_width": 552,
            "id": solve["id"],
            "mode": "slide",
            "reply": list(
                {
                    "relative_time": i * solve["randlenght"],
                    "x": round(solve["maxloc"] / (solve["randlenght"] / (i + 1))),
                    "y": solve["tip"],
                }
                for i in range(solve["randlenght"])
            ),
        }

        headers = self.__headers()

        req = self.__client.post(
            url=("https://" + self.__host + "/captcha/verify?" + params),
            headers=headers.update({"content-type": "application/json"}),
            json=body,
        )

        return req.json()

    def solve_captcha(self):
        __captcha_challenge = self.__get_challenge()

        __captcha_id = __captcha_challenge["data"]["id"]
        __tip_y = __captcha_challenge["data"]["question"]["tip_y"]

        solve = self.__solve_captcha(
            __captcha_challenge["data"]["question"]["url1"],
            __captcha_challenge["data"]["question"]["url2"],
        )

        solve.update({"id": __captcha_id, "tip": __tip_y})

        return self.__post_captcha(solve)


