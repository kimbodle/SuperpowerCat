import time
from PIL import Image, ImageDraw, ImageFont


   
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



def stage1(joystick, my_character, platforms, background_image, obstacles, portal, background_images, skills):
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
            draw.text((170, 10), f"Lives: {my_character.life_manager.get_lives()}", fill="red", font=font)

        # 캐릭터의 목숨이 0 이하인 경우 게임 종료
        if my_character.life_manager.get_lives() <= 0:
            print("Game over!") # 이걸 이제 나중에 게임 오버 인트로 함수 부르면 될듯
            break
        
        if portal.is_character_inside(my_character) and joystick.is_button_pressed(joystick.button_U):
            print("포탈")
            time.sleep(1)
            # 입력 패턴 정의
            pattern = ['U', 'D', 'R', 'R', 'U','L','L']


            # 스테이지2 시작
            monster_stage1(joystick, background_images[1], pattern, skills)

            # 1초 대기
            time.sleep(1)

            break
        

        my_character.draw(image, camera_position)

        # RGB 디스플레이에 이미지 표시
        joystick.disp.image(image.convert("RGBA"))
        
        

def monster_stage1(joystick, background_image, pattern, skills):
    # 입력 패턴 인덱스 초기화
    pattern_index = 0

    # 패턴 입력 결과를 저장할 리스트 초기화
    pattern_result = []

    # 몬스터 스테이지1 시작
    while True:
        # 조이스틱 입력 확인
        if joystick.is_button_pressed(joystick.button_U):
            input = 'U'
        elif joystick.is_button_pressed(joystick.button_D):
            input = 'D'
        elif joystick.is_button_pressed(joystick.button_L):
            input = 'L'
        elif joystick.is_button_pressed(joystick.button_R):
            input = 'R'
        else:
            input = None

        # 입력이 있으면 패턴 결과를 업데이트
        if input is not None:
            # 입력이 패턴과 일치하면 'O', 아니면 'X'를 결과에 추가
            if input == pattern[pattern_index]:
                pattern_result.append('O')
            else:
                pattern_result.append('X')

            # 패턴 인덱스를 증가
            pattern_index += 1

        # 이미지에 패턴 결과를 그리기
        image = Image.new("RGBA", (joystick.disp.width, joystick.disp.height))
        image.paste(background_image)
        draw = ImageDraw.Draw(image)
        draw.text((10, 10), ' '.join(pattern_result), fill="white")

        # RGB 디스플레이에 이미지 표시
        joystick.disp.image(image.convert("RGBA"))

        # 디바운싱
        time.sleep(0.2)

        # 모든 패턴을 입력했으면
        if pattern_index >= len(pattern):
            # 결과 이미지를 로드: 패턴 결과에 'X'가 하나라도 있으면 'error.png', 아니면 'skill1.png'

            result_image = skills[1] if 'X' in pattern_result else skills[0]
            
            # 결과 이미지 표시
            joystick.disp.image(result_image)

            # 1초 대기
            time.sleep(1)

            # 패턴 결과에 'X'가 없으면 몬스터 스테이지1 종료
            if 'X' not in pattern_result:
                joystick.disp.image(skills[2])
                break

            # 패턴 결과를 초기화하고 다시 입력 받기
            pattern_result.clear()
            pattern_index = 0



def stage2(joystick, my_character, platforms, background_image, obstacles, portal, background_images, skills):
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
        draw.text((10, 10), f"Stage 2", fill=(153,255,51), font=font)
        
        # 충돌 확인 및 목숨 감소
        previous_lives = my_character.life_manager.get_lives()  # 충돌 전 캐릭터의 목숨
        my_character.check_collision(obstacles)
        
        if my_character.life_manager.get_lives() < previous_lives:
            draw.text((170, 10), f"Lives: {my_character.life_manager.get_lives()}", fill="red", font=font)

        # 캐릭터의 목숨이 0 이하인 경우 게임 종료
        if my_character.life_manager.get_lives() <= 0:
            print("Game over!") # 이걸 이제 나중에 게임 오버 인트로 함수 부르면 될듯
            break
        
        if portal.is_character_inside(my_character) and joystick.is_button_pressed(joystick.button_U):
            print("포탈")
            time.sleep(1)
            # 입력 패턴 정의
            pattern = ['D', 'L', 'R', 'A', 'U','R','A']

            # 스테이지2 시작
            monster_stage2(joystick, background_images[3], pattern, skills)

            # 1초 대기
            time.sleep(1)

            break
        

        my_character.draw(image, camera_position)

        # RGB 디스플레이에 이미지 표시
        joystick.disp.image(image.convert("RGBA"))
        
def monster_stage2(joystick, background_image, pattern, skills):
    # 입력 패턴 인덱스 초기화
    pattern_index = 0

    # 패턴 입력 결과를 저장할 리스트 초기화
    pattern_result = []

    # 몬스터 스테이지1 시작
    while True:
        # 조이스틱 입력 확인
        if joystick.is_button_pressed(joystick.button_U):
            input = 'U'
        elif joystick.is_button_pressed(joystick.button_D):
            input = 'D'
        elif joystick.is_button_pressed(joystick.button_L):
            input = 'L'
        elif joystick.is_button_pressed(joystick.button_R):
            input = 'R'
        elif joystick.is_button_pressed(joystick.button_A):
            input = 'A'
        else:
            input = None

        # 입력이 있으면 패턴 결과를 업데이트
        if input is not None:
            # 입력이 패턴과 일치하면 'O', 아니면 'X'를 결과에 추가
            if input == pattern[pattern_index]:
                pattern_result.append('O')
            else:
                pattern_result.append('X')

            # 패턴 인덱스를 증가
            pattern_index += 1

        # 이미지에 패턴 결과를 그리기
        image = Image.new("RGBA", (joystick.disp.width, joystick.disp.height))
        image.paste(background_image)
        draw = ImageDraw.Draw(image)
        draw.text((10, 10), ' '.join(pattern_result), fill="white")

        # RGB 디스플레이에 이미지 표시
        joystick.disp.image(image.convert("RGBA"))

        # 디바운싱
        time.sleep(0.2)

        # 모든 패턴을 입력했으면
        if pattern_index >= len(pattern):
            # 결과 이미지를 로드: 패턴 결과에 'X'가 하나라도 있으면 'error.png', 아니면 'skill1.png'

            result_image = skills[4] if 'X' in pattern_result else skills[3]
            
            # 결과 이미지 표시
            joystick.disp.image(result_image)

            # 1초 대기
            time.sleep(1)

            # 패턴 결과에 'X'가 없으면 몬스터 스테이지2 종료
            if 'X' not in pattern_result:
                joystick.disp.image(skills[5])
                break

            # 패턴 결과를 초기화하고 다시 입력 받기
            pattern_result.clear()
            pattern_index = 0