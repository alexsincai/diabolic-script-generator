import re
import io
import base64
from os.path import dirname, join, realpath
from typing import List, Optional, Tuple, Union

from PIL import Image


GLYPH = 210
DIACRITIC = 30


def read_symbol_image(name: str, symbols: dict[str, str] = {}) -> Image:
    name = symbols[name] if name in symbols.keys() else name
    path = realpath(join(dirname(__file__), "..", "assets"))

    return Image.open(join(path, name + ".png"))


def paste_transparent_image(
    base: Image,
    layer: Image,
    box: Tuple[int, int] = (0, 0),
) -> Image:

    overlay = Image.new(mode="RGBA", size=base.size)
    overlay.paste(im=layer, box=box, mask=layer)

    return Image.alpha_composite(base, overlay)


class Diacritic:
    def __init__(self, symbol: str):
        self.symbol = symbol


class Glyph:
    def __init__(self, string: str, index: int, start: bool, end: bool) -> None:
        self.string = string
        self.index = index
        self.is_start = start
        self.is_end = end

    @property
    def angle(self) -> int:
        return [0, 3, 2, 1][self.index % 4] if self.index > 0 else 4

    @property
    def col(self) -> int:
        return [0, 1, 1, 0][self.index % 4]

    @property
    def row(self) -> int:
        return self.index // 2

    @property
    def base(self) -> str:
        consonants = [char in "bcdfgjklmnpqrstvwxyz,.?!_" for char in self.string]
        return self.string[consonants.index(True)]

    @property
    def diacritics(self) -> Optional[List[Diacritic]]:
        diacritics = []

        for letter in self.string:
            if letter not in "bcdfgjklmnpqrstvwxyz,.?!_":
                diacritics.append(Diacritic(symbol=letter))

        return None if not len(diacritics) else diacritics

    @property
    def start(self) -> Optional[int]:
        if self.is_start:
            return [2, 3, 2, 1][self.index % 4] if self.index > 0 else 0

    @property
    def end(self) -> Optional[int]:
        if self.is_end:
            return [1, 0, 3, 0][self.index % 4]

    @property
    def ahead(self) -> Optional[int]:
        if not self.is_end:
            return [1, 0, 3, 0][self.index % 4]

    @property
    def behind(self) -> Optional[int]:
        if not self.is_start:
            return [2, 3, 2, 1][self.index % 4]

    @property
    def image(self) -> Image:
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
                layer=read_symbol_image(name="cap").rotate(90 * self.start),
            )

        if self.is_end:
            img = paste_transparent_image(
                base=img,
                layer=read_symbol_image(name="cap").rotate(90 * self.end),
            )

        if self.ahead is not None:
            img = paste_transparent_image(
                base=img,
                layer=read_symbol_image(name="connect").rotate(90 * self.ahead),
            )

        if self.behind is not None:
            img = paste_transparent_image(
                base=img,
                layer=read_symbol_image(name="connect").rotate(90 * self.behind),
            )

        return img


class Diabolic:
    def __init__(self, string: str) -> None:
        self.string = self.clean_up_string(string=string)

    def clean_up_string(self, string: str) -> str:
        string = string.lower().strip()

        string = re.sub(
            pattern=r"([bcdfghjklmnpqrstvwxyz])\1+",
            repl=r"\1&",
            string=string,
            flags=re.MULTILINE,
        )

        devoc = re.sub(
            pattern=r"[aeiouh&]+",
            repl="",
            string=string,
            flags=re.MULTILINE,
        )

        if len(devoc) == 0:
            string = re.sub(
                pattern=r"([aeiouh&]{1,3})([aeiouh&]{1,3})",
                repl=r"\1_\2",
                string=string,
                flags=re.MULTILINE,
            )

        string = re.sub(
            pattern=r"(\s)([aeiouh&])(\s)",
            repl=r"\1\2_\3",
            string=string,
            flags=re.MULTILINE,
        )

        string = re.sub(
            pattern=r"([.,:?!])(\s?)",
            repl=r" \1\2",
            string=string,
            flags=re.MULTILINE,
        )

        string = re.sub(
            pattern=r"\s+",
            repl=" ",
            string=string,
            flags=re.MULTILINE,
        )

        return string.strip()

    @property
    def glyphs(self) -> List[Glyph]:
        glyphs = []

        matches = list(
            re.finditer(
                pattern=r"[aeiouh&]{0,3}([bcdfgjklmnpqrstvwxyz_])\1?[aeiouh&]{0,3}",
                string=self.string,
            )
        )

        for index, match in enumerate(matches):
            start, end = match.span()
            text = match.group(0)

            glyphs.append(
                Glyph(
                    string=text,
                    index=index,
                    start=start == 0 or index > 0 and self.string[start - 1] == " ",
                    end=end == len(self.string) or self.string[end] == " ",
                )
            )

        return glyphs

    @property
    def data_url(self) -> None:
        buffer = io.BytesIO()
        self.image.save(buffer, format="PNG")
        buffer.seek(0)

        output = buffer.getvalue()
        return "data:image/png;base64," + base64.b64encode(output).decode()

    @property
    def image(self) -> Image:
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

        for g in glyphs:
            img = paste_transparent_image(
                base=img,
                layer=g.image,
                box=(
                    int(g.col * GLYPH + GLYPH / 2),
                    int(g.row * GLYPH + GLYPH / 2),
                ),
            )

        return img

    def show(self) -> None:
        self.image.show()


if __name__ == "__main__":
    from os import system

    system("clear")

    image = Diabolic(
        # string="we found there a garden of horrible roses",
        string="qqrta",
    )
    image.show()
