import time
import random
from colorsys import hsv_to_rgb
import board
from digitalio import DigitalInOut, Direction
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789
import numpy as np

class Platform:
    def __init__(self, x, y, width, height):
        self.position = [x, y]
        self.width = width
        self.height = height

    def is_character_above(self, character):
        # 캐릭터 이미지의 하단 중점 좌표
        character_bottom_center = (
            character.position[0] + character.character_image.width // 2,
            character.position[1] + character.character_image.height,
        )

        # 플랫폼 이미지의 왼쪽 위 끝점과 오른쪽 아래 끝점 좌표
        platform_top_left = self.position
        platform_bottom_right = (
            self.position[0] + self.width,
            self.position[1] + self.height,
        )

        # 캐릭터 이미지의 하단 중점이 플랫폼 이미지 내에 있는지 확인
        if (
            platform_top_left[0] <= character_bottom_center[0] <= platform_bottom_right[0]
            and platform_top_left[1] <= character_bottom_center[1] <= platform_bottom_right[1]
        ):
            return True
        return False