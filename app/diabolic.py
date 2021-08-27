# """
# Diabolic script generator, and helper functions
# """

# from typing import List, Optional, Union
# from re import sub, compile, MULTILINE
# from PIL import Image


# def clean_up_string(string: str) -> str:
#     """
#     Removes duplicate consonants, add placeholder for vowels, removes extra spaces
#     """


# def split_into_groups(string: str) -> List[str]:
#     """
#     Given a string, it splits it into VCV groups
#     """
#     values = []

#     pattern = "[aeiouh]*[bcdfgjklmnpqrstvwxyz][_,:\?!&\.]*[aeiouh]*|"
#     pattern += "[aeiouh]*[bcdfgjklmnpqrstvwxyz_,:\?!&\.][aeiouh]*"

#     pattern = compile(
#         pattern=pattern,
#         flags=MULTILINE,
#     )

#     word_index = 0
#     for word in string.split(" "):

#         for match in pattern.finditer(string=word):
#             if match:
#                 group = ""
#                 index = 0

#                 for i in range(*match.span(0)):
#                     index = i + word_index
#                     group += word[i]

#                 word_index = index

#                 values.append(
#                     dict(
#                         index=word_index,
#                         group=group,
#                     )
#                 )

#     values = sorted(
#         values,
#         key=lambda item: item.get("index"),
#     )

#     values = [item.get("group").strip() for item in values]

#     if not len(values):
#         raise ValueError('Words can not contain only vowels and/or "h"')

#     return values


# def populate_array(template: List[Union[int, List[int]]], base: List[str]) -> List[int]:
#     """
#     Replicates a template array as many times as needed
#     """
#     out = template * ((len(base) // len(template)) + 1)
#     return out[: len(base)]


# def compute_group_angles(groups: List[str]) -> List[int]:
#     """
#     Decides how much to rotate a group
#     """
#     angles = populate_array(
#         template=[1, 3, 2, 0],
#         base=groups,
#     )
#     return [0 if i == 0 else a for i, a in enumerate(angles)]


# def is_vowel(character: str) -> bool:
#     """
#     Decides whether a character is a vowel or not
#     """
#     return character in "aeiouh&"


# def remove_vowels(string: str) -> str:
#     """
#     Removes vowels from a group
#     """
#     return "".join([character for character in string if not is_vowel(character)])


# def compute_start_caps(groups: List[str], string: str) -> List[Optional[int]]:
#     """
#     Decides whether a start cap is needed
#     """
#     angles = populate_array(
#         template=[2, 3, 2, 1],
#         base=groups,
#     )
#     checks = []
#     string = remove_vowels(string)

#     for i, group in enumerate(groups):
#         group = remove_vowels(group)

#         is_start = i == 0
#         after_space = string[string.index(group) - 1] == " "

#         checks.append(is_start or after_space)
#         string = string[len(group) :]

#     return [0 if i == 0 else a if checks[i] else None for i, a in enumerate(angles)]


# def compute_end_caps(groups: List[str], string: str) -> List[Optional[int]]:
#     """
#     Decides whether an end cap is needed
#     """
#     angles = populate_array(
#         template=[1, 0, 3, 0],
#         base=groups,
#     )
#     checks = []
#     string = remove_vowels(string)

#     for i, group in enumerate(groups):
#         group = remove_vowels(group)

#         is_end = i == len(groups) - 1
#         try:
#             before_space = string[string.index(group) + len(group)] == " "
#         except IndexError:
#             pass

#         checks.append(is_end or before_space)
#         string = string[len(group) :]

#     return [
#         1 if i == 0 and checks[i] else angle if checks[i] else None
#         for i, angle in enumerate(angles)
#     ]


# def compute_start_connectors(groups: List[str], string: str) -> List[Optional[int]]:
#     """
#     Decides whether a start connector is needed
#     """
#     angles = populate_array(
#         template=[2, 3, 2, 1],
#         base=groups,
#     )
#     checks = []
#     string = remove_vowels(string)

#     for i, group in enumerate(groups):
#         group = remove_vowels(group)

#         not_start = i != 0
#         not_before_space = string[string.index(group) - 1] != " "

#         checks.append(not_start and not_before_space)
#         string = string[len(group) :]

#     return [a if checks[i] else None for i, a in enumerate(angles)]


# def compute_end_connectors(groups: List[str], string: str) -> List[Optional[int]]:
#     angles = populate_array(
#         template=[1, 0, 3, 0],
#         base=groups,
#     )
#     checks = []
#     string = remove_vowels(string)

#     for i, group in enumerate(groups):
#         group = remove_vowels(group)

#         before_end = i != len(groups) - 1
#         try:
#             not_before_space = string[string.index(group) + len(group)] != " "
#         except IndexError:
#             pass

#         checks.append(before_end and not_before_space)
#         string = string[len(group) :]

#     return [
#         1 if i == 0 and checks[i] else a if checks[i] else None
#         for i, a in enumerate(angles)
#     ]


# def compute_group_horizontals(groups: List[str]) -> List[int]:
#     return populate_array(
#         template=[0, 1, 1, 0],
#         base=groups,
#     )


# def compute_group_verticals(groups: List[str]) -> List[int]:
#     return [index // 2 for index in range(len(groups))]


# def compute_vowel_locations(
#     groups: List[List[str]],
#     horizontals: List[int],
#     verticals: List[int],
#     angles: List[int],
# ) -> List[dict[str, Union[str, int]]]:
#     columns_template = [
#         [0, 1],
#         [0, 1],
#         [2, 1],
#         [1, 2],
#     ]
#     out = []

#     for group_index, group in enumerate(groups):
#         consonant_index = [is_vowel(c) for c in group].index(False)

#         for i, character in enumerate(group):
#             if is_vowel(character):
#                 angle = columns_template[angles[group_index]]

#                 horizontal = angle[int(i > consonant_index)]
#                 vertical = verticals[group_index]

#                 vertical_offset = 1 if horizontal in [0, 2] else 0

#                 current = dict(
#                     character=character,
#                     horizontal=horizontals[group_index],
#                     vertical=vertical,
#                     horizontal_offset=horizontal,
#                     vertical_offset=vertical_offset,
#                 )

#                 out.append(current)

#     for i in range(1, len(out)):
#         prev = out[i - 1]
#         current = out[i]

#         if (
#             prev.get("character") != "h"
#             and current.get("horizontal") == prev.get("horizontal")
#             and current.get("vertical") == prev.get("vertical")
#         ):
#             out[i]["vertical_offset"] += prev.get("vertical_offset") + 1

#     return out


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
    alt_angles = [(val + 1) % 4 for val in angles]

    start_caps = [None] * len(matches)
    end_caps = [None] * len(matches)

    start_connects = [None] * len(matches)
    end_connects = [None] * len(matches)

    columns = populate_array(template=[0, 1, 1, 0], base=matches)

    for index, match in enumerate(matches):
        start, end = match.span()
        prev = string[max(0, start - 1)]
        next = string[min(end, len(string) - 1)]

        if index == 0 or prev == " ":
            start_caps[index] = angles[index]

        if index == len(matches) - 1 or next == " ":
            end_caps[index] = alt_angles[index]

        if index > 0 and prev != " ":
            start_connects[index] = angles[index]

        if index < len(matches) - 1 and next != " ":
            end_connects[index] = alt_angles[index]

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

        image_width = max([g.get("column") + 1 for g in groups])
        image_height = max([g.get("row") + 1 for g in groups])

        self.base_image = Image.new(
            mode="RGBA",
            color=(255, 255, 255, 0),
            size=(image_width, image_height),
        )

        # string = clean_up_string(string=text)
        # groups = split_into_groups(string=string)
        # angles = compute_group_angles(groups=groups)

        # start_caps = compute_start_caps(
        #     groups=groups,
        #     string=string,
        # )
        # end_caps = compute_end_caps(
        #     groups=groups,
        #     string=string,
        # )

        # connectors_before = compute_start_connectors(
        #     groups=groups,
        #     string=string,
        # )
        # connectors_after = compute_end_connectors(
        #     groups=groups,
        #     string=string,
        # )
        # group_horizontals = compute_group_horizontals(groups=groups)
        # group_verticals = compute_group_verticals(groups=groups)

        # self.groups = [
        #     dict(
        #         chars=group,
        #         angle=angles[i],
        #         start_cap=start_caps[i],
        #         end_cap=end_caps[i],
        #         connect_before=connectors_before[i],
        #         connect_after=connectors_after[i],
        #         horizontal=group_horizontals[i],
        #         vertical=group_verticals[i],
        #     )
        #     for i, group in enumerate(groups)
        # ]

        # vowels = compute_vowel_locations(
        #     groups=groups,
        #     horizontals=group_horizontals,
        #     verticals=group_verticals,
        #     angles=angles,
        # )

        # self.base_image = Image.new(
        #     mode="RGBA",
        #     color=(255, 255, 255, 0),
        #     size=(
        #         self.compute_image_width(horizontals=group_horizontals),
        #         self.compute_image_height(verticals=group_verticals),
        #     ),
        # )

        # self.construct_image(
        #     groups=groups,
        #     horizontals=group_horizontals,
        #     verticals=group_verticals,
        #     angles=angles,
        #     start_caps=start_caps,
        #     end_caps=end_caps,
        #     connectors_before=connectors_before,
        #     connectors_after=connectors_after,
        #     vowels=vowels,
        # )

    # def compute_image_width(self, horizontals: List[int]) -> int:
    #     width = max(horizontals) + 1 if len(horizontals) else 1
    #     return self.SIZE * (width + 1)

    # def compute_image_height(self, verticals: List[int]) -> int:
    #     height = max(verticals) + 1 if len(verticals) else 1
    #     return self.SIZE * height + (self.SIZE // 3) + 1

    # def construct_image(
    #     self,
    #     groups: List[str],
    #     horizontals: List[int],
    #     verticals: List[int],
    #     angles: List[int],
    #     start_caps: List[Optional[int]],
    #     end_caps: List[Optional[int]],
    #     connectors_before: List[int],
    #     connectors_after: List[int],
    #     vowels: List[dict[str, Union[str, int]]],
    # ) -> None:

    #     self.place_consonants(
    #         groups=groups,
    #         horizontals=horizontals,
    #         verticals=verticals,
    #         angles=angles,
    #     )

    #     self.place_caps(
    #         groups=groups,
    #         horizontals=horizontals,
    #         verticals=verticals,
    #         start_caps=start_caps,
    #         end_caps=end_caps,
    #     )

    #     self.place_connectors(
    #         groups=groups,
    #         horizontals=horizontals,
    #         verticals=verticals,
    #         connectors_before=connectors_before,
    #         connectors_after=connectors_after,
    #     )

    #     self.place_vowels(vowels=vowels)

    # def place_consonants(
    #     self,
    #     groups: List[str],
    #     horizontals: List[int],
    #     verticals: List[int],
    #     angles: List[int],
    # ) -> None:
    #     for i, group in enumerate(groups):
    #         horizontal = horizontals[i] * self.SIZE
    #         vertical = verticals[i] * self.SIZE

    #         char = [c for c in group if not is_vowel(c)]
    #         char = [
    #             self.SPECIAL_CHARACTERS.get(c)
    #             if c in self.SPECIAL_CHARACTERS.keys()
    #             else c
    #             for c in char
    #         ]
    #         char = [read_symbol_image(c).rotate(90 * angles[i]) for c in char]

    #         for c in char:
    #             self.base_image = paste_transparent_image(
    #                 background=self.base_image,
    #                 overlay=c,
    #                 horizontal=int(horizontal + (self.SIZE * 0.5)),
    #                 vertical=int(vertical + (self.SIZE * 0.25)),
    #             )

    # def place_caps(
    #     self,
    #     groups: List[str],
    #     horizontals: List[int],
    #     verticals: List[int],
    #     start_caps: List[int],
    #     end_caps: List[int],
    # ) -> None:
    #     for i in range(len(groups)):
    #         horizontal = horizontals[i] * self.SIZE
    #         vertical = verticals[i] * self.SIZE

    #         if start_caps[i] is not None:
    #             cap = read_symbol_image("cap").rotate(90 * start_caps[i])

    #             self.base_image = paste_transparent_image(
    #                 background=self.base_image,
    #                 overlay=cap,
    #                 horizontal=int(horizontal + (self.SIZE * 0.5)),
    #                 vertical=int(vertical + (self.SIZE * 0.25)),
    #             )

    #         if end_caps[i] is not None:
    #             cap = read_symbol_image("cap").rotate(90 * end_caps[i])

    #             self.base_image = paste_transparent_image(
    #                 background=self.base_image,
    #                 overlay=cap,
    #                 horizontal=int(horizontal + (self.SIZE * 0.5)),
    #                 vertical=int(vertical + (self.SIZE * 0.25)),
    #             )

    # def place_connectors(
    #     self,
    #     groups: List[str],
    #     horizontals: List[int],
    #     verticals: List[int],
    #     connectors_before: List[int],
    #     connectors_after: List[int],
    # ) -> None:
    #     for i in range(len(groups)):
    #         horizontal = horizontals[i] * self.SIZE
    #         vertical = verticals[i] * self.SIZE

    #         if connectors_before[i] is not None:
    #             connect = read_symbol_image("connect")
    #             connect = connect.rotate(90 * connectors_before[i])

    #             self.base_image = paste_transparent_image(
    #                 background=self.base_image,
    #                 overlay=connect,
    #                 horizontal=int(horizontal + (self.SIZE * 0.5)),
    #                 vertical=int(vertical + (self.SIZE * 0.25)),
    #             )

    #         if connectors_after[i] is not None:
    #             connect = read_symbol_image("connect")
    #             connect = connect.rotate(90 * connectors_after[i])

    #             self.base_image = paste_transparent_image(
    #                 background=self.base_image,
    #                 overlay=connect,
    #                 horizontal=int(horizontal + (self.SIZE * 0.5)),
    #                 vertical=int(vertical + (self.SIZE * 0.25)),
    #             )

    # def place_vowels(self, vowels: List[dict[str, Union[str, int]]]) -> None:
    #     for vowel in vowels:
    #         try:
    #             char = vowel.get("character")
    #             char = (
    #                 self.SPECIAL_CHARACTERS.get(char)
    #                 if char in self.SPECIAL_CHARACTERS.keys()
    #                 else char
    #             )

    #             horizontal = self.SIZE * vowel.get("horizontal")
    #             horizontal += [-0.15, 0, 0.85][
    #                 vowel.get("horizontal_offset")
    #             ] * self.SIZE

    #             vertical = self.SIZE * vowel.get("vertical")
    #             vertical += self.VOWEL * vowel.get("vertical_offset")
    #             vertical += self.SIZE * 0.25

    #             if vowel.get("character") != "h":
    #                 self.base_image = paste_transparent_image(
    #                     background=self.base_image,
    #                     overlay=read_symbol_image(char),
    #                     horizontal=int(horizontal),
    #                     vertical=int(vertical),
    #                 )

    #         except FileNotFoundError:
    #             pass

    # def show(self) -> None:
    #     self.base_image.show()

    # def build_data_url(self) -> None:
    #     from io import BytesIO
    #     from base64 import b64encode

    #     buffer = BytesIO()
    #     self.base_image.save(buffer, format="PNG")
    #     buffer.seek(0)

    #     output = buffer.getvalue()
    #     return "data:image/png;base64," + b64encode(output).decode()


if __name__ == "__main__":
    import os

    os.system("clear")

    strings = [
        # "necromancer bee",
        "hermit crane",
        # "sorrow hawk",
        # "hehe",
        # "this was a dumb idea"
    ]

    for string in strings:
        s = Diabolic(string)
        print(s.__dict__)
