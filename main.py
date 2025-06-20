import pygame
import math

GRAVITY = 3
FRICTION_FLOOR = 10
FRICTION_AIR = 0.3

#this is a test
class Player:
    def __init__(self, x, y, color, left_key, right_key, jump_key, hit_key_right, hit_key_left):
        self.rect = pygame.Rect(x, y, 50, 100)
        self.speed = 15
        self.max_vel_y = 20
        self.max_vel_x = 15
        self.vy = 0
        self.vx = 0
        self.color = color
        self.in_air = True
        self.punching_left = False
        self.punching_right = False
        self.left_key = left_key
        self.right_key = right_key
        self.jump_key = jump_key
        self.hit_key_right = hit_key_right
        self.hit_key_left = hit_key_left

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        if self.punching_right:
            hand_right = pygame.Rect(self.rect.midright, (40, 10))
            pygame.draw.rect(screen, self.color, hand_right)
        if self.punching_left:
            hand_left = pygame.Rect((self.rect.left - 40,  self.rect.centery), (40, 10))
            pygame.draw.rect(screen, self.color, hand_left)

    def update(self, tiles):
        if self.in_air:
            self.vy += GRAVITY
            if self.vy >= self.max_vel_y:
                self.max_vel_y

            if self.vx > 0:
                self.vx = max(0, self.vx - FRICTION_AIR)
            elif self.vx < 0:
                self.vx = min(0, self.vx + FRICTION_AIR)

        elif not self.in_air and not self.vx == 0:
            if self.vx > 0:
                self.vx = max(0, self.vx - FRICTION_FLOOR)
            elif self.vx < 0:
                self.vx = min(0, self.vx + FRICTION_FLOOR)

        # ist max geschwindigkeit erreicht
        if abs(self.vx) > self.max_vel_x:
            self.vx = math.copysign(self.max_vel_x, self.vx)

        self.rect.y += self.vy
        self.rect.x += self.vx

        self.rect.y -= 1
        # boden collision
        if self.rect.collidelistall(tiles):
            for i in self.rect.collidelistall(tiles):
                tile = tiles[i]
                if self.vy > 0:
                    if tile.top < self.rect.bottom < tile.bottom:
                        self.in_air = False
                        self.vy = 0
                        self.rect.bottom = tile.top
        else:
            self.in_air = True
        self.rect.y += 1

    def move(self, direction):
        if not self.in_air:
            self.vx += direction * self.speed

    def check_input(self, keys):
        if keys[self.left_key]:
            self.move(-1)
        if keys[self.right_key]:
            self.move(1)
        if not self.in_air and keys[self.jump_key]:
            self.jump()
        if keys[self.hit_key_left]:
            self.hit("left")
        if keys[self.hit_key_right]:
            self.hit("right")

    def jump(self):
        self.vy = -40
        self.in_air = True

    def hit(self, direction):
            if direction == "left":
                self.punching_left = not self.punching_left
            if direction == "right":
                self.punching_right = not self.punching_right


# Initialization
pygame.init()
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True

# Player setup
player1 = Player(100, 100, "red", pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_e, pygame.K_q)
player2 = Player(800, 100, "green", pygame.K_j, pygame.K_l, pygame.K_i, pygame.K_o, pygame.K_u)
players = [player1, player2]

# Tilemap and tiles
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

tiles = []
tile_width = SCREEN_WIDTH / 16
tile_height = SCREEN_HEIGHT / 9


def generate_tiles(tiles):
    for row_idx, row in enumerate(tilemap):
        for col_idx, tile in enumerate(row):
            if tile == 1:
                rect = pygame.Rect(
                    col_idx * tile_width,
                    row_idx * tile_height,
                    tile_width,
                    tile_height
                )
                tiles.append(rect)


generate_tiles(tiles)

# Main game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    for player in players:
        player.check_input(keys)
        player.update(tiles)

    screen.fill((0, 0, 0))

    # Draw player
    for player in players:
        player.draw(screen)

    # Draw tiles
    for tile in tiles:
        pygame.draw.rect(screen, (255, 255, 255), tile)


    pygame.display.flip()
    clock.tick(60)

pygame.quit()
