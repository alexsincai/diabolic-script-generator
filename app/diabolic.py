"""
Diabolic script generator
"""

from posixpath import dirname, join
from typing import List, Optional, Tuple
from csv import DictReader
from base64 import b64encode
from io import BytesIO
from PIL import Image

SPECIALS = {
    "_": "blank",
    ".": "stop",
    ",": "comma",
    ":": "colon",
    "!": "exclaim",
    "?": "question",
}

SIZE = 210


def read_file(name: str) -> Image:
    """Args:
        name (str): The name of the character

    Returns:
        Image: The image for the character
    """
    return Image.open(join(dirname(__file__), "..", "assets", name + ".png"))


def apply_extras(images: List, condition: bool, option_1: int, option_2: int) -> Image:
    """Args:
        images (List): The base image, the cap image, and the connector image
        condition (bool): Use cap or connector?
        option_1 (int): Cap angle
        option_2 (int): Connector angle

    Returns:
        Image: [description]
    """

    base, cap, connect = images
    copy = Image.new(mode="RGBA", size=base.size)

    angle = option_1 if condition else option_2
    symbol = cap.copy() if condition else connect.copy()
    symbol = symbol.rotate(90 * angle)

    copy.paste(im=symbol, box=(0, 0), mask=symbol)

    return Image.alpha_composite(base, copy)


def map_range(value: int, in_min: int, in_max: int, out_min: int, out_max: int) -> int:
    """Args:
        value (int): The value to be mapped
        in_min (int): Input min
        in_max (int): Input max
        out_min (int): Output min
        out_max (int): Output max

    Returns:
        int: Interpolated result
    """
    div = (in_max - in_min) if (in_max - in_min) != 0 else 1
    return out_min + ((value - in_min) * (out_max - out_min) / div)


class Diacritic:
    """
    A glyph vowel sign
    """

    def __init__(self, sign: str, preceding: bool, parent) -> None:
        self.sign = sign
        self.preceding = preceding
        self.parent = parent

    def __repr__(self) -> str:
        return f"<{'-' if self.preceding else ''}{self.sign}>"

    @property
    def similar_count(self) -> int:
        """Returns:
        int: Gets total diacritics of parent in group
        """
        return sum(1 for d in self.parent.diacritics if d.preceding == self.preceding)

    @property
    def index(self) -> int:
        """Returns:
        int: The current index in the parent diacritic list
        """
        group = [d for d in self.parent.diacritics if d.preceding == self.preceding]
        return group.index(self) if self in group else 0

    @property
    def position(self) -> List[int]:
        """Returns:
        List[ int]: The [x, y] position of the diacritic
        """
        track = self.parent.tracks
        angle = self.parent.angle

        if track["before_start"] is None and self.parent.previous is not None:
            track["before_start"] = self.parent.previous.tracks["after_start"]

            if angle == 4:
                track["before_start"][0] -= SIZE
            if angle == 3:
                track["before_start"][1] -= SIZE
            if angle == 2:
                track["before_start"][0] += SIZE
            if angle == 1:
                track["before_start"][0] -= SIZE
            if angle == 0:
                track["before_start"][1] -= SIZE

        if track["after_end"] is None and self.parent.next is not None:
            track["after_end"] = self.parent.next.tracks["before_end"]

            if angle == 4:
                track["after_end"][0] += SIZE
            if angle == 3:
                track["after_end"][1] += SIZE
            if angle == 2:
                track["after_end"][0] -= SIZE
            if angle == 1:
                track["after_end"][0] += SIZE
            if angle == 0:
                track["after_end"][1] += SIZE

        index = self.index
        this_list = self.similar_count - 1

        minimum = track["before_start"] if self.preceding else track["after_start"]
        maximum = track["before_end"] if self.preceding else track["after_end"]

        this_x = map_range(index, 0, this_list, minimum[0], maximum[0])
        this_y = map_range(index, 0, this_list, minimum[1], maximum[1])

        if this_list == 0:
            this_x = (minimum[0] + maximum[0]) / 2
            this_y = (minimum[1] + maximum[1]) / 2

        return [this_x, this_y]

    @property
    def image(self) -> Image:
        """Returns:
        Image: The image for the diacritic
        """
        return read_file(self.sign)


class Glyph:
    """
    Base consonant and associated vowels
    """

    def __init__(self, base: str) -> None:
        self.base = SPECIALS[base] if base in SPECIALS.keys() else base
        self.previous = None
        self.next = None
        self.is_start = False
        self.is_end = False
        self.diacritics = []
        self._tracks = None

    def __repr__(self) -> str:
        prc = "".join([str(d) for d in self.diacritics if d.preceding])
        nxt = "".join([str(d) for d in self.diacritics if not d.preceding])
        return f"({prc}-{self.base}-{nxt})"

    def mark(self, sign: str, preceding: bool = False) -> None:
        """Adds a diacritic to the glyph

        Args:
            sign (str): The diacritic
            preceding (bool, optional): Place before the bend? Defaults to False.
        """
        self.diacritics.append(
            Diacritic(
                sign=sign,
                preceding=preceding,
                parent=self,
            )
        )

    @property
    def index(self) -> int:
        """Returns:
        int: The index of the glyph
        """
        return self.get_index()

    def get_index(self, start: int = 0) -> int:
        """Args:
            start (int, optional): The preceding index. Defaults to 0.

        Returns:
            int: The index of the glyph
        """
        if self.previous is None:
            return start
        return self.previous.get_index(start + 1)

    @property
    def column(self) -> int:
        """Returns:
        int: The column index of the glyph
        """
        return [0, 1, 1, 0][self.index % 4]

    @property
    def row(self) -> int:
        """Returns:
        int: The row index of the glyph
        """
        return self.index // 2

    @property
    def start(self) -> Optional[int]:
        """Returns:
        Optional[int]: The position of the start cap, if any
        """
        if not self.is_start:
            return None

        index = self.index
        return 0 if index == 0 else [1, 0, 0, 1][index % 4]

    @property
    def end(self) -> Optional[int]:
        """Returns:
        Optional[int]: The position of the end cap, if any
        """
        if not self.is_end:
            return None

        index = self.index
        return 1 if index == 0 else [0, 1, 1, 0][index % 4]

    @property
    def behind(self) -> Optional[int]:
        """Returns:
        Optional[int]: The position of the connector behind, if any
        """
        if self.is_start:
            return None

        return [1, 0, 0, 1][self.index % 4]

    @property
    def ahead(self) -> Optional[int]:
        """Returns:
        Optional[int]: The position of the connector ahead, if any
        """
        if self.is_end:
            return None

        index = self.index
        return 1 if index == 0 else [0, 1, 1, 0][index % 4]

    @property
    def angle(self) -> int:
        """Returns:
        int: The angle of the glyph
        """
        index = self.index
        return 4 if index == 0 else [1, 3, 2, 0][index % 4]

    @property
    def image(self) -> Image:
        """Returns:
        Image: The image for the glyph base
        """
        base = read_file(self.base)
        cap = read_file("cap")
        connect = read_file("connect")

        if self.base not in SPECIALS.values():
            base = apply_extras(
                images=[base, cap, connect],
                condition=self.is_start,
                option_1=self.start,
                option_2=self.behind,
            )

            base = apply_extras(
                images=[base, cap, connect],
                condition=self.is_end,
                option_1=self.end,
                option_2=self.ahead,
            )

        base = base.rotate(90 * self.angle)

        return base

    def get_tracks_by_angle(self, angle: int) -> List[List[int]]:
        """
        Args:
            angle (int): The direction of the glyph. 0-4

        Returns:
            List[List[int]]: The list of track endpoints
        """
        with open(
            join(
                dirname(__file__),
                "..",
                "assets",
                f"diabolic_angles_{angle}.csv",
            ),
            encoding="utf8",
        ) as file:
            reader = DictReader(
                file,
                fieldnames=[
                    "base",
                    "before_start_x",
                    "before_start_y",
                    "before_end_x",
                    "before_end_y",
                    "after_start_x",
                    "after_start_y",
                    "after_end_x",
                    "after_end_y",
                ],
            )
            reader = [r for r in reader if r["base"] == self.base].pop()

            before_start_x = int(reader["before_start_x"])
            before_start_y = int(reader["before_start_y"])
            before_end_x = int(reader["before_end_x"])
            before_end_y = int(reader["before_end_y"])
            after_start_x = int(reader["after_start_x"])
            after_start_y = int(reader["after_start_y"])
            after_end_x = int(reader["after_end_x"])
            after_end_y = int(reader["after_end_y"])

            return [
                [before_start_x, before_start_y] if self.is_start else None,
                [before_end_x, before_end_y],
                [after_start_x, after_start_y],
                [after_end_x, after_end_y] if self.is_end else None,
            ]

    @property
    def tracks(self) -> dict[str, List[int]]:
        """Returns:
        dict[str, List[int]]: The start and end of the current track
        """

        return dict(
            zip(
                ("before_start", "before_end", "after_start", "after_end"),
                self.get_tracks_by_angle(self.angle),
            )
        )


def blank_and_vowels(word: str) -> List[Glyph]:
    """Args:
        word (str): The vowel-only word to process

    Returns:
        List[Glyph]: A list containing a blank glyph with diacritics
    """
    glyph = Glyph(base="blank")
    glyph.is_start = True
    glyph.is_end = True

    for letter in word:
        glyph.mark(sign=letter)

    return [glyph]


def process_consonant(
    word: str,
    index: int,
    array: list,
    diacritics: list,
) -> Tuple[Glyph, list]:
    """Creates a glyph and adds diacritics as needed

    Args:
        word (str): The word to process
        index (int): The inadex of the current letter
        array (list): The array containing all glyphs
        diacritics (list): The array of diacritics

    Returns:
        Tuple[Glyph, list]: The glyph and a blank list of diacritics
    """

    glyph = Glyph(base=word[index])

    if index > 0 and word[index] == word[index - 1]:
        glyph = array.pop()
        glyph.mark(sign="repeat")

    for diacritic in diacritics:
        glyph.mark(
            sign=diacritic,
            preceding=True,
        )

    return glyph, []


def split_word_into_glyphs(word: str) -> List[Glyph]:
    """Args:
        word (str): The input word

    Returns:
        List[Glyph]: The glyphs describing the word
    """

    consonants = [l in "bcdfgjklmnpqrstvwxyz.,:!?" for l in word]

    output = []
    glyph = None

    if not any(consonants):
        return blank_and_vowels(word=word)

    extras = []

    for index, consonant in enumerate(consonants):
        if consonant:
            glyph, extras = process_consonant(
                word=word,
                index=index,
                array=output,
                diacritics=extras,
            )
            output.append(glyph)
        else:
            if glyph is not None:
                glyph.mark(sign=word[index])
            else:
                extras.append(word[index])

    if output[0].base == "blank" and len(output[0].diacritics) == 0:
        output = output[1:]

    output[0].is_start = True
    output[-1].is_end = True

    for i, glyph in enumerate(output):
        if glyph.base in SPECIALS.values():
            glyph.is_start = False
            glyph.is_end = False

            if i > 0:
                output[i - 1].is_end = True

            if i < len(output) - 1:
                output[i + 1].is_start = True

    return output


class Diabolic:
    """
    Turns a string into a set of glyphs
    """

    def __init__(self, string: str) -> None:
        self.string = string.lower().strip()

    def __repr__(self) -> str:
        return "".join([str(g) for g in self.glyphs])

    @property
    def glyphs(self) -> List[Glyph]:
        """Returns:
        List[Glyph]: The list of glyphs making up self.string
        """
        output = []
        for word in self.string.split(" "):
            if len(word) > 0:
                for glyph in split_word_into_glyphs(word):
                    output.append(glyph)

        for i, obj in enumerate(output):
            if i > 0:
                obj.previous = output[i - 1]

            if i < len(output) - 1:
                obj.next = output[i + 1]

        return output

    @property
    def image(self) -> Image:
        """Returns:
        Image: The generated image for the text
        """

        glyphs = self.glyphs

        image_width = 2.5 if len(glyphs) > 1 else 1.5
        image_height = 1.5 + glyphs[-1].row

        img = Image.new(
            mode="RGBA",
            size=(
                int(image_width * SIZE),
                int(image_height * SIZE),
            ),
            color=(0, 0, 0, 0),
        )
        copy = img.copy()

        for glyph in glyphs:

            g_img = glyph.image
            offset_x = int((glyph.column + 0.25) * SIZE)
            offset_y = int((glyph.row + 0.25) * SIZE)

            copy.paste(
                im=g_img,
                box=(offset_x, offset_y),
                mask=g_img,
            )
            img = Image.alpha_composite(img, copy)

            for diacritic in glyph.diacritics:
                diacritic_x, diacritic_y = diacritic.position

                d_img = diacritic.image

                copy.paste(
                    im=d_img,
                    box=(
                        int(offset_x + diacritic_x),
                        int(offset_y + diacritic_y),
                    ),
                    mask=d_img,
                )
                img = Image.alpha_composite(img, copy)

        return img

    def show(self):
        """
        Displays the current image
        """
        self.image.show()

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


if __name__ == "__main__":
    import os

    os.system("clear")

    Diabolic(
        """
        illusory owl
        """
    ).show()
