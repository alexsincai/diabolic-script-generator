from typing import List, Optional, Union
from PIL import Image
from re import sub, compile, MULTILINE


def clean_up_string(string: str) -> str:

    string = string.lower().strip()
    string = sub(
        pattern=r"([bcdfghjklmnpqrstvwxyz])\1+",
        repl=r"\1&",
        string=string,
        flags=MULTILINE,
    )
    string = sub(
        pattern=r"\b([aeiouh]+)\s",
        repl=r" \1_ ",
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


def split_into_groups(string: str) -> List[str]:
    values = []

    pattern = "[aeiouh]*[bcdfgjklmnpqrstvwxyz][_,:\?!&\.]*[aeiouh]*|"
    pattern += "[aeiouh]*[bcdfgjklmnpqrstvwxyz_,:\?!&\.][aeiouh]*"

    pattern = compile(
        pattern=pattern,
        flags=MULTILINE,
    )

    word_index = 0
    for word in string.split(" "):

        for match in pattern.finditer(string=word):
            if match:
                group = ""
                index = 0

                for i in range(*match.span(0)):
                    index = i + word_index
                    group += word[i]

                word_index = index

                values.append(
                    dict(
                        index=word_index,
                        group=group,
                    )
                )

    values = sorted(
        values,
        key=lambda item: item.get("index"),
    )

    values = [item.get("group").strip() for item in values]

    if not len(values):
        raise ValueError('Words can not contain only vowels and/or "h"')

    return values


def populate_array(template: List[Union[int, List[int]]], base: List[str]) -> List[int]:
    out = template * ((len(base) // len(template)) + 1)
    return out[: len(base)]


def compute_group_angles(groups: List[str]) -> List[int]:
    angles = populate_array(
        template=[1, 3, 2, 0],
        base=groups,
    )
    return [0 if i == 0 else a for i, a in enumerate(angles)]


def is_vowel(character: str) -> bool:
    return character in "aeiouh&"


def remove_vowels(string: str) -> str:
    return "".join([character for character in string if not is_vowel(character)])


def compute_start_caps(groups: List[str], string: str) -> List[Optional[int]]:
    angles = populate_array(
        template=[2, 3, 2, 1],
        base=groups,
    )
    checks = []
    string = remove_vowels(string)

    for i, group in enumerate(groups):
        group = remove_vowels(group)

        is_start = i == 0
        after_space = string[string.index(group) - 1] == " "

        checks.append(is_start or after_space)
        string = string[len(group) :]

    return [0 if i == 0 else a if checks[i] else None for i, a in enumerate(angles)]


def compute_end_caps(groups: List[str], string: str) -> List[Optional[int]]:
    angles = populate_array(
        template=[1, 0, 3, 0],
        base=groups,
    )
    checks = []
    string = remove_vowels(string)

    for i, group in enumerate(groups):
        group = remove_vowels(group)

        is_end = i == len(groups) - 1
        before_space = string[string.index(group) + len(group)] == " "

        checks.append(is_end or before_space)
        string = string[len(group) :]

    return [
        1 if i == 0 and checks[i] else angle if checks[i] else None
        for i, angle in enumerate(angles)
    ]


def compute_start_connectors(groups: List[str], string: str) -> List[Optional[int]]:
    angles = populate_array(
        template=[2, 3, 2, 1],
        base=groups,
    )
    checks = []
    string = remove_vowels(string)

    for i, group in enumerate(groups):
        group = remove_vowels(group)

        not_start = i != 0
        not_before_space = string[string.index(group) - 1] != " "

        checks.append(not_start and not_before_space)
        string = string[len(group) :]

    return [a if checks[i] else None for i, a in enumerate(angles)]


def compute_end_connectors(groups: List[str], string: str) -> List[Optional[int]]:
    angles = populate_array(
        template=[1, 0, 3, 0],
        base=groups,
    )
    checks = []
    string = remove_vowels(string)

    for i, group in enumerate(groups):
        group = remove_vowels(group)

        before_end = i != len(groups) - 1
        not_before_space = string[string.index(group) + len(group)] != " "

        checks.append(before_end and not_before_space)
        string = string[len(group) :]

    return [
        1 if i == 0 and checks[i] else a if checks[i] else None
        for i, a in enumerate(angles)
    ]


def compute_group_horizontals(groups: List[str]) -> List[int]:
    return populate_array(
        template=[0, 1, 1, 0],
        base=groups,
    )


def compute_group_verticals(groups: List[str]) -> List[int]:
    return [index // 2 for index in range(len(groups))]


def compute_vowel_locations(
    groups: List[List[str]],
    horizontals: List[int],
    verticals: List[int],
    angles: List[int],
) -> List[dict[str, Union[str, int]]]:
    columns_template = [
        [0, 1],
        [0, 1],
        [2, 1],
        [1, 2],
    ]
    out = []

    for group_index, group in enumerate(groups):
        consonant_index = [is_vowel(c) for c in group].index(False)

        for i, character in enumerate(group):
            if is_vowel(character):
                angle = columns_template[angles[group_index]]

                horizontal = angle[int(i > consonant_index)]
                vertical = verticals[group_index]

                vertical_offset = 1 if horizontal in [0, 2] else 0

                current = dict(
                    character=character,
                    horizontal=horizontals[group_index],
                    vertical=vertical,
                    horizontal_offset=horizontal,
                    vertical_offset=vertical_offset,
                )

                out.append(current)

    for i in range(1, len(out)):
        prev = out[i - 1]
        current = out[i]

        if (
            prev.get("character") != "h"
            and current.get("horizontal") == prev.get("horizontal")
            and current.get("vertical") == prev.get("vertical")
        ):
            out[i]["vertical_offset"] += prev.get("vertical_offset") + 1

    return out


def read_symbol_image(name: str) -> Image:
    from os.path import realpath, join, dirname

    return Image.open(
        realpath(
            join(
                dirname(__file__),
                "..",
                "assets",
                name + ".png",
            )
        )
    )


def paste_transparent_image(
    background: Image,
    overlay: Image,
    horizontal: int = 0,
    vertical: int = 0,
) -> Image:

    layer = Image.new(
        mode="RGBA",
        size=background.size,
    )
    layer.paste(
        im=overlay,
        box=(horizontal, vertical),
        mask=overlay,
    )

    return Image.alpha_composite(background, layer)


class Diabolic:
    SIZE = 210
    VOWEL = 50
    SPECIAL_CHARACTERS = {
        "_": "blank",
        ",": "comma",
        ",": "stop",
        ":": "colon",
        "!": "exclaim",
        "?": "question",
        "&": "repeat",
    }

    def __init__(self, string: str) -> None:
        string = clean_up_string(string=string)
        groups = split_into_groups(string=string)
        angles = compute_group_angles(groups=groups)

        start_caps = compute_start_caps(
            groups=groups,
            string=string,
        )
        end_caps = compute_end_caps(
            groups=groups,
            string=string,
        )
        connectors_before = compute_start_connectors(
            groups=groups,
            string=string,
        )
        connectors_after = compute_end_connectors(
            groups=groups,
            string=string,
        )
        group_horizontals = compute_group_horizontals(groups=groups)
        group_verticals = compute_group_verticals(groups=groups)

        vowels = compute_vowel_locations(
            groups=groups,
            horizontals=group_horizontals,
            verticals=group_verticals,
            angles=angles,
        )

        self.base_image = Image.new(
            mode="RGBA",
            color=(255, 255, 255, 0),
            size=(
                self.compute_image_width(horizontals=group_horizontals),
                self.compute_image_height(verticals=group_verticals),
            ),
        )

        self.construct_image(
            groups=groups,
            horizontals=group_horizontals,
            verticals=group_verticals,
            angles=angles,
            start_caps=start_caps,
            end_caps=end_caps,
            connectors_before=connectors_before,
            connectors_after=connectors_after,
            vowels=vowels,
        )

    def compute_image_width(self, horizontals: List[int]) -> int:
        width = max(horizontals) + 1 if len(horizontals) else 1
        return self.SIZE * (width + 1)

    def compute_image_height(self, verticals: List[int]) -> int:
        height = max(verticals) + 1 if len(verticals) else 1
        return self.SIZE * height + (self.SIZE // 3) + 1

    def construct_image(
        self,
        groups: List[str],
        horizontals: List[int],
        verticals: List[int],
        angles: List[int],
        start_caps: List[Optional[int]],
        end_caps: List[Optional[int]],
        connectors_before: List[int],
        connectors_after: List[int],
        vowels: List[dict[str, Union[str, int]]],
    ) -> None:

        self.place_consonants(
            groups=groups,
            horizontals=horizontals,
            verticals=verticals,
            angles=angles,
        )

        self.place_caps(
            groups=groups,
            horizontals=horizontals,
            verticals=verticals,
            start_caps=start_caps,
            end_caps=end_caps,
        )

        self.place_connectors(
            groups=groups,
            horizontals=horizontals,
            verticals=verticals,
            connectors_before=connectors_before,
            connectors_after=connectors_after,
        )

        self.place_vowels(vowels=vowels)

    def place_consonants(
        self,
        groups: List[str],
        horizontals: List[int],
        verticals: List[int],
        angles: List[int],
    ) -> None:
        for i, group in enumerate(groups):
            horizontal = horizontals[i] * self.SIZE
            vertical = verticals[i] * self.SIZE

            char = [c for c in group if not is_vowel(c)]
            char = [
                self.SPECIAL_CHARACTERS.get(c)
                if c in self.SPECIAL_CHARACTERS.keys()
                else c
                for c in char
            ]
            char = [read_symbol_image(c).rotate(90 * angles[i]) for c in char]

            for c in char:
                self.base_image = paste_transparent_image(
                    background=self.base_image,
                    overlay=c,
                    horizontal=int(horizontal + (self.SIZE * 0.5)),
                    vertical=int(vertical + (self.SIZE * 0.25)),
                )

    def place_caps(
        self,
        groups: List[str],
        horizontals: List[int],
        verticals: List[int],
        start_caps: List[int],
        end_caps: List[int],
    ) -> None:
        for i in range(len(groups)):
            horizontal = horizontals[i] * self.SIZE
            vertical = verticals[i] * self.SIZE

            if start_caps[i] is not None:
                cap = read_symbol_image("cap").rotate(90 * start_caps[i])

                self.base_image = paste_transparent_image(
                    background=self.base_image,
                    overlay=cap,
                    horizontal=int(horizontal + (self.SIZE * 0.5)),
                    vertical=int(vertical + (self.SIZE * 0.25)),
                )

            if end_caps[i] is not None:
                cap = read_symbol_image("cap").rotate(90 * end_caps[i])

                self.base_image = paste_transparent_image(
                    background=self.base_image,
                    overlay=cap,
                    horizontal=int(horizontal + (self.SIZE * 0.5)),
                    vertical=int(vertical + (self.SIZE * 0.25)),
                )

    def place_connectors(
        self,
        groups: List[str],
        horizontals: List[int],
        verticals: List[int],
        connectors_before: List[int],
        connectors_after: List[int],
    ) -> None:
        for i in range(len(groups)):
            horizontal = horizontals[i] * self.SIZE
            vertical = verticals[i] * self.SIZE

            if connectors_before[i] is not None:
                connect = read_symbol_image("connect")
                connect = connect.rotate(90 * connectors_before[i])

                self.base_image = paste_transparent_image(
                    background=self.base_image,
                    overlay=connect,
                    horizontal=int(horizontal + (self.SIZE * 0.5)),
                    vertical=int(vertical + (self.SIZE * 0.25)),
                )

            if connectors_after[i] is not None:
                connect = read_symbol_image("connect")
                connect = connect.rotate(90 * connectors_after[i])

                self.base_image = paste_transparent_image(
                    background=self.base_image,
                    overlay=connect,
                    horizontal=int(horizontal + (self.SIZE * 0.5)),
                    vertical=int(vertical + (self.SIZE * 0.25)),
                )

    def place_vowels(self, vowels: List[dict[str, Union[str, int]]]) -> None:
        for vowel in vowels:
            try:
                char = vowel.get("character")
                char = (
                    self.SPECIAL_CHARACTERS.get(char)
                    if char in self.SPECIAL_CHARACTERS.keys()
                    else char
                )

                horizontal = self.SIZE * vowel.get("horizontal")
                horizontal += [-0.15, 0, 0.85][
                    vowel.get("horizontal_offset")
                ] * self.SIZE

                vertical = self.SIZE * vowel.get("vertical")
                vertical += self.VOWEL * vowel.get("vertical_offset")
                vertical += self.SIZE * 0.25

                if vowel.get("character") != "h":
                    self.base_image = paste_transparent_image(
                        background=self.base_image,
                        overlay=read_symbol_image(char),
                        horizontal=int(horizontal),
                        vertical=int(vertical),
                    )

            except FileNotFoundError:
                pass

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
