
import time
import random
from colorsys import hsv_to_rgb
import board
from digitalio import DigitalInOut, Direction
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789
import numpy as np

class Obstacle: #장애물 클래스
    #장애물의 위치, 너비, 높이 초기화
    def __init__(self, x, y, width, height):
        self.position = [x, y]
        self.width = width
        self.height = height

    def is_character_inside(self, character):
        # 캐릭터가 장애물 내부에 있는지 확인
        character_left = character.position[0]
        character_right = character.position[0] + character.character_image.width
        character_top = character.position[1]
        character_bottom = character.position[1] + character.character_image.height

        obstacle_left = self.position[0]
        obstacle_right = self.position[0] + self.width
        obstacle_top = self.position[1]
        obstacle_bottom = self.position[1] + self.height
        # 캐릭터와 장애물의 좌표 정보(박스)가 겹치는지 확인
        if ((obstacle_left <= character_left <= obstacle_right or obstacle_left <= character_right <= obstacle_right) and
            (obstacle_top <= character_top <= obstacle_bottom or obstacle_top <= character_bottom <= obstacle_bottom)):
            return True #겹치면 true 반환
        return False #겹치지 않으면 false 반환