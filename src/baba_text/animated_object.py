from .constants import RESOURCE_DIR, MASK_COLOR
from glob import glob
import os
import random
from .rect import Rect
from .color import Color
import numpy as np
from PIL import Image
from .constants import LETTER_SAMPLE_MODE
from .masked_image import MaskedImage


class AnimatedObject:
    def __init__(
        self,
        name: str,
        box: Rect,
        foreground_color: Color,
        background_color: Color,
    ) -> None:
        self.__name = name
        self.__box = box
        self.__foreground_color = foreground_color
        self.__background_color = background_color

        self.__sprites = self.__load_images()

        if len(self.__sprites) == 0:
            raise FileNotFoundError(f"Did not find sprites for object: {name}")

        self.__current_animation_index = 0

    def advance_animation(self, override_index: int | None = None) -> int:
        offset = (
            random.randint(1, len(self.__sprites) - 1) if len(self.__sprites) > 2 else 1
        )
        self.__current_animation_index = (
            (
                self.__current_animation_index
                if override_index is None
                else override_index
            )
            + offset
        ) % len(self.__sprites)
        return self.__current_animation_index

    def draw(self, surface: np.ndarray) -> None:
        # Careful: Numpy is column major (we need to flip x and y)
        surface[
            self.__box.top : self.__box.bottom, self.__box.left : self.__box.right
        ] = self.__sprites[self.__current_animation_index].image

    @property
    def location(self) -> tuple[int, int]:
        return (self.__box.left, self.__box.top)

    @location.setter
    def location(self, value: tuple[int, int]) -> None:
        self.__box.left = value[0]
        self.__box.top = value[1]

    @property
    def background_color(self) -> Color:
        return self.__background_color

    @background_color.setter
    def background_color(self, value: Color) -> None:
        for sprite in self.__sprites:
            sprite.set_background_color(value)
        self.__background_color = value

    @property
    def foreground_color(self) -> Color:
        return self.foreground_color

    @foreground_color.setter
    def foreground_color(self, value: Color) -> None:
        for sprite in self.__sprites:
            sprite.set_foreground_color(value)
        self.__foreground_color = value

    def __load_images(self) -> list[MaskedImage]:
        files = glob(os.path.join(RESOURCE_DIR, f"{self.__name}_*.png"))
        images = []

        for file in files:
            image = np.array(
                Image.open(file)
                .convert("RGBA")
                .resize(self.__box.size, resample=LETTER_SAMPLE_MODE)
            )
            foreground_mask = np.any(image != MASK_COLOR, axis=2)
            background_mask = np.all(image == MASK_COLOR, axis=2)
            image[foreground_mask] = self.__foreground_color
            image[background_mask] = self.__background_color
            images.append(
                MaskedImage(self.__name, file, image, foreground_mask, background_mask)
            )

        return images
