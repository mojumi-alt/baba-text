class Rect:
    def __init__(self, left: float, top: float, width: float, height: float) -> None:
        self.__left = round(left)
        self.__top = round(top)
        self.__width = round(width)
        self.__height = round(height)

    @property
    def left(self) -> int:
        return self.__left

    @left.setter
    def left(self, value: float) -> None:
        self.__left = round(value)

    @property
    def right(self) -> int:
        return self.__left + self.__width

    @property
    def top(self) -> int:
        return self.__top

    @top.setter
    def top(self, value: float) -> None:
        self.__top = round(value)

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
