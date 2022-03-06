"""Math library."""


class Vector2(object):
    """Math object, vector2."""

    def __init__(self, x=0, y=0):
        """Initialize the object."""
        self._x = x
        self._y = y
        self._xy = [x, y]

    @property
    def x(self):
        """Return x item."""
        return self._x

    @property
    def y(self):
        """Return y item."""
        return self._y

    @x.setter
    def x(self, value):
        """Set the x attribute."""
        self._x = value
        self._xy[0] = self._x

    @y.setter
    def y(self, value):
        """Set the y attribute."""
        self._y = value
        self._xy[1] = self._y

    def __str__(self):
        """Override the str."""
        return str(self._xy)

    def __add__(self, vector2):
        """Override the operator `+`."""
        assert isinstance(vector2, Vector2)
        return Vector2(self._x + vector2.x, self._y + vector2.y)

    def __sub__(self, vector2):
        """Override the operator `-`."""
        assert isinstance(vector2, Vector2)
        return Vector2(self._x - vector2.x, self._y - vector2.y)

    def __getitem__(self, item):
        """Override the operator index."""
        return self._xy[item]

    def __setitem__(self, key, value):
        """Override the operator index store."""
        self._xy[key] = value
        self._x = self._xy[0]
        self._y = self._xy[1]
