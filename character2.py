import time
from PIL import Image, ImageDraw, ImageFont

class Character2:
    def __init__(self, x, y, character_image_path, bullet_image_path):
        self.position = [x, y]
        self.jumping = False
        self.jump_height = 40  # 점프 높이
        self.jump_frames = 10  # 점프에 걸리는 프레임 수
        self.jump_frame_count = 0
        self.character_image = Image.open(character_image_path, mode='r').convert("RGBA")
        self.bullet = Bullet(x, y, bullet_image_path)
        #self.lives = 3
        self.life_manager = LifeManager(3)  # 캐릭터의 목숨 관리자
        self.invincible = False  # 무적 상태
        self.invincibility_start_time = None  # 무적 상태 시작 시간

    def move(self, joystick, platforms, monster):
        # 조이스틱 입력에 따라 캐릭터 위치 갱신
        #if joystick.is_button_pressed(joystick.button_U):
        #    self.position[1] -= 5
        if joystick.is_button_pressed(joystick.button_D):
            self.position[1] += 5
        elif joystick.is_button_pressed(joystick.button_L):
            self.position[0] -= 5
        elif joystick.is_button_pressed(joystick.button_R):
            self.position[0] += 5
            
        if joystick.is_button_pressed(joystick.button_A):
            if not self.bullet.active:
                self.bullet.position = [self.position[0], self.position[1]]
                self.bullet.active = True
        
        # 총알 이동
        self.bullet.move()
            
        # A 버튼이 떼어진 경우 총알 발사 상태를 재설정
        if not joystick.is_button_pressed(joystick.button_A):
            self.bullet.active = False


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
        # 총알 그리기
        self.bullet.draw(image, camera_position)


class LifeManager:
    def __init__(self, initial_lives):
        self.lives = initial_lives

    def decrease_life(self):
        self.lives -= 1

    def get_lives(self):
        return self.lives
    

class Bullet:
    def __init__(self, x, y, bullet_image_path):
        self.position = [x, y]
        self.bullet_image = Image.open(bullet_image_path).convert("RGBA")
        self.active = False  # 총알이 활성화되어 있는지 여부

    def move(self):
        if self.active:
            # 총알을 위로 이동 (필요에 따라 속도 조절)
            self.position[0] += 5

    def draw(self, image, camera_position):
        if self.active:
            bullet_draw_position = (
                self.position[0] - camera_position[0],
                self.position[1] - camera_position[1],
            )
            image.alpha_composite(self.bullet_image, bullet_draw_position)

    def check_collision(self, monster):
        # 몬스터와 총알의 충돌을 확인
        bullet_left = self.position[0]
        bullet_right = self.position[0] + self.bullet_image.width
        bullet_top = self.position[1]
        bullet_bottom = self.position[1] + self.bullet_image.height

        monster_left = monster.position[0]
        monster_right = monster.position[0] + monster.width
        monster_top = monster.position[1]
        monster_bottom = monster.position[1] + monster.height

        if (
            bullet_right >= monster_left
            and bullet_left <= monster_right
            and bullet_bottom >= monster_top
            and bullet_top <= monster_bottom
            ):
                return True
        return False

        # for monster in monsters:
        #     monster_left = monster.position[0]
        #     monster_right = monster.position[0] + monster.width
        #     monster_top = monster.position[1]
        #     monster_bottom = monster.position[1] + monster.height

        #     if (
        #         bullet_right >= monster_left
        #         and bullet_left <= monster_right
        #         and bullet_bottom >= monster_top
        #         and bullet_top <= monster_bottom
        #     ):
        #         return True
        # return False
    
class Monster:
    def __init__(self, x, y, width, height,image_path):
        self.position = [x, y]
        self.width = width
        self.height = height
        self.active = True  # 몬스터가 활성화되어 있는지 여부
        self.monster_image = Image.open(image_path).convert("RGBA")