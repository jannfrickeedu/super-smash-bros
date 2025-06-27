import pygame
import math
from abc import ABC, abstractmethod

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
GRAVITY = 3
FRICTION_FLOOR = 3
FRICTION_AIR = 0.3


class Progressbar:
    def __init__(self, xpos, ypos, width, height, **kwargs):
        self.__width = width
        self.__height = height
        self.bg_color = kwargs.get("bg_color", (100, 100, 100))
        self.color = kwargs.get("color", (255, 255, 255))
        self.__percent = kwargs.get("percent", 0)
        self.__background = pygame.Rect((xpos, ypos), (width, height))
        self.__bar = pygame.Rect((xpos, ypos), (width, height))
        self.__bar.width = self.__width * self.__percent / 100

    #function for this because of performance issues
    def change_percent(self, new_percent):
        self.__percent = new_percent
        self.__bar.width = self.__width * self.__percent / 100

    def draw(self, screen):
        pygame.draw.rect(screen, self.bg_color, self.__background,)
        pygame.draw.rect(screen, self.color, self.__bar,)


class BodyPart:
    def __init__(self, rect, offset) -> None:
        self.rect = rect
        self.visible = False
        self.offset = offset

    def draw(self, screen, color):
        if self.visible:
            pygame.draw.rect(screen, color, self.rect)

    def update(self, anchor):
        self.rect.x = (anchor.x + self.offset.x)
        self.rect.y = (anchor.y + self.offset.y)


class Player:
    def __init__(self, x, y, color, left_key, right_key, jump_key, hit_key_right, hit_key_left):
        self.rect = pygame.Rect(x, y, 75, 150)
        self.pos = pygame.Vector2(x, y)
        self.initial_pos = pygame.Vector2(x, y)
        self.speed = 10
        self.max_velocity = pygame.Vector2(20, 20)
        self.velocity = pygame.Vector2(0, 0)
        self.color = color
        self.in_air = True
        self.health = 100
        self.lives = 3
        if self.initial_pos.x >= SCREEN_WIDTH / 2:
            health_bar = Progressbar(x - 100, 30, 200, 30, percent=100)
        else:
            health_bar = Progressbar(x, 30, 200, 30, percent=100)
        self.gui = [health_bar]
        hand_right = BodyPart(
            pygame.Rect(0, 0, 80, 20),
            pygame.Vector2(self.rect.width, self.rect.height // 2 - 5)
        )
        hand_left = BodyPart(
            pygame.Rect(0, 0, 80, 20),
            pygame.Vector2(-80, self.rect.height // 2 - 5)
        )
        self.body_parts = [hand_left, hand_right]
        self.left_key = left_key
        self.right_key = right_key
        self.jump_key = jump_key
        self.hit_key_right = hit_key_right
        self.hit_key_left = hit_key_left

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

        for part in self.body_parts:
            part.draw(screen, self.color)

        for item in self.gui:
            item.draw(screen)

    def update(self, tiles):
        self.apply_gravity()
        self.apply_friction()

        #max speed gets smoothly slowed and not clamped
        if abs(self.velocity.x) > self.max_velocity.x:
            self.velocity.x = math.copysign(self.max_velocity.x, self.velocity.x)

        self.pos.y += self.velocity.y
        self.pos.x += self.velocity.x

        for part in self.body_parts:
            part.update(self.pos)

        self.check_tile_collsions(tiles)
        self.check_alive()

    def check_alive(self):
        if self.health <= 0:
            self.reset()
            return
        
        elif self.pos.y > 1000:
            self.reset()
            return

    def reset(self):
        self.pos.x = self.initial_pos.x
        self.pos.y = self.initial_pos.y
        self.velocity = pygame.Vector2(0,0)
        self.health = 100
        self.gui[0].change_percent(100)
        self.lives -= 1

    def apply_gravity(self):
        if self.in_air:
            self.velocity.y += GRAVITY
            if self.velocity.y >= self.max_velocity.y:
                self.max_velocity.y

    def apply_friction(self):
        if self.in_air:
            if self.velocity.x > 0:
                self.velocity.x = max(0, self.velocity.x - FRICTION_AIR)
            elif self.velocity.x < 0:
                self.velocity.x = min(0, self.velocity.x + FRICTION_AIR)

        elif not self.in_air and not self.velocity.x == 0:
            if self.velocity.x > 0:
                self.velocity.x = max(0, self.velocity.x - FRICTION_FLOOR)
            elif self.velocity.x < 0:
                self.velocity.x = min(0, self.velocity.x + FRICTION_FLOOR)

    def check_tile_collsions(self, tiles):
        hit_tiles = self.rect.collidelistall(tiles)
        if hit_tiles:
            for i in hit_tiles:
                tile = tiles[i]
                if self.velocity.y > 0 and self.rect.bottom <= tile.top + self.velocity.y:
                    self.pos.y = tile.top - 149
                    self.velocity.y = 0
                    self.in_air = False
        else:
            self.in_air = True

        self.rect.x = round(self.pos.x)
        self.rect.y = round(self.pos.y)

    def move(self, direction):
        if not self.in_air:
            self.velocity.x += direction * self.speed

    def check_input(self, keys, players):
        enemies = [p for p in players if p is not self]

        if keys[self.left_key]:
            self.move(-1)
        if keys[self.right_key]:
            self.move(1)
        if not self.in_air and keys[self.jump_key]:
            self.jump()
        if keys[self.hit_key_left]:
            self.punch("left", enemies)
            keys[self.hit_key_left] = False
        if keys[self.hit_key_right]:
            self.punch("right", enemies)
            keys[self.hit_key_right] = False

    def jump(self):
        self.velocity.y = -40
        self.in_air = True

    def punch(self, direction, enemies):
        punch_velocity = 0
        if direction == "left":
            self.body_parts[0].visible = not self.body_parts[0].visible
            collisions = self.body_parts[0].rect.collidelistall(enemies)
            punch_velocity -= 40
        elif direction == "right":
            self.body_parts[1].visible = not self.body_parts[1].visible
            collisions = self.body_parts[1].rect.collidelistall(enemies)
            punch_velocity += 40
        else:
            raise ValueError("invalid direction")

        if collisions:
            for i in collisions:
                enemies[i].hit(punch_velocity)

    def hit(self, punch_velocity):
        self.velocity.x += punch_velocity
        self.velocity.y -= 10
        self.health -= 10
        self.gui[0].change_percent(self.health)


class SceneManager():
    def __init__(self, scenes) -> None:
        self.scenes = scenes
        self.scene_index = 0
        self.current_scene = scenes[0]
        self.current_scene.active = True

    def validate_scene(self):
        if self.current_scene.active:
            return
        else:
            self.scene_index += 1
            self.current_scene = self.scenes[self.scene_index]
            self.current_scene.active = True

    def check_input(self, keys):
        self.current_scene.check_input(keys)

    def update(self):
        self.validate_scene()
        self.current_scene.update()

    def draw(self, screen):
        self.current_scene.draw(screen)



class Scene(ABC):
    def __init__(self) -> None:
        self.clock = pygame.time.Clock()
        self.active = False

    @abstractmethod
    def check_input(self, keys):
        pass

    @abstractmethod
    def update(self):
        self.clock.tick(60)

    @abstractmethod
    def draw(self, screen):
        pass


class Level(Scene):
    def __init__(self, tilemap) -> None:
        super().__init__()
        player1 = Player(100, 100, "red", pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_e, pygame.K_q)
        player2 = Player(SCREEN_WIDTH - 175, 100, "green", pygame.K_j, pygame.K_l, pygame.K_i, pygame.K_o, pygame.K_u)
        self.players = [player1, player2]
        self.tiles = generate_tiles(tilemap)
        self.background = pygame.image.load('background.jpg')
        
    def check_input(self, keys):
         for player in self.players:
            player.check_input(keys, self.players)

    def update(self):
        super().update()
        for player in self.players:
            player.update(self.tiles)
            if player.lives < 0:
                self.active = False

    def draw(self, screen):
        screen.blit(self.background, (0, 0))
        for player in self.players:
            player.draw(screen)

        for tile in self.tiles:
            pygame.draw.rect(screen, (255, 255, 255), tile)


class Menu(Scene):
    def __init__(self) -> None:
        super().__init__()
    
    def check_input(self, keys):
        return super().check_input(keys)

    def update(self):
        return super().update()

    def draw(self, screen):
        screen.fill("blue")


class Game:
    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.keys = [False] * 2048
        # Tilemap setup
        tilemap = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]

        level = Level(tilemap)
        menu = Menu()

        scenes = [level, menu]

        self.scene_manager = SceneManager(scenes)


    def poll_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                if event.key <= 2048:
                    self.keys[event.key] = not self.keys[event.key]
        self.scene_manager.check_input(self.keys)

    def update(self):
        self.scene_manager.update()

    def draw(self):
        self.scene_manager.draw(self.screen)
        pygame.display.flip()

    def start(self):
        while self.running:
            self.poll_events()
            self.update()
            self.draw()


# Tilemap and tiles
def generate_tiles(tilemap):
    result = []
    tile_width = SCREEN_WIDTH / 16
    tile_height = SCREEN_HEIGHT / 9
    for row_idx, row in enumerate(tilemap):
        for col_idx, tile in enumerate(row):
            if tile == 1:
                rect = pygame.Rect(
                    col_idx * tile_width,
                    row_idx * tile_height,
                    tile_width,
                    tile_height
                )
                result.append(rect)
    return result



# Initialization
pygame.init()
game = Game()
game.start()

pygame.quit()
