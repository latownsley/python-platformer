# Platformer Game
# Leela Townsley
# 8/15/2023
#
import random
import sys
import time

import constant
import pygame
from pygame.locals import *


class Player(pygame.sprite.Sprite):
    def __init__(self, color):
        super().__init__()

        # look
        self._display = pygame.Surface((30, 30))
        self._display.fill(color)
        self.rect = self._display.get_rect(center=(10, 420))

        # player position
        self._position = pygame.math.Vector2((10, 385))
        self._velocity = pygame.math.Vector2(0, 0)
        self._accel = pygame.math.Vector2(0, 0)
        self._is_jumping = False

        # GAME
        self._score = 0

    def get_rect_y(self):
        return self.rect.y

    def get_score(self):
        return self._score

    def get_display(self):
        return self._display

    def get_rect(self):
        return self.rect

    def get_y_velocity(self):
        return self._velocity.y

    def move(self):
        self._accel = pygame.math.Vector2(0, 0.5)

        pressed = pygame.key.get_pressed()

        # horizontal movement
        if pressed[K_LEFT]:
            self._accel.x = -constant.ACC
        if pressed[K_RIGHT]:
            self._accel.x = constant.ACC

        self._accel.x += self._velocity.x * constant.FRIC
        self._velocity += self._accel
        self._position += self._velocity + constant.ACC * self._accel

        # allow screen warping
        if self._position.x > constant.WIDTH:
            self._position.x = 0
        if self._position.x < 0:
            self._position.x = constant.WIDTH

        self.rect.midbottom = self._position

    def update(self, player, objects):
        # collisions
        collision = pygame.sprite.spritecollide(player, objects, False)
        if collision:
            if self._velocity.y > 0:
                self._velocity.y = 0
                self._position.y = collision[0].rect.top + 1
                self._is_jumping = False
                if collision[0].get_point():
                    self._score += 1
                    collision[0].point_taken()
                if collision[0].get_speed() != 0:
                    self._velocity.x = collision[0].get_speed()

        # jumping - only 1 bouce per collision allowed
        pressed = pygame.key.get_pressed()
        if pressed[K_SPACE]:
            if collision and not self._is_jumping:
                self._velocity.y = -12
                self._velocity.x = 0

        # other things player needs to update

    def jump_deceleration(self):
        if self._is_jumping:
            if self._velocity.y < -3:
                self._velocity.y = -3


'''
class SecondPlayer(Player):
    def __init__(self, color):
        super().__init__(color)

    def move(self):
        self._accel = pygame.math.Vector2(0, 0.5)

        pressed = pygame.key.get_pressed()

        # horizontal movement
        if pressed[K_a]:
            self._accel.x = -constant.ACC
        if pressed[K_d]:
            self._accel.x = constant.ACC

        self._accel.x += self._velocity.x * constant.FRIC
        self._velocity += self._accel
        self._position += self._velocity + constant.ACC * self._accel

        # allow screen warping
        if self._position.x > constant.WIDTH:
            self._position.x = 0
        if self._position.x < 0:
            self._position.x = constant.WIDTH

        self.rect.midbottom = self._position

    def update(self, player, objects):
        # collisions
        collision = pygame.sprite.spritecollide(player, objects, False)
        if collision:
            if self._velocity.y > 0:
                self._velocity.y = 0
                self._position.y = collision[0].rect.top + 1
                self._is_jumping = False
                if collision[0].get_point():
                    self._score += 1
                    collision[0].point_taken()

        # jumping - only 1 bouce per collision allowed
        pressed = pygame.key.get_pressed()
        if pressed[K_w]:
            if collision and not self._is_jumping:
                self._velocity.y = -12
'''


class Platform(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        red = (255, 0, 0)
        self._display = pygame.Surface((random.randint(50, 100), 12))
        self._display.fill(red)
        self.rect = self._display.get_rect(center=(random.randint(0, constant.WIDTH - 10),
                                                   random.randint(0, constant.HEIGHT - 30)))
        self._point = True
        self._speed = random.randint(-1, 1)

    def get_speed(self):
        return self._speed

    def move(self):
        self.rect.move_ip(self._speed, 0)
        if self._speed > 0 and self.rect.left > constant.WIDTH:
            self.rect.right = 0
        if self._speed < 0 and self.rect.right < 0:
            self.rect.left = constant.WIDTH

    def get_point(self):
        return self._point

    # when a platform has been touched, it no longer gives points
    def point_taken(self):
        self._point = False

    def get_display(self):
        return self._display

    def get_rect(self):
        return self.rect


class GroundPlatform(Platform):
    def __init__(self):
        super().__init__()
        red = (255, 0, 0)
        self._display = pygame.Surface((constant.WIDTH, 20))
        self._display.fill(red)
        self.rect = self._display.get_rect(center=(constant.WIDTH / 2, constant.HEIGHT - 10))
        self._point = False
        self._speed = 0


class Renderer:
    def __init__(self):
        pygame.init()

        self.vec2 = pygame.math.Vector2

        # colors
        yellow = (255, 255, 0)
        turquoise = (64, 224, 208)

        # Game items
        self._clock = pygame.time.Clock()
        self._FPS = 60
        self._ACC = 0.5
        self._FRIC = -0.12
        self._quit = False
        self._screen = pygame.display.set_mode((constant.WIDTH, constant.HEIGHT))

        pygame.display.set_caption("Climb the Sky: A Platformer")
        self._ground_platform = GroundPlatform()
        self._player_one = Player(turquoise)

        self._game_objects = pygame.sprite.Group()
        self._game_objects.add(self._ground_platform)
        self._game_objects.add(self._player_one)

        self._platforms = pygame.sprite.Group()
        self._platforms.add(self._ground_platform)

    def plat_gen(self):
        while len(self._platforms) < 7:
            width = random.randrange(50, 100)

            p = Platform()
            p.rect.center = (random.randrange(0, constant.WIDTH - width),
                             random.randrange(-50, 0))

            while not self.plat_check(p, self._platforms):

                p = Platform()
                p.rect.center = (random.randrange(0, constant.WIDTH - width),
                                 random.randrange(-50, 0))

            self._platforms.add(p)
            self._game_objects.add(p)

    # make sure the platforms are an appropriate height and distance from each other
    # False if the platforms are too close / too far and return True if they're ok
    @staticmethod
    def plat_check(platform, all_plats):

        # check if any collisions with the group
        if pygame.sprite.spritecollideany(platform, all_plats):
            return False
        else:
            for plat in all_plats:
                if (abs(platform.rect.top - plat.rect.bottom) < 20) and (
                        abs(platform.rect.bottom - plat.rect.top) < 20):
                    return False

                if abs(platform.rect.top - plat.rect.top) == 0:
                    return False

        return True

    def game_loop(self):
        # colors
        black = (0, 0, 0)
        red = (255, 0, 0)
        green = (123, 255, 0)
        yellow = (255, 255, 0)  # player one color
        turquoise = (64, 224, 208)  # player two color

        # initial random platform generation
        for num in range(random.randint(5, 6)):
            platform = Platform()
            self._platforms.add(platform)
            self._game_objects.add(platform)

        # main game loop
        while not self._quit:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self._quit = True
                    pygame.quit()
                    sys.exit()

            # refresh screen each iteration
            self._screen.fill(black)

            # player one score
            font = pygame.font.SysFont("Verdana", 20)
            g = font.render(str(self._player_one.get_score()), True, yellow)
            score_len = len(str(self._player_one.get_score()))  # adjust position on screen for size of score
            if score_len == 1:
                self._screen.blit(g, (constant.WIDTH - 20, 10))
            elif score_len == 2:
                self._screen.blit(g, (constant.WIDTH - 30, 10))
            else:
                self._screen.blit(g, (constant.WIDTH - 40, 10))

            for item in self._game_objects:
                self._screen.blit(item.get_display(), item.get_rect())

            self._player_one.update(self._player_one, self._platforms)
            self._player_one.move()
            self._player_one.jump_deceleration()

            # adjust the screen for player position (rewrite so doesn't access private variables)
            if self._player_one.rect.top <= constant.HEIGHT / 3:
                self._player_one._position.y += abs(self._player_one._velocity.y)
                for plat in self._platforms:
                    plat.rect.y += abs(self._player_one._velocity.y)
                    if plat.rect.top >= constant.HEIGHT:
                        plat.kill()

            # move platforms
            for plat in self._platforms:
                plat.move()

            # platform generation
            self.plat_gen()

            # game over condition
            if self._player_one.get_rect().top > constant.HEIGHT:
                for obj in self._game_objects:
                    obj.kill()
                    self._screen.fill(red)
                    font = pygame.font.Font('freesansbold.ttf', 22)
                    text = font.render('GAME OVER', True, green, red)
                    score_text = font.render(str(self._player_one.get_score()), True, yellow)
                    self._screen.blit(text, (constant.WIDTH / 15, constant.HEIGHT / 3))
                    self._screen.blit(score_text, (constant.WIDTH / 15, constant.HEIGHT / 5))

                    time.sleep(1)
                    pygame.display.update()
                    self._quit = True

            pygame.display.update()
            self._clock.tick(self._FPS)

        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    game = Renderer()
    game.game_loop()
