import time
import random
from colorsys import hsv_to_rgb
import board
from digitalio import DigitalInOut, Direction
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789
import numpy as np

class Joystick:
    def __init__(self):
        # 디스플레이 설정
        self.cs_pin = DigitalInOut(board.CE0)
        self.dc_pin = DigitalInOut(board.D25)
        self.reset_pin = DigitalInOut(board.D24)
        self.BAUDRATE = 24000000

        self.spi = board.SPI()
        self.disp = st7789.ST7789(
            self.spi,
            height=240,
            y_offset=80,
            rotation=180,
            cs=self.cs_pin,
            dc=self.dc_pin,
            rst=self.reset_pin,
            baudrate=self.BAUDRATE,
        )

        # 입력 핀 설정: 조이스틱, 버튼 1, 2
        self.button_L = DigitalInOut(board.D27)
        self.button_L.direction = Direction.INPUT

        self.button_R = DigitalInOut(board.D23)
        self.button_R.direction = Direction.INPUT

        self.button_U = DigitalInOut(board.D17)
        self.button_U.direction = Direction.INPUT

        self.button_D = DigitalInOut(board.D22)
        self.button_D.direction = Direction.INPUT

        self.button_C = DigitalInOut(board.D4)
        self.button_C.direction = Direction.INPUT

        self.button_A = DigitalInOut(board.D5)
        self.button_A.direction = Direction.INPUT

        self.button_B = DigitalInOut(board.D6)
        self.button_B.direction = Direction.INPUT

    def is_button_pressed(self, button):
        # 버튼이 눌렸는지 확인
        return not button.value

class Character:
    def __init__(self, x, y, character_image_path):
        self.position = [x, y]
        self.jumping = False
        self.jump_height = 40  # 점프 높이
        self.jump_frames = 10  # 점프에 걸리는 프레임 수
        self.jump_frame_count = 0
        self.character_image = Image.open(character_image_path).convert("RGBA")

    def move(self, joystick):
        # 조이스틱 입력에 따라 캐릭터 위치 갱신
        if joystick.is_button_pressed(joystick.button_U):
            self.position[1] -= 5
        elif joystick.is_button_pressed(joystick.button_D):
            self.position[1] += 5
        elif joystick.is_button_pressed(joystick.button_L):
            self.position[0] -= 5
        elif joystick.is_button_pressed(joystick.button_R):
            self.position[0] += 5

        # 점프 버튼 확인 및 캐릭터 점프
        if joystick.is_button_pressed(joystick.button_A) and not self.jumping:
            self.jumping = True
            self.jump_frame_count = 0

        # 점프 중일 때 처리
        if self.jumping:
            self.position[1] -= 2
            self.jump_frame_count += 1

            if self.jump_frame_count >= self.jump_frames:
                self.jumping = False

    def draw(self, draw, camera_position):
        # 캐릭터를 주어진 draw 객체를 사용하여 그림
        character_draw_position = (
            self.position[0] - camera_position[0],
            self.position[1] - camera_position[1],
        )
        draw.bitmap(character_draw_position, self.character_image)

    def is_on_ground(self, ground_position):
        # 캐릭터가 땅 위에 있는지 확인
        return self.position[1] >= ground_position[1]

    def can_fall(self, ground_position):
        # 캐릭터가 땅에서 떨어질 수 있는지 확인
        return not self.is_on_ground(ground_position)

# Joystick 및 Character 클래스 인스턴스 생성
joystick = Joystick()
character_image_path = "/home/kau-esw/esw/SuperpowerCat/Asset/Charactor.png"  # 캐릭터 이미지 파일 경로
my_character = Character(
    joystick.disp.width // 2 - 20, joystick.disp.height // 2 - 20, character_image_path
)

# 큰 이미지 및 바닥 이미지 로드
background_image = Image.open(
    "/home/kau-esw/esw/SuperpowerCat/Asset/test_background.png"
).convert("RGB")
ground_image = Image.open("/home/kau-esw/esw/SuperpowerCat/Asset/ground.png").convert(
    "RGBA"
)

# 초기 위치 설정
camera_position = [0, 0]
# ...

while True:
    # 조이스틱 버튼 확인 및 캐릭터 위치 갱신
    my_character.move(joystick)

    # 카메라 위치 조절 (이미지 경계를 벗어나지 않도록)
    camera_position[0] = max(
        0, min(my_character.position[0] - joystick.disp.width // 7, background_image.width - joystick.disp.width)
    )
    camera_position[1] = max(
        0, min(my_character.position[1] - joystick.disp.height // 2, background_image.height - joystick.disp.height)
    )

    # 화면에 보이는 이미지 부분 자르기
    visible_image = background_image.crop(
        (
            camera_position[0],
            camera_position[1],
            camera_position[0] + joystick.disp.width,
            camera_position[1] + joystick.disp.height,
        )
    )

    # RGB 모드의 빈 이미지 생성
    image = Image.new("RGB", (joystick.disp.width, joystick.disp.height))
    draw = ImageDraw.Draw(image)

    # 보이는 이미지 부분을 새로운 이미지에 붙여넣기
    image.paste(visible_image, (0, 0))

    # 바닥 이미지 그리기 (배경 이미지의 움직임에 따라 같이 움직임)
    ground_position = (
        -camera_position[0],
        #my_character.position[0] - camera_position[0],
        background_image.height - ground_image.height,  # 바닥 이미지를 배경의 하단에 고정
    )
    image.paste(ground_image, ground_position, mask=ground_image)

    # 캐릭터 아래에 바닥 이미지 그리기
    my_character.draw(draw, camera_position)

    # RGB 디스플레이에 이미지 표시
    joystick.disp.image(image)
