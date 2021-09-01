"""Base generator for Diabolic script images"""

from base64 import b64encode
from io import BytesIO
from os.path import dirname, join, realpath
from re import MULTILINE, finditer, sub
from typing import List, Optional, Tuple

from PIL import Image


GLYPH = 210
DIACRITIC = 30


def clean_up_string(string: str) -> str:
    """Cleans up string as Diabolic likes it

    Args:
        string (str): The input text

    Returns:
        str: The formatted text
    """
    string = string.lower().strip()

    string = sub(
        pattern=r"([bcdfghjklmnpqrstvwxyz])\1+",
        repl=r"\1&",
        string=string,
        flags=MULTILINE,
    )

    devoc = sub(
        pattern=r"[aeiouh&]+",
        repl="",
        string=string,
        flags=MULTILINE,
    )

    if len(devoc) == 0:
        string = sub(
            pattern=r"([aeiouh&]{1,3})([aeiouh&]{1,3})",
            repl=r"\1_\2",
            string=string,
            flags=MULTILINE,
        )

    string = sub(
        pattern=r"(\s)([aeiouh&])(\s)",
        repl=r"\1\2_\3",
        string=string,
        flags=MULTILINE,
    )

    string = sub(
        pattern=r"([.,:?!])(\s?)",
        repl=r" \1\2",
        string=string,
        flags=MULTILINE,
    )

    string = sub(
        pattern=r"\s+",
        repl=" ",
        string=string,
        flags=MULTILINE,
    )

    return string.strip()


def read_symbol_image(name: str, symbols: dict[str, str]) -> Image:
    """Reads an image from the assets folder

    Args:
        name (str): The filename of the symbol
        symbols (dict[str, str]): Optional transformations from symbol to text

    Returns:
        Image: The image for the specified symbol
    """
    name = symbols[name] if len(symbols) and name in symbols.keys() else name
    path = realpath(join(dirname(__file__), "..", "assets"))

    return Image.open(join(path, name + ".png"))


def paste_transparent_image(
    base: Image,
    layer: Image,
    box: Tuple[int, int] = (0, 0),
) -> Image:
    """Overlays the `layer` image on the `base` image, at coordinates `box`

    Args:
        base (Image): The background image
        layer (Image): The overlayed image
        box (Tuple[int, int], optional): The top-left corner of the layer. Defaults to (0, 0).

    Returns:
        Image: The combined images
    """

    overlay = Image.new(mode="RGBA", size=base.size)
    overlay.paste(im=layer, box=box, mask=layer)

    return Image.alpha_composite(base, overlay)


class Diacritic:
    """A diacritic symbol for a Glyph"""

    def __init__(
        self,
        symbol: str,
        numerics: dict[str, int],
        solo: bool,
    ) -> None:
        """Generates a diacritic symbol

        Args:
            symbol (str): The symbol letter
            numerics (dict[str, int]): Dictionary of angle, index and length
            solo (bool): Following glyph has diacritics?
        """
        self.symbol = symbol
        self.angle = numerics["angle"]
        self.index = numerics["index"]
        self.length = numerics["length"]
        self.solo = solo

    @property
    def box(self) -> Tuple[int, int]:
        """Computes the offset of a diacritic in a Glyph

        Returns:
            Tuple[int, int]: Top-left corner in the Glyph
        """
        differences = [i - (self.length - 1) / 2 for i in range(self.length)]
        difference = differences[abs(self.index) - 1]
        difference *= 2 if self.solo else 1

        add = (0, difference) if self.angle in [1, 2, 4] else (difference, 0)

        angles_before_solo = [(5.5, 2), (2, 1.5), (5, 1), (2, 1.5), (2, 5.5)]
        angles_before_multi = [(5.5, 2), (2, 1.5), (5, 1), (2, 1.5), (2, 5.5)]
        angles_after_solo = [(2, 5.5), (6, 2), (1.5, 2), (5, 5), (5.5, 2)]
        angles_after_multi = [(2, 6), (6.5, 2), (1, 2), (5, 6), (6.5, 2)]

        if self.index < 0:
            angles = angles_before_solo if self.solo else angles_before_multi
        else:
            add = add[::-1]
            angles = angles_after_solo if self.solo else angles_after_multi

        angle = [angles[self.angle][i] + add[i] for i in range(2)]
        angle = [int(a * DIACRITIC) for a in angle]

        return tuple(angle)

    @property
    def image(self) -> Image:
        """Generates the Diacritic image

        Returns:
            Image: The generated image
        """
        return read_symbol_image(
            name=self.symbol,
            symbols={"&": "repeat"},
        )


class Glyph:
    """A Glyph for a syllable(ish)"""

    def __init__(self, string: str, index: int, bools: dict[str, bool]) -> None:
        self.string = string
        self.index = index
        self.is_start = bools["start"]
        self.is_end = bools["end"]
        self.solo = bools["solo"]

        print(self.string)

    @property
    def col(self) -> int:
        """Computes which of 2 columns the glyph occupies

        Returns:
            int: Column index
        """
        return [0, 1, 1, 0][self.index % 4]

    @property
    def row(self) -> int:
        """Computes the row for the glyph

        Returns:
            int: Row index
        """
        return self.index // 2

    @property
    def base(self) -> str:
        """Extracts the consonant of a group

        Returns:
            str: The consonant
        """
        consonants = [char in "bcdfgjklmnpqrstvwxyz,.?!_" for char in self.string]
        return self.string[consonants.index(True)]

    @property
    def diacritics(self) -> List[Diacritic]:
        """Generates list of diacritics for glyph

        Returns:
            List[Diacritic]: The list of diacritics
        """
        diacritics = []

        for index, letter in enumerate(self.string):
            if letter not in "bcdfgjklmnpqrstvwxyz,.?!_":
                length = (
                    len(self.string[: self.string.index(self.base)])
                    if index < self.string.index(self.base)
                    else len(self.string[self.string.index(self.base) + 1 :])
                )
                ail = dict(
                    angle=self.angle,
                    index=index - self.string.index(self.base),
                    length=length,
                )
                diacritics.append(
                    Diacritic(
                        symbol=letter,
                        numerics=ail,
                        solo=self.solo,
                    )
                )

        return diacritics

    @property
    def angle(self) -> int:
        """Computes glyph angle

        Returns:
            int: The angle, in CCW turns
        """
        return [1, 3, 2, 0][self.index % 4] if self.index > 0 else 4

    @property
    def start(self) -> Optional[int]:
        """Place of the start cap

        Returns:
            Optional[int]: The angle, in CCW turns
        """
        if self.is_start:
            return [2, 3, 2, 1][self.index % 4] if self.index > 0 else 0
        return None

    @property
    def end(self) -> Optional[int]:
        """Place of the end cap

        Returns:
            Optional[int]: The angle, in CCW turns
        """
        if self.is_end:
            return [1, 0, 3, 0][self.index % 4]
        return None

    @property
    def ahead(self) -> Optional[int]:
        """Place of the next connector

        Returns:
            Optional[int]: The angle, in CCW turns
        """
        if not self.is_end:
            return [1, 0, 3, 0][self.index % 4]
        return None

    @property
    def behind(self) -> Optional[int]:
        """Place of the previous connector

        Returns:
            Optional[int]: The angle, in CCW turns
        """
        if not self.is_start:
            return [2, 3, 2, 1][self.index % 4]
        return None

    @property
    def image(self) -> Image:
        """Generates the image for the glyph

        Returns:
            Image: The generated image
        """
        symbols = {
            "_": "blank",
            ",": "comma",
            ":": "colon",
            "!": "exclaim",
            "?": "question",
            ".": "stop",
        }

        img = read_symbol_image(
            name=self.base,
            symbols=symbols,
        ).rotate(90 * self.angle)

        if self.is_start:
            img = paste_transparent_image(
                base=img,
                layer=read_symbol_image(name="cap", symbols={}).rotate(90 * self.start),
            )

        if self.is_end:
            img = paste_transparent_image(
                base=img,
                layer=read_symbol_image(name="cap", symbols={}).rotate(90 * self.end),
            )

        if self.ahead is not None:
            img = paste_transparent_image(
                base=img,
                layer=read_symbol_image(name="connect", symbols={}).rotate(
                    90 * self.ahead
                ),
            )

        if self.behind is not None:
            img = paste_transparent_image(
                base=img,
                layer=read_symbol_image(name="connect", symbols={}).rotate(
                    90 * self.behind
                ),
            )

        for diacritic in self.diacritics:
            img = paste_transparent_image(
                base=img,
                layer=diacritic.image,
                box=diacritic.box,
            )

        return img


class Diabolic:
    """Generator base"""

    def __init__(self, string: str) -> None:
        self.string = clean_up_string(string=string)

    @property
    def glyphs(self) -> List[Glyph]:
        """Generates list of glyphs for text

        Returns:
            List[Glyph]: The list of glyphs
        """
        glyphs = []

        matches = list(
            finditer(
                pattern=r"[aeiouh&]{0,3}([bcdfgjklmnpqrstvwxyz_])\1?[aeiouh&]{0,3}",
                string=self.string,
            )
        )

        for index, match in enumerate(matches):
            start, end = match.span()
            text = match.group(0)
            solo = (
                len(matches[index + 1].group(0)) > 1
                if index < len(matches) - 1
                else True
            )
            bools = dict(
                start=start == 0 or index > 0 and self.string[start - 1] == " ",
                end=end == len(self.string) or self.string[end] == " ",
                solo=solo,
            )

            glyphs.append(
                Glyph(
                    string=text,
                    index=index,
                    bools=bools,
                )
            )

        return glyphs

    @property
    def data_url(self) -> str:
        """Converts image into base64-encoded string

        Returns:
            str: The base64-encoded string
        """
        buffer = BytesIO()
        self.image.save(buffer, format="PNG")
        buffer.seek(0)

        output = buffer.getvalue()
        return "data:image/png;base64," + b64encode(output).decode()

    @property
    def image(self) -> Image:
        """Generates the image for the text

        Returns:
            Image: The generated image
        """
        glyphs = self.glyphs

        width = max([g.col for g in glyphs]) + 1.5
        height = max([g.row for g in glyphs]) + 1.5
        img = Image.new(
            mode="RGBA",
            size=(
                int(GLYPH * width),
                int(GLYPH * height),
            ),
            color=(255, 255, 255, 0),
        )

        for glyph in glyphs:
            img = paste_transparent_image(
                base=img,
                layer=glyph.image,
                box=(
                    int(glyph.col * GLYPH + GLYPH / 4),
                    int(glyph.row * GLYPH + GLYPH / 4),
                ),
            )

        return img

    def show(self) -> None:
        """Displays the image, normally not used"""
        self.image.show()
