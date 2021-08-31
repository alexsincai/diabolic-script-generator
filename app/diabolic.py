import re
from io import BytesIO
from base64 import b64encode

from PIL import Image


def clean_up_string(string: str) -> str:
    string = string.lower().strip()

    string = re.sub(
        pattern=r"([bcdfghjklmnpqrstvwxyz_])\1+",
        repl=r"\1&",
        string=string,
    )

    string = re.sub(
        pattern=r"([aeiouh&]{1,3})",
        repl=r"\1_",
        string=string,
    )

    string = re.sub(
        pattern=r"_([aeiouh&]{1,2})_",
        repl=r"_\1",
        string=string,
    )

    string = re.sub(
        pattern=r"\s+",
        repl=" ",
        string=string,
    )

    return string


class Diabolic:
    def __init__(self, string: str) -> None:
        self.string = clean_up_string(string=string)

        self.base_image = Image.new(
            mode="RGBA",
            size=(100, 100),
            color=(255, 255, 255, 0),
        )

    def show(self) -> None:
        self.base_image.show()

    def build_data_url(self) -> str:

        buffer = BytesIO()
        self.base_image.save(buffer, format="PNG")
        buffer.seek(0)

        output = buffer.getvalue()
        return "data:image/png;base64," + b64encode(output).decode()


if __name__ == "__main__":
    from os import system

    system("clear")

    image = Diabolic(
        string="aeih   ddeeee a",
    )
    # image.show()
