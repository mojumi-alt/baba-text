import pygame

MASK_COLOR = pygame.Color(255, 255, 255)
SPRITE_SIZE = 100
BACKGROUND_COLOR = pygame.Color(49, 51, 56)
ANIMATION_FPS = 4
MAX_LETTER_HEIGHT = 55
LETTER_WIDTH_TO_HEIGHT_RATIO = 0.8
RESOURCE_DIR = "./resources"
ANIMATION_FRAME_COUNT = 6
COLOR_WHITE = pygame.Color(255, 255, 255)
COLOR_PALETTE = {
    "gray": pygame.Color(128, 128, 128),
    "yellow": pygame.Color(255, 255, 60),
    "orange": pygame.Color(250, 120, 60),
    "dark_red": pygame.Color(255, 60, 60),
    "red": pygame.Color(255, 50, 120),
    "pale_red": pygame.Color(255, 120, 120),
    "dark_purple": pygame.Color(160, 20, 160),
    "purple": pygame.Color(120, 120, 255),
    "dark_blue": pygame.Color(20, 20, 200),
    "blue": pygame.Color(60, 60, 255),
    "light_blue": pygame.Color(60, 160, 255),
    "pink": pygame.Color(255, 120, 255),
    "dark_pink": pygame.Color(255, 60, 255),
    "dark_green": pygame.Color(60, 160, 60),
    "green": pygame.Color(60, 255, 60),
    "light_green": pygame.Color(120, 255, 120),
    "brown": pygame.Color(150, 100, 70),
    "black": pygame.Color(0, 0, 0),
}

KNOWN_WORDS_TO_COLOR = {
    "baba": COLOR_PALETTE["red"],
    "You": COLOR_PALETTE["red"],
    "is": COLOR_WHITE,
    "and": COLOR_WHITE,
    "not": COLOR_PALETTE["red"],
    "or": COLOR_WHITE,
    "on": COLOR_WHITE,
    "can": COLOR_WHITE,
    "the": COLOR_WHITE,
    "has": COLOR_WHITE,
    "wall": COLOR_PALETTE["gray"],
    "Float": COLOR_PALETTE["light_blue"],
    "flag": COLOR_PALETTE["yellow"],
    "Blue": COLOR_PALETTE["blue"],
    "Red": COLOR_PALETTE["red"],
    "Green": COLOR_PALETTE["green"],
    "Yellow": COLOR_PALETTE["yellow"],
    "Pink": COLOR_PALETTE["pink"],
    "Orange": COLOR_PALETTE["orange"],
    "Purple": COLOR_PALETTE["purple"],
    "White": COLOR_WHITE,
    "Black": COLOR_PALETTE["black"],
    "blue": COLOR_PALETTE["blue"],
    "red": COLOR_PALETTE["red"],
    "green": COLOR_PALETTE["green"],
    "yellow": COLOR_PALETTE["yellow"],
    "pink": COLOR_PALETTE["pink"],
    "orange": COLOR_PALETTE["orange"],
    "purple": COLOR_PALETTE["purple"],
    "white": COLOR_WHITE,
    "black": COLOR_PALETTE["black"],
}
