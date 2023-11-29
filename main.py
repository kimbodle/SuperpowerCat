from joystick import Joystick
from character import Character
from secondFloor import Platform
from obstacle import Obstacle
from portal import Portal
from game_funtions import show_intro_images, stage1, stage2, stage3
from character2 import Character2, Bullet, Monster
from character3 import Character3, Bullet, Monster
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
    

    #이미지 로드
    background_image0 = Image.open("/home/kau-esw/esw/SuperpowerCat/Asset/stage1.png").convert("RGB") #스테이지1 배경 완료
    background_image1 = Image.open("/home/kau-esw/esw/SuperpowerCat/Asset/monster_stage1.png").convert("RGBA") # 몬스터 스테이지1 배경
    background_image2 = Image.open("/home/kau-esw/esw/SuperpowerCat/Asset/stage2.png").convert("RGB")
    background_image3 = Image.open("/home/kau-esw/esw/SuperpowerCat/Asset/monster_stage2.png").convert("RGBA")
    background_image4 = Image.open("/home/kau-esw/esw/SuperpowerCat/Asset/stage3.png").convert("RGBA")
    background_image5 = Image.open("/home/kau-esw/esw/SuperpowerCat/Asset/monster_stage31.png").convert("RGBA")
    background_image6 = Image.open("/home/kau-esw/esw/SuperpowerCat/Asset/monster_stage32r.png").convert("RGBA")
    
    
    character_image_path = "/home/kau-esw/esw/SuperpowerCat/Asset/Charactor.png"  # 캐릭터 이미지 파일 경로 완료
    skill0 = Image.open("/home/kau-esw/esw/SuperpowerCat/Asset/skill0.png").convert("RGBA")
    skill0_end = Image.open("/home/kau-esw/esw/SuperpowerCat/Asset/skill0_end.png").convert("RGBA")
    skill0_error = Image.open("/home/kau-esw/esw/SuperpowerCat/Asset/skill0_error.png").convert("RGBA")
    skill2 = Image.open("/home/kau-esw/esw/SuperpowerCat/Asset/skill2.png").convert("RGBA")
    skill2_end = Image.open("/home/kau-esw/esw/SuperpowerCat/Asset/skill2_end.png").convert("RGBA")
    skill2_error = Image.open("/home/kau-esw/esw/SuperpowerCat/Asset/skill2_error.png").convert("RGBA")
    skill31 = Image.open("/home/kau-esw/esw/SuperpowerCat/Asset/skill31.png").convert("RGBA")
    skill31_end = Image.open("/home/kau-esw/esw/SuperpowerCat/Asset/skill31_end.png").convert("RGBA")
    skill31_error = Image.open("/home/kau-esw/esw/SuperpowerCat/Asset/skill31_error.png").convert("RGBA")
    skill32 = Image.open("/home/kau-esw/esw/SuperpowerCat/Asset/skill32.png").convert("RGBA")
    skill32_end = Image.open("/home/kau-esw/esw/SuperpowerCat/Asset/skill32_end.png").convert("RGBA")
    skill32_error = Image.open("/home/kau-esw/esw/SuperpowerCat/Asset/skill32_error.png").convert("RGBA")
    
    bullet_image_path = "/home/kau-esw/esw/SuperpowerCat/Asset/bullet.png"
    monster_image_path1 = "/home/kau-esw/esw/SuperpowerCat/Asset/mini_monster1.png"
    monster_image_path2 = "/home/kau-esw/esw/SuperpowerCat/Asset/mini_monster2.png"

    background_images = [background_image0, background_image1, background_image2, background_image3, background_image4, background_image5, background_image6]

    monsters =[ Monster(542,144,61,47,monster_image_path1), Monster(1343,105,61,47,monster_image_path1), Monster(1600,133,41,62,monster_image_path2),Monster(1800,132,41,62,monster_image_path2),
               Monster(806,145,68,50,monster_image_path1), Monster(1257,134,48,61,monster_image_path2)]
    
    # 플랫폼 생성
    platforms1 = [
        Platform(0, 210, 1920, 30), #바닥
        Platform(297, 144, 84, 34),
        Platform(420, 85, 43, 34),
        Platform(633,166,86,43),
        Platform(761,121,86,43),
        Platform(847,116,120,31),
        Platform(964,124,84,85),
        Platform(1309,163,43,34),
        Platform(1400,126,43,34),
        Platform(1606,173,33,36),
        #Platform(240, 190, 50, 20) # 플랫폼 위치와 크기 설정
    ]
    
    platforms2 = [
        Platform(0, 210, 1920, 30), #바닥
        Platform(226,169,43,42),
        Platform(291,124,129,42),
        Platform(877,156,44,34),
        Platform(964,121,44,34),
        Platform(1058,115,84,27),
        Platform(1269,170,121,39),
        Platform(1443,124,43,85),
        #Platform(240, 190, 50, 20) # 플랫폼 위치와 크기 설정
    ]
    
    platforms3 = [
        Platform(0, 210, 1920, 30), #바닥
        Platform(242,171,85,13),
        Platform(359,135,44,19),
        Platform(422,88,44,19),
        Platform(469,83,124,27),
        Platform(592,89,42,41),
        Platform(854,154,42,42),
        Platform(1021,130,85,85),
        Platform(1412,175,39,37),
        Platform(1485,117,43,42),
        Platform(1580,97,57,29),
        Platform(1635,99,127,29),
        Platform(1761,104,45,24)
    ]

    intro_image_paths = [
        "/home/kau-esw/esw/SuperpowerCat/Asset/Intro1.png",
        "/home/kau-esw/esw/SuperpowerCat/Asset/Intro2.png",
        "/home/kau-esw/esw/SuperpowerCat/Asset/Intro3.png",
        "/home/kau-esw/esw/SuperpowerCat/Asset/Intro4.png",
    ]

    skills = [skill0, skill0_error, skill0_end, skill2, skill2_error, skill2_end, skill31, skill31_error, skill31_end, skill32, skill32_error, skill32_end ]

    obstacle1 = [
        Obstacle(0,210,1,1),
        Obstacle(442,182,79,27),
        Obstacle(1384,180,79,27),
    ]
    
    obstacle2 = [
        Obstacle(0,183,70,29),
        Obstacle(733,184,52,28),
        Obstacle(969,183,77,28),
    ]
    
    obstacle3 = [
        Obstacle(361,168,39,15),
        Obstacle(417,199,77,15),
        Obstacle(541,186,158,28),
        Obstacle(946,188,79,26),
        Obstacle(1412,160,38,15),
        Obstacle(1635,186,159,28),
    ]
    

    my_character = Character(
        joystick.disp.width // 2 - 60, joystick.disp.height // 2 - 20, character_image_path
    )
    
    my_character2 = Character2(
        joystick.disp.width // 2 - 60, joystick.disp.height // 2 - 20, character_image_path, bullet_image_path
    )
    
    my_character3 = Character3(
        joystick.disp.width // 2 - 60, joystick.disp.height // 2 - 20, character_image_path, bullet_image_path
    )

    # 포탈 생성
    #portal1 = Portal(260, 190, 50, 20)  # 포탈 위치와 크기 설정
    portal1 = Portal(1815,121,42,105)

    # 인트로 이미지 보여주기
    show_intro_images(joystick, intro_image_paths)

    # 스테이지 1 시작
    #stage1(joystick, my_character, platforms1, background_images[0], obstacle1, portal1, background_images, skills)
    print("스테이지 1 끝")
    
    stage2(joystick, my_character2, platforms2, background_images[2], obstacle2, portal1, background_images, skills, monsters)
    print("스테이지 2 끝")
    
    stage3(joystick, my_character3, platforms3, background_images[4], obstacle3, portal1, background_images, skills, monsters)
   
    
    
if __name__ == "__main__":
    main()