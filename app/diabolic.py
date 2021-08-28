import re
from typing import Any, List, Optional, Union
from PIL import Image


def clean_up_string(string: str):
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
        pattern=r"\s+",
        repl=" ",
        string=string,
        flags=re.MULTILINE,
    )

    return string.strip()


def populate_array(template: List[int], base: List[Any]):
    out = template * len(base)
    return out[: len(base)]


def determine_vowel_positions(string: str):
    characters = [char for char in string]
    vowels = [char in "aeiouh&" for char in characters]
    base = vowels.index(False)

    distances = [abs(i - base) for i in range(len(vowels))]

    befores = [i < base for i in range(len(vowels))]
    befores = [distances[i] - 1 for i, b in enumerate(befores) if b and vowels[i]]

    afters = [i > base for i in range(len(vowels))]
    afters = [distances[i] - 1 for i, a in enumerate(afters) if a and vowels[i]]

    return dict(
        vowels=vowels,
        base=base,
        before=befores[::-1],
        after=afters,
    )


def split_into_groups(string: str):
    pattern = r"[aeiouh&]{0,3}([bcdfgjklmnpqrstvwxyz_])\1?[aeiouh&]{0,3}"
    matches = [match for match in re.finditer(pattern, string, re.MULTILINE)]

    output = []

    angles = populate_array(template=[1, 3, 2, 0], base=matches)
    angles[0] = 0

    start_caps = populate_array(template=[2, 3, 2, 1], base=matches)
    start_caps[0] = 0

    end_caps = populate_array(template=[1, 0, 3, 0], base=matches)
    end_caps[0] = 1

    start_connects = populate_array(template=[2, 3, 2, 1], base=matches)
    start_connects[0] = 0

    end_connects = populate_array(template=[1, 0, 3, 0], base=matches)
    end_connects[0] = 1

    columns = populate_array(template=[0, 1, 1, 0], base=matches)

    for index, match in enumerate(matches):
        start, end = match.span()
        prev = string[max(0, start - 1)]
        next = string[min(end, len(string) - 1)]

        if index == 0 or prev == " ":
            start_connects[index] = None

        if index == len(matches) - 1 or next == " ":
            end_connects[index] = None

        if prev != " " and index > 0:
            start_caps[index] = None

        if next != " " and index < len(matches) - 1:
            end_caps[index] = None

        output.append(
            dict(
                string=match.group(0),
                positions=determine_vowel_positions(match.group(0)),
                angle=angles[index],
                row=index // 2,
                column=columns[index],
                start_cap=start_caps[index],
                end_cap=end_caps[index],
                start_connect=start_connects[index],
                end_connect=end_connects[index],
            )
        )

    output = [elem for elem in output if elem.get("string") != "_"]
    return output


def read_symbol_image(name: str):
    from os.path import realpath, join, dirname

    return Image.open(realpath(join(dirname(__file__), "..", "assets", name + ".png")))


def paste_transparent_image(
    background: Image, overlay: Image, horizontal: int = 0, vertical: int = 0
):

    layer = Image.new(mode="RGBA", size=background.size)
    layer.paste(
        im=overlay,
        box=(horizontal, vertical),
        mask=overlay,
    )

    return Image.alpha_composite(background, layer)


def place_character(
    char: str,
    angle: int,
    base: Image,
    horizontal: int,
    vertical: int,
    offset: int,
):
    try:
        char = read_symbol_image(char)
        char = char.rotate(90 * angle)

        return paste_transparent_image(
            background=base,
            overlay=char,
            horizontal=horizontal + offset,
            vertical=vertical + offset,
        )

    except FileNotFoundError:
        pass


class Diabolic:
    SIZE = 210
    VOWEL = 30
    SPECIAL_CHARACTERS = {
        "_": "blank",
        ",": "comma",
        ",": "stop",
        ":": "colon",
        "!": "exclaim",
        "?": "question",
        "&": "repeat",
    }
    TEMPLATES = [
        dict(
            before=[
                [(1, 6)],
                [(1, 6), (1, 5)],
                [(1, 7), (1, 6), (1, 5)],
            ],
            after=[
                [(6, 1)],
                [(6, 1), (7, 1)],
                [(5, 1), (6, 1), (7, 1)],
            ],
        ),
        dict(
            before=[
                [(2, 1)],
                [(2, 1), (2, 2)],
                [(2, 0), (2, 1), (2, 2)],
            ],
            after=[
                [(6, 2)],
                [(6, 2), (7, 2)],
                [(5, 2), (6, 2), (7, 2)],
            ],
        ),
        dict(
            before=[
                [(5, 1)],
                [(5, 1), (5, 2)],
                [(5, 0), (5, 1), (5, 2)],
            ],
            after=[
                [(1, 2)],
                [(1, 2), (1, 3)],
                [(1, 1), (1, 2), (1, 3)],
            ],
        ),
        dict(
            before=[
                [(1, 2)],
                [(1, 2), (2, 2)],
                [(0, 2), (1, 2), (2, 2)],
            ],
            after=[
                [(5, 6)],
                [(5, 6), (5, 7)],
                [(5, 5), (5, 6), (5, 7)],
            ],
        ),
    ]

    def __init__(self, string: str):
        string = clean_up_string(string=string)
        groups = split_into_groups(string=string)
        print([g["string"] for g in groups])

        image_width = max([g.get("column") + 1 for g in groups]) * self.SIZE
        image_height = max([g.get("row") + 1 for g in groups]) * self.SIZE

        self.base_image = Image.new(
            mode="RGBA",
            color=(255, 255, 255, 0),
            size=(
                image_width + self.SIZE,
                image_height + self.SIZE,
            ),
        )

        self.construct_image(groups=groups)

    def construct_image(self, groups: List[dict]):

        for group in groups:

            pos = group.get("positions")
            angle = self.TEMPLATES[group.get("angle")]

            h = group.get("column") * self.SIZE
            v = group.get("row") * self.SIZE

            characters = [
                self.SPECIAL_CHARACTERS.get(char)
                if char in self.SPECIAL_CHARACTERS.keys()
                else char
                for char in group.get("string")
            ]

            consonant = [
                char for i, char in enumerate(characters) if not pos.get("vowels")[i]
            ].pop()

            vowels = [char for i, char in enumerate(characters) if pos.get("vowels")[i]]

            before = (
                angle.get("before")[len(pos.get("before")) - 1]
                if len(pos.get("before"))
                else []
            )
            after = (
                angle.get("after")[len(pos.get("after")) - 1]
                if len(pos.get("after"))
                else []
            )
            vowel_pos = [*before, *after]
            vowel_pos = [(w[0] * self.VOWEL, w[1] * self.VOWEL) for w in vowel_pos]
            # vowel_pos = [(w[0] + h, w[1] + 1) for w in vowel_pos]

            self.base_image = place_character(
                char=consonant,
                angle=group.get("angle"),
                base=self.base_image,
                horizontal=h,
                vertical=v,
                offset=self.SIZE // 2,
            )

            if group.get("start_cap") is not None:
                self.base_image = place_character(
                    char="cap",
                    angle=group.get("start_cap"),
                    base=self.base_image,
                    horizontal=h,
                    vertical=v,
                    offset=self.SIZE // 2,
                )

            if group.get("end_cap") is not None:
                self.base_image = place_character(
                    char="cap",
                    angle=group.get("end_cap"),
                    base=self.base_image,
                    horizontal=h,
                    vertical=v,
                    offset=self.SIZE // 2,
                )

            if group.get("start_connect") is not None:
                self.base_image = place_character(
                    char="connect",
                    angle=group.get("start_connect"),
                    base=self.base_image,
                    horizontal=h,
                    vertical=v,
                    offset=self.SIZE // 2,
                )

            if group.get("end_connect") is not None:
                self.base_image = place_character(
                    char="connect",
                    angle=group.get("end_connect"),
                    base=self.base_image,
                    horizontal=h,
                    vertical=v,
                    offset=self.SIZE // 2,
                )

            if len(vowels):
                for i in range(len(vowels)):
                    self.base_image = place_character(
                        char=vowels[i],
                        angle=0,
                        base=self.base_image,
                        horizontal=vowel_pos[i][0] + h,
                        vertical=vowel_pos[i][1] + v,
                        offset=self.SIZE // 2,
                    )

    def show(self):
        self.base_image.show()

    def build_data_url(self):
        from io import BytesIO
        from base64 import b64encode

        buffer = BytesIO()
        self.base_image.save(buffer, format="PNG")
        buffer.seek(0)

        output = buffer.getvalue()
        return "data:image/png;base64," + b64encode(output).decode()


if __name__ == "__main__":
    import os

    os.system("clear")

    # TODO - only first block has before?
    strings = [
        # "oqoworotoyo",
        "qwaratay",
    ]

    for string in strings:
        s = Diabolic(string)
        s.show()
