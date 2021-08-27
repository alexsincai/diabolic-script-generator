import re
from typing import Any, List, Optional, Union
from PIL import Image


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
        pattern=r"\s+",
        repl=" ",
        string=string,
        flags=re.MULTILINE,
    )

    return string.strip()


def populate_array(template: List[int], base: List[Any]) -> List[int]:
    out = template * len(base)
    return out[: len(base)]


def determine_vowel_positions(string: str) -> dict[str, List[Union[bool, int]]]:
    characters = [char for char in string]
    vowels = [char in "aeiouh&" for char in characters]

    distances = [abs(i - vowels.index(False)) for i in range(len(vowels))]

    befores = [i < vowels.index(False) for i in range(len(vowels))]
    befores = [distances[i] - 1 for i, b in enumerate(befores) if b and vowels[i]]

    afters = [i > vowels.index(False) for i in range(len(vowels))]
    afters = [distances[i] - 1 for i, a in enumerate(afters) if a and vowels[i]]

    return dict(
        vowels=vowels,
        before=befores[::-1],
        after=afters,
    )


def split_into_groups(string: str) -> List[dict[str, Union[str, Optional[int]]]]:
    pattern = r"[aeiouh&]{0,3}([bcdfgjklmnpqrstvwxyz_])\1?[aeiouh&]{0,3}"
    matches = [match for match in re.finditer(pattern, string, re.MULTILINE)]

    output = []

    angles = populate_array(template=[1, 3, 2, 0], base=matches)
    angles[0] = 0

    start_caps = populate_array(template=[2, 3, 2, 1], base=matches)
    start_caps[0] = 0

    end_caps = populate_array(template=[1, 3, 3, 0], base=matches)
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


def read_symbol_image(name: str) -> Image:
    from os.path import realpath, join, dirname

    return Image.open(realpath(join(dirname(__file__), "..", "assets", name + ".png")))


def paste_transparent_image(
    background: Image, overlay: Image, horizontal: int = 0, vertical: int = 0
) -> Image:

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
) -> Image:
    try:
        char = read_symbol_image(char)
        char = char.rotate(90 * angle)

        return paste_transparent_image(
            background=base,
            overlay=char,
            horizontal=horizontal,
            vertical=vertical,
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
                [(60, 180)],
                [(60, 180), (60, 150)],
                [(60, 210), (60, 180), (60, 150)],
            ],
            after=[
                [(180, 60)],
                [(180, 60), (210, 60)],
                [(150, 60), (180, 60), (210, 60)],
            ],
        ),
        dict(
            before=[
                [(60, 30)],
                [(60, 30), (60, 60)],
                [(60, 0), (60, 30), (60, 60)],
            ],
            after=[
                [(180, 60)],
                [(180, 60), (210, 60)],
                [(150, 60), (180, 60), (210, 60)],
            ],
        ),
        dict(
            before=[
                [(150, 30)],
                [(150, 30), (150, 60)],
                [(150, 0), (150, 30), (150, 60)],
            ],
            after=[
                [(30, 60)],
                [(30, 60), (60, 60)],
                [(0, 60), (30, 60), (60, 60)],
            ],
        ),
        dict(
            before=[
                [(30, 60)],
                [(30, 60), (60, 60)],
                [(0, 60), (30, 60), (60, 60)],
            ],
            after=[
                [(150, 150)],
                [(150, 150), (180, 150)],
                [(150, 120), (150, 150), (150, 180)],
            ],
        ),
    ]

    def __init__(self, string: str) -> None:
        string = clean_up_string(string=string)
        groups = split_into_groups(string=string)

        image_width = max([g.get("column") + 1 for g in groups]) * self.SIZE
        image_height = max([g.get("row") + 1 for g in groups]) * self.SIZE

        self.base_image = Image.new(
            mode="RGBA",
            color=(255, 255, 255, 0),
            size=(image_width, image_height),
        )

        self.construct_image(groups=groups)

    def construct_image(self, groups: List[dict]) -> None:

        for group in groups:

            characters = [
                self.SPECIAL_CHARACTERS.get(char)
                if char in self.SPECIAL_CHARACTERS.keys()
                else char
                for char in group.get("string")
            ]

            consonant = [
                char
                for i, char in enumerate(characters)
                if not group.get("positions").get("vowels")[i]
            ].pop()

            h = group.get("column") * self.SIZE
            v = group.get("row") * self.SIZE

            self.base_image = place_character(
                char=consonant,
                angle=group.get("angle"),
                base=self.base_image,
                horizontal=h,
                vertical=v,
            )

            if group.get("start_cap") is not None:
                self.base_image = place_character(
                    char="cap",
                    angle=group.get("start_cap"),
                    base=self.base_image,
                    horizontal=h,
                    vertical=v,
                )

            if group.get("end_cap") is not None:
                self.base_image = place_character(
                    char="cap",
                    angle=group.get("end_cap"),
                    base=self.base_image,
                    horizontal=h,
                    vertical=v,
                )

            if group.get("start_connect") is not None:
                self.base_image = place_character(
                    char="connect",
                    angle=group.get("start_connect"),
                    base=self.base_image,
                    horizontal=h,
                    vertical=v,
                )

            if group.get("end_connect") is not None:
                self.base_image = place_character(
                    char="connect",
                    angle=group.get("end_connect"),
                    base=self.base_image,
                    horizontal=group.get("column") * self.SIZE,
                    vertical=v,
                )

            # index = 0
            # for i, c in enumerate(characters):
            #     if group.get("positions").get("vowels")[i]:
            #         for before in group.get("positions").get("before"):
            #             print(before)

            # # print(group.get("string"), group.get("positions"))

    def show(self) -> None:
        self.base_image.show()

    def build_data_url(self) -> None:
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

    strings = [
        "necromancer bee",
        # "hermit crane",
        # "sorrow hawk",
        # "hehe",
        # "this was a dumb idea"
    ]

    for string in strings:
        s = Diabolic(string)
        s.show()
