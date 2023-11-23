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

class Character:
    def __init__(self, x, y, character_image_path):
        self.position = [x, y]
        self.jumping = False
        self.jump_height = 40  # 점프 높이
        self.jump_frames = 10  # 점프에 걸리는 프레임 수
        self.jump_frame_count = 0
        self.character_image = Image.open(character_image_path, mode='r').convert("RGBA")
        #self.lives = 3
        self.life_manager = LifeManager(3)  # 캐릭터의 목숨 관리자
        self.invincible = False  # 무적 상태
        self.invincibility_start_time = None  # 무적 상태 시작 시간

    def move(self, joystick, platforms):
        # 조이스틱 입력에 따라 캐릭터 위치 갱신
        #if joystick.is_button_pressed(joystick.button_U):
        #    self.position[1] -= 5
        if joystick.is_button_pressed(joystick.button_D):
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
        if joystick.is_button_pressed(joystick.button_U) and not self.jumping and on_platform:
            self.jumping = True
            self.jump_frame_count = 0

        # 점프 중일 때 처리
        if self.jumping:
            self.position[1] -= 7
            self.jump_frame_count += 1

            if self.jump_frame_count >= self.jump_frames:
                self.jumping = False

    def check_collision(self, obstacles):
        # 무적 상태가 아닐 때만 충돌을 검사하고 목숨을 감소
        if not self.invincible:
            for obstacle in obstacles:
                if obstacle.is_character_inside(self):
                    self.life_manager.decrease_life()
                    self.invincible = True  # 무적 상태 시작
                    self.invincibility_start_time = time.time()  # 무적 상태 시작 시간 저장
                    break

        # 무적 상태에서 3초가 지났으면 무적 상태 해제
        if self.invincible and time.time() - self.invincibility_start_time >= 3:
            self.invincible = False
            self.invincibility_start_time = None
            
            
    def draw(self, image, camera_position):
        # 캐릭터를 주어진 draw 객체를 사용하여 그림
        character_draw_position = (
            self.position[0] - camera_position[0],
            self.position[1] - camera_position[1],
        )
        image.alpha_composite(self.character_image, character_draw_position)

class LifeManager:
    def __init__(self, initial_lives):
        self.lives = initial_lives

    def decrease_life(self):
        self.lives -= 1

    def get_lives(self):
        return self.lives
    
class Portal:
    def __init__(self, x, y, width, height):
        self.position = [x, y]
        self.width = width
        self.height = height

    def is_character_inside(self, character):
        character_left_top = character.position
        character_right_bottom = (
            character.position[0] + character.character_image.width,
            character.position[1] + character.character_image.height,
        )

        portal_left_top = self.position
        portal_right_bottom = (
            self.position[0] + self.width,
            self.position[1] + self.height,
        )

        if (
            (portal_left_top[0] <= character_left_top[0] <= portal_right_bottom[0]
            and portal_left_top[1] <= character_left_top[1] <= portal_right_bottom[1])
            or
            (portal_left_top[0] <= character_right_bottom[0] <= portal_right_bottom[0]
            and portal_left_top[1] <= character_right_bottom[1] <= portal_right_bottom[1])
        ):
            return True
        return False

    
    
def show_intro_images(joystick, intro_images):
    # 이미지를 보여주는 함수
    for image_path in intro_images:
        # 이미지를 로드하고 RGB 모드로 변환
        image = Image.open(image_path).convert("RGB")

        # 디스플레이 크기에 맞게 이미지 크기를 조정
        image = image.resize((joystick.disp.width, joystick.disp.height))

        # A 버튼이 눌릴 때까지 이미지를 계속해서 디스플레이에 표시
        while True:
            joystick.disp.image(image)
            if joystick.is_button_pressed(joystick.button_A):
                time.sleep(0.2)  # 디바운싱: 버튼이 눌렸다 떼어진 후 0.2초 동안 추가 입력을 무시
                break


def stage1(joystick, my_character, platforms, background_image, obstacles, portal):
    # 초기 위치 설정
    camera_position = [0, 0]
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)


    while True:

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
        draw.text((170, 10), f"Lives: {my_character.life_manager.get_lives()}", fill=(255,255,102), font=font)
        draw.text((10, 10), f"Stage 1", fill=(153,255,51), font=font)
        
        # 충돌 확인 및 목숨 감소
        previous_lives = my_character.life_manager.get_lives()  # 충돌 전 캐릭터의 목숨
        my_character.check_collision(obstacles)
        
        if my_character.life_manager.get_lives() < previous_lives:
            draw.text((10, 10), f"Lives: {my_character.life_manager.get_lives()}", fill="red", font=font)

        # 캐릭터의 목숨이 0 이하인 경우 게임 종료
        if my_character.life_manager.get_lives() <= 0:
            print("Game over!") # 이걸 이제 나중에 게임 오버 인트로 함수 부르면 될듯
            break
        
        if portal.is_character_inside(my_character) and joystick.is_button_pressed(joystick.button_U):
            print("포탈")
            break
        

        my_character.draw(image, camera_position)

        # RGB 디스플레이에 이미지 표시
        joystick.disp.image(image.convert("RGBA"))



# 큰 이미지 로드
background_image = Image.open("/home/kau-esw/esw/SuperpowerCat/Asset/test_background.png").convert("RGB")
character_image_path = "/home/kau-esw/esw/SuperpowerCat/Asset/Charactor.png"  # 캐릭터 이미지 파일 경로

###background_images = [ (여기에 배열로 넣고 아래 스테이지를 부를 때, background_image[0,1... 이렇게 해도 되지 않나])]

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

# Joystick 및 Character 클래스 인스턴스 생성
joystick = Joystick()

my_character = Character(
    joystick.disp.width // 2 - 20, joystick.disp.height // 2 - 20, character_image_path
)

# 포탈 생성
portal1 = Portal(260, 190, 50, 20)  # 포탈 위치와 크기 설정


# 인트로 이미지 보여주기
show_intro_images(joystick, intro_image_paths)

# 스테이지 1 시작
stage1(joystick, my_character, platforms1, background_image, obstacle1, portal1)