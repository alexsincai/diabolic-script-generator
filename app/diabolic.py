import re
import io
import base64
from os.path import dirname, join, realpath
from typing import List, Optional, Tuple, Union

from PIL import Image


def vowel(character: str) -> bool:
    return character in "aeiouh&"


def clean_up_string(string: str) -> str:
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


def split_into_groups(string: str) -> List[dict[str, Optional[Union[int, List[str]]]]]:
    output = []

    for index, match in enumerate(
        re.finditer(
            pattern=r"[aeiouh&]{0,3}([bcdfgjklmnpqrstvwxyz_])\1?[aeiouh&]{0,3}",
            string=string,
        )
    ):
        start, end = match.span()

        temp = dict(
            letters=[character for character in match.group(0)],
            angle=[1, 3, 2, 0][index % 4] if index != 0 else 4,
            start=None,
            end=None,
            connect_before=None,
            connect_after=None,
            col=[0, 1, 1, 0][index % 4],
            row=index // 2,
        )

        if start == 0 or start > 0 and string[start - 1] == " ":
            temp["start"] = [2, 3, 2, 1][index % 4] if index != 0 else 0

        if end == len(string) or string[end] == " ":
            temp["end"] = [1, 0, 3, 0][index % 4]

        if start > 0 and string[start - 1] != " ":
            temp["connect_before"] = [2, 3, 2, 1][index % 4]

        if end != len(string) and string[end] != " ":
            temp["connect_after"] = [1, 0, 3, 0][index % 4]

        output.append(temp)

    return output


def paste_transparent_image(
    background: Image,
    overlay: Image,
    box: Tuple[int, int] = (0, 0),
) -> Image:

    layer = Image.new(mode="RGBA", size=background.size)
    layer.paste(im=overlay, box=box, mask=overlay)

    return Image.alpha_composite(background, layer)


class Glyph:
    SYMBOLS = {
        "_": "blank",
        ":": "colon",
        ",": "comma",
        "!": "exclaim",
        "?": "question",
        "&": "repeat",
        ".": "stop",
    }

    SIZE = 30

    def __init__(
        self,
        letters: List[str],
        angle: Optional[int],
        start: Optional[int],
        end: Optional[int],
        connect_before: Optional[int],
        connect_after: Optional[int],
        col: int,
        row: int,
        size: int,
    ) -> None:
        self.letters = letters
        self.angle = angle
        self.start = start
        self.end = end
        self.connect_before = connect_before
        self.connect_after = connect_after
        self.col = col
        self.row = row
        self.size = size

        consonant_base = [not vowel(c) for c in letters].index(True)

        vowels_before = [vowel(c) for c in letters[:consonant_base]]
        vowels_after = [vowel(c) for c in letters[consonant_base:]]

        self.before = [i for i, c in enumerate(vowels_before) if c]
        self.after = [i - 1 for i, c in enumerate(vowels_after) if c]

    def read_symbol_image(self, name: str) -> Image:
        name = self.SYMBOLS[name] if name in self.SYMBOLS.keys() else name
        path = realpath(join(dirname(__file__), "..", "assets"))

        return Image.open(join(path, name + ".png"))

    def get_vowel_position(
        self,
        after: bool,
        angle: int,
        length: int,
        index: int,
    ) -> Tuple[int, int]:

        before_0 = [
            [(2, 3.5)],
            [(2, 5), (2, 4)],
            [(2, 5.5), (2, 4.5), (2, 3.5)],
        ]
        before_1 = []
        before_2 = []
        before_3 = []
        before_4 = [
            [(2, 4.5)],
            [(2, 5), (2, 4)],
            [(2, 5.5), (2, 4.5), (2, 3.5)],
        ]

        after_0 = [
            [(2, 4.5)],
            [(2, 4), (2, 5)],
            [(2, 3.5), (2, 4.5), (2, 5.5)],
        ]
        after_1 = []
        after_2 = []
        after_3 = []
        after_4 = [
            [(2, 3.5)],
            [(2, 4), (2, 5)],
            [(2, 3.5), (2, 4.5), (2, 5.5)],
        ]

        choices = [
            before_0,
            before_1,
            before_2,
            before_3,
            before_4,
        ]

        if after:
            choices = [
                after_0,
                after_1,
                after_2,
                after_3,
                after_4,
            ]

        print(angle, length, index)
        print(choices[angle])
        print(choices[angle][length])
        print(choices[angle][length][index])
        return (0, 0)
        return tuple([int(self.SIZE * b) for b in choices[angle][length][index]])

    def render(self) -> None:
        img = Image.new(
            mode="RGBA",
            size=(self.size, self.size),
            color=(255, 255, 255, 0),
        )
        box = (0, 0)
        saw_consonant = False

        for index, letter in enumerate(self.letters):
            layer = self.read_symbol_image(letter)

            if not vowel(letter):
                angle = 0 if self.angle == 5 else self.angle
                layer = layer.rotate(90 * angle)
                saw_consonant = True
                box = (0, 0)

            else:
                array = self.before if not saw_consonant else self.after
                box = self.get_vowel_position(
                    after=saw_consonant,
                    angle=self.angle,
                    length=len(array) - 1,
                    index=index,
                )

            img = paste_transparent_image(background=img, overlay=layer, box=box)

        if self.start is not None:
            layer = self.read_symbol_image("cap").rotate(90 * self.start)
            img = paste_transparent_image(background=img, overlay=layer, box=box)

        if self.end is not None:
            layer = self.read_symbol_image("cap").rotate(90 * self.end)
            img = paste_transparent_image(background=img, overlay=layer, box=box)

        if self.connect_before is not None:
            layer = self.read_symbol_image("connect").rotate(90 * self.connect_before)
            img = paste_transparent_image(background=img, overlay=layer, box=box)

        if self.connect_after is not None:
            layer = self.read_symbol_image("connect").rotate(90 * self.connect_after)
            img = paste_transparent_image(background=img, overlay=layer, box=box)

        return img


class Diabolic:
    SIZE = 210

    def __init__(self, string: str) -> None:
        string = clean_up_string(string=string)
        groups = split_into_groups(string=string)

        self.groups = [Glyph(**group, size=self.SIZE) for group in groups]

        self.base_image = Image.new(
            mode="RGBA",
            size=(
                int(self.SIZE * (max([g["col"] for g in groups]) + 1.5)),
                int(self.SIZE * (max([g["row"] for g in groups]) + 1.5)),
            ),
            color=(255, 255, 255, 0),
        )

        self.render()

    def render(self) -> None:
        for group in self.groups:
            self.base_image = paste_transparent_image(
                background=self.base_image,
                overlay=group.render(),
                box=(
                    (self.SIZE * group.col) + (self.SIZE // 4),
                    (self.SIZE * group.row) + (self.SIZE // 4),
                ),
            )

    def show(self) -> None:
        self.base_image.show()

    def build_data_url(self) -> str:

        buffer = io.BytesIO()
        self.base_image.save(buffer, format="PNG")
        buffer.seek(0)

        output = buffer.getvalue()
        return "data:image/png;base64," + base64.b64encode(output).decode()


if __name__ == "__main__":
    from os import system

    system("clear")

    image = Diabolic(
        # string="we found there a garden of horrible roses",
        string="qwrta",
    )
    image.show()
