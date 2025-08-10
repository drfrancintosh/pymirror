class PMRect:
    def __init__(self, x0: int, y0: int, x1: int, y1: int):
        self._coords = [x0, y0, x1, y1]

    def __iter__(self):
        return iter(self._coords)

    def __getitem__(self, index):
        return self._coords[index]

    def __setitem__(self, index, value):
        self._coords[index] = value

    def __len__(self):
        return 4

    def __tuple__(self):
        return tuple(self._coords)

    @property
    def x0(self) -> int:
        return self._coords[0]

    @property
    def y0(self) -> int:
        return self._coords[1]

    @property
    def x1(self) -> int:
        return self._coords[2]

    @property
    def y1(self) -> int:
        return self._coords[3]

    @property
    def width(self) -> int:
        return self.x1 - self.x0

    @property
    def height(self) -> int:
        return self.y1 - self.y0
    
    @x0.setter
    def x0(self, value: int):
        self._coords[0] = value
        self._coords[2] = value + self.width

    @y0.setter
    def y0(self, value: int):
        self._coords[1] = value
        self._coords[3] = value + self.height

    @x1.setter
    def x1(self, value: int):
        self._coords[2] = value
        self._coords[0] = value - self.width

    @y1.setter
    def y1(self, value: int):
        self._coords[3] = value
        self._coords[1] = value - self.height

    @width.setter
    def width(self, value: int):
        if value < 0:
            raise ValueError("Width cannot be negative")
        self._coords[2] = self.x0 + value

    @height.setter
    def height(self, value: int):
        if value < 0:
            raise ValueError("Height cannot be negative")
        self._coords[3] = self.y0 + value

    def __add__(self, other: 'PMRect') -> 'PMRect':
        return PMRect(
            self.x0 + other.x0,
            self.y0 + other.y0,
            self.x1 + other.x1,
            self.y1 + other.y1
        )

    def move(self, x0: int, y0: int) -> 'PMRect':
        """Move the rectangle to (x0, y0)."""
        self[0] = x0
        self[1] = y0
        self[2] = x0 + self.width
        self[3] = y0 + self.height
        return self

    def rmove(self, dx: int, dy: int) -> 'PMRect':
        """Move the rectangle by dx and dy."""
        self[0] += dx
        self[1] += dy
        self[2] += dx
        self[3] += dy
        return self

    def __hash__(self):
        return hash((self.x0, self.y0, self.x1, self.y1))
    
    def __eq__(self, other: 'PMRect') -> bool:
        return (self.x0 == other.x0 and self.y0 == other.y0 and
                self.x1 == other.x1 and self.y1 == other.y1)

    def __str__(self):
        return f"PMRect({self.x0}, {self.y0}, {self.x1}, {self.y1})"
    
    def __repr__(self):
        return f"PMRect({self.x0}, {self.y0}, {self.x1}, {self.y1})"

    def contains(self, x: int, y: int) -> bool:
        return self.x0 <= x < self.x1 and self.y0 <= y < self.y1

    def intersects(self, other: 'PMRect') -> bool:
        return not (self.x1 <= other.x0 or self.x0 >= other.x1 or
                    self.y1 <= other.y0 or self.y0 >= other.y1)

    def to_tuple(self) -> tuple:
        return (self.x0, self.y0, self.x1, self.y1)

    @staticmethod
    def from_dims(dims: tuple) -> 'PMRect':
        """Create a PMRect from normalized dimensions."""
        if len(dims) != 4:
            raise ValueError("Dimensions must be a tuple of four elements (x0, y0, x1, y1).")
        rect = (
            int((dims[0] * 100) - 1),  # Assuming dims are normalized between 0 and 1
            int((dims[1] * 100) - 1),
            int((dims[2] * 100) - 1),
            int((dims[3] * 100) - 1)
        )
        return PMRect(*rect)

    @staticmethod
    def from_string(position: str) -> 'PMRect':
        """Create a PMRect from a position string."""
        x0, y0, x1, y1 = position.split(",")
        return PMRect(
            int(x0),
            int(y0),
            int(x1),
            int(y1)
        )