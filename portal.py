class Portal:
    def __init__(self, x, y, width, height):
        #포탈 초기화
        self.position = [x, y]
        self.width = width
        self.height = height

    def is_character_inside(self, character): #캐릭터가 포탈 안에 있는지 확인
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
        #캐릭터의 두 꼭지점이 포탈의 두 꼭지점 사이에 위치하는지 확인
        if (
            (portal_left_top[0] <= character_left_top[0] <= portal_right_bottom[0]
            and portal_left_top[1] <= character_left_top[1] <= portal_right_bottom[1])
            or
            (portal_left_top[0] <= character_right_bottom[0] <= portal_right_bottom[0]
            and portal_left_top[1] <= character_right_bottom[1] <= portal_right_bottom[1])
        ):
            return True
        return False