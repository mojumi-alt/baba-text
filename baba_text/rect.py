class Rect:
    def __init__(self, left: float, top: float, width: float, height: float) -> None:
        self.__left = round(left)
        self.__top = round(top)
        self.__width = round(width)
        self.__height = round(height)

    @property
    def left(self) -> int:
        return self.__left

    @property
    def right(self) -> int:
        return self.__left + self.__width

    @property
    def top(self) -> int:
        return self.__top

    @property
    def bottom(self) -> int:
        return self.__top + self.__height

    @property
    def width(self) -> int:
        return self.__width

    @property
    def height(self) -> int:
        return self.__height

    @property
    def size(self) -> tuple[int, int]:
        return (self.__width, self.__height)
