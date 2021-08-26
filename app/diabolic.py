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


def remove_vowels(string: str) -> str:
    return "".join([character for character in string if character not in "aeiouh&"])


def compute_start_caps(groups: List[str], string: str) -> List[Optional[int]]:
    angles = populate_array(
        template=[2, 3, 2, 1],
        base=groups,
    )
    checks = []
    string = remove_vowels(string)

    for i, group in enumerate(groups):
        group = remove_vowels(group)
        checks.append(i == 0 or string[string.index(group) - 1] == " ")
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
    pass


def compute_end_connectors(groups: List[str], string: str) -> List[Optional[int]]:
    pass


def compute_group_horizontals(groups: List[str]) -> List[int]:
    pass


def compute_group_verticals(groups: List[str]) -> List[int]:
    pass


def compute_vowel_locations(
    groups: List[List[str]],
    horizontals: List[int],
    verticals: List[int],
    angles: List[int],
) -> List[dict[str, Union[str, int]]]:
    pass


class Diabolic:
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
        connects_before = compute_start_connectors(
            groups=groups,
            string=string,
        )
        connects_after = compute_end_connectors(
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
                self.compute_image_width(),
                self.compute_image_height(),
            ),
        )

        self.construct_image()

    def compute_image_width(self):
        pass

    def compute_image_height(self):
        pass

    def build_data_url(self) -> str:
        pass
