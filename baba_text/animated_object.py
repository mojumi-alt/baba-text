import pygame
from .constants import RESOURCE_DIR, MASK_COLOR
from glob import glob
import os
import random


class AnimatedObject:
    def __init__(
        self,
        name: str,
        box: pygame.Rect,
        foreground_color: pygame.Color,
        background_color: pygame.Color,
    ) -> None:
        self.__name = name
        self.__box = box
        self.__foreground_color = foreground_color
        self.__background_color = background_color

        self.__sprites = self.__load_images()

        if len(self.__sprites) == 0:
            raise FileNotFoundError(f"Did not find sprites for object: {name}")

        self.__current_animation_index = 0

    def advance_animation(self) -> None:
        offset = (
            random.randint(1, len(self.__sprites) - 1) if len(self.__sprites) > 2 else 1
        )
        self.__current_animation_index = (
            self.__current_animation_index + offset
        ) % len(self.__sprites)

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.__sprites[self.__current_animation_index], self.__box.topleft)

    def __load_images(self) -> list[pygame.Surface]:
        files = glob(os.path.join(RESOURCE_DIR, f"{self.__name}_*.png"))
        images = [pygame.image.load(f) for f in files]

        # Change the text and background color and
        # scale the image to the bounding box of the letter
        for i, image in enumerate(images):
            for y in range(image.get_height()):
                for x in range(image.get_width()):
                    if image.get_at((x, y)) == MASK_COLOR:
                        image.set_at((x, y), self.__background_color)
                    else:
                        image.set_at((x, y), self.__foreground_color)

            images[i] = pygame.transform.scale(image, self.__box.size)

        return images
