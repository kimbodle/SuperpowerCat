
import time
import random
from colorsys import hsv_to_rgb
import board
from digitalio import DigitalInOut, Direction
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789
import numpy as np

class Obstacle:
    def __init__(self, x, y, width, height):
        self.position = [x, y]
        self.width = width
        self.height = height

    def is_character_inside(self, character):
        character_left = character.position[0]
        character_right = character.position[0] + character.character_image.width
        obstacle_left = self.position[0]
        obstacle_right = self.position[0] + self.width

        if obstacle_left <= character_left <= obstacle_right or obstacle_left <= character_right <= obstacle_right:
            return True
        return False