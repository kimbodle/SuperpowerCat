from joystick import Joystick
from character import Character
from secondFloor import Platform
from obstacle import Obstacle
from portal import Portal
from game_funtions import show_intro_images, stage1


import time
import random
from colorsys import hsv_to_rgb
import board
from digitalio import DigitalInOut, Direction
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789
import numpy as np

def main():
    # Joystick 및 Character 클래스 인스턴스 생성
    joystick = Joystick()

    # 큰 이미지 로드
    background_image = Image.open("/home/kau-esw/esw/SuperpowerCat/Asset/test_background.png").convert("RGB")
    character_image_path = "/home/kau-esw/esw/SuperpowerCat/Asset/Charactor.png"  # 캐릭터 이미지 파일 경로

    # 플랫폼 생성
    platforms1 = [
        Platform(0, 210, 480, 70),
        Platform(100, 190, 50, 10),
        #Platform(240, 190, 50, 20) # 플랫폼 위치와 크기 설정
        # 필요한 만큼 플랫폼을 추가할 수 있습니다.
    ]

    intro_image_paths = [
        "/home/kau-esw/esw/SuperpowerCat/Asset/Intro1.png",
        "/home/kau-esw/esw/SuperpowerCat/Asset/Intro2.png",
        "/home/kau-esw/esw/SuperpowerCat/Asset/Intro3.png",
    ]

    obstacle1 = [
        Obstacle(0,210,1,1),
    ]
    
    portal1 = Portal(260, 190, 50, 20)



    my_character = Character(
        joystick.disp.width // 2 - 20, joystick.disp.height // 2 - 20, character_image_path
    )


    # 인트로 이미지 보여주기
    show_intro_images(joystick, intro_image_paths)

    # 스테이지 1 시작
    stage1(joystick, my_character, platforms1, background_image, obstacle1, portal1)
    
    print("스테이지 1 끝")
    
    
if __name__ == "__main__":
    main()