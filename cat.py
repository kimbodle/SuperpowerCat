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

class Character:
    def __init__(self, x, y, character_image_path):
        self.position = [x, y]
        self.jumping = False
        self.jump_height = 40  # 점프 높이
        self.jump_frames = 10  # 점프에 걸리는 프레임 수
        self.jump_frame_count = 0
        self.character_image = Image.open(character_image_path, mode='r').convert("RGBA")

    def move(self, joystick, platforms):
        # 조이스틱 입력에 따라 캐릭터 위치 갱신
        if joystick.is_button_pressed(joystick.button_U):
            self.position[1] -= 5
        elif joystick.is_button_pressed(joystick.button_D):
            self.position[1] += 5
        elif joystick.is_button_pressed(joystick.button_L):
            self.position[0] -= 5
        elif joystick.is_button_pressed(joystick.button_R):
            self.position[0] += 5

        # 플랫폼 위에서 움직임 확인
        on_platform = False
        for platform in platforms:
            if platform.is_character_above(self):
                # 캐릭터가 플랫폼 위에 있을 경우
                self.position[1] = platform.position[1] - self.character_image.height
                on_platform = True
                break

        # 캐릭터가 플랫폼 위에 있는지 확인
        if not on_platform:
            # 플랫폼 위에 없는 경우, 중력 효과 적용
            self.position[1] += 2

        # 점프 버튼 확인 및 캐릭터 점프
        if joystick.is_button_pressed(joystick.button_A) and not self.jumping and on_platform:
            self.jumping = True
            self.jump_frame_count = 0

        # 점프 중일 때 처리
        if self.jumping:
            self.position[1] -= 2
            self.jump_frame_count += 1

            if self.jump_frame_count >= self.jump_frames:
                self.jumping = False

    def draw(self, image, camera_position):
        # 캐릭터를 주어진 draw 객체를 사용하여 그림
        character_draw_position = (
            self.position[0] - camera_position[0],
            self.position[1] - camera_position[1],
        )
        image.alpha_composite(self.character_image, character_draw_position)

def stage1(joystick, my_character, platforms, background_image):
    # 초기 위치 설정
    camera_position = [0, 0]

    while True:
        ground_position = (
            -camera_position[0],
            240-80,  # 바닥 이미지를 배경의 하단에 고정
        )

        # 조이스틱 버튼 확인 및 캐릭터 위치 갱신
        my_character.move(joystick, platforms)

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
        image = Image.new("RGBA", (joystick.disp.width, joystick.disp.height))
        draw = ImageDraw.Draw(image)

        # 보이는 이미지 부분을 새로운 이미지에 붙여넣기
        image.paste(visible_image, (0, 0))

        my_character.draw(image, camera_position)

        # RGB 디스플레이에 이미지 표시
        joystick.disp.image(image.convert("RGBA"))

# Joystick 및 Character 클래스 인스턴스 생성
joystick = Joystick()
character_image_path = "/home/kau-esw/esw/SuperpowerCat/Asset/Charactor.png"  # 캐릭터 이미지 파일 경로
my_character = Character(
    joystick.disp.width // 2 - 20, joystick.disp.height // 2 - 20, character_image_path
)

# 플랫폼 생성
platforms = [
    Platform(0, 210, 240, 70),
    #Platform(100, 200, 50, 10),  # 플랫폼 위치와 크기 설정
    # 필요한 만큼 플랫폼을 추가할 수 있습니다.
]

# 큰 이미지 및 바닥 이미지 로드
background_image = Image.open(
    "/home/kau-esw/esw/SuperpowerCat/Asset/test_background.png"
).convert("RGB")

# 스테이지 1 시작
stage1(joystick, my_character, platforms, background_image)