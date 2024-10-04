from dataclasses import dataclass
import numpy as np
from .color import Color


@dataclass
class MaskedImage:
    resource_name: str
    resource_uri: str
    image: np.ndarray
    foreground_mask: np.ndarray
    background_mask: np.ndarray

    def set_foreground_color(self, color: Color) -> None:
        self.image[self.foreground_mask] = color

    def set_background_color(self, color: Color) -> None:
        self.image[self.background_mask] = color
