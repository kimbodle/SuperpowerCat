
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
        character_top = character.position[1]
        character_bottom = character.position[1] + character.character_image.height

        obstacle_left = self.position[0]
        obstacle_right = self.position[0] + self.width
        obstacle_top = self.position[1]
        obstacle_bottom = self.position[1] + self.height

        if ((obstacle_left <= character_left <= obstacle_right or obstacle_left <= character_right <= obstacle_right) and
            (obstacle_top <= character_top <= obstacle_bottom or obstacle_top <= character_bottom <= obstacle_bottom)):
            return True
        return False