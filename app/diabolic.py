from typing import List, Optional, Union


def clean_up_string(string: str) -> str:
    return string


def split_into_groups(string: str) -> List[str]:
    pass


def compute_group_angles(groups: List[str]) -> List[int]:
    pass


def compute_start_caps(groups: List[str], string: str) -> List[Optional[int]]:
    pass


def compute_end_caps(groups: List[str], string: str) -> List[Optional[int]]:
    pass


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

    def build_data_url(self) -> str:
        pass
