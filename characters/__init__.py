from characters.base_character import BaseCharacter
from characters.cat import CatCharacter
from characters.fairy import FairyCharacter
from characters.ghost import GhostCharacter
from characters.robot import RobotCharacter

CHARACTERS: dict[str, type[BaseCharacter]] = {
    "robot": RobotCharacter,
    "ghost": GhostCharacter,
    "cat": CatCharacter,
    "fairy": FairyCharacter,
}


def get_character(name: str) -> BaseCharacter:
    char_class = CHARACTERS.get(name.lower(), RobotCharacter)
    return char_class()


def list_characters() -> list[dict[str, str]]:
    res = []
    for key, cls in CHARACTERS.items():
        inst = cls()
        res.append({
            "key": key,
            "display_name": inst.display_name,
            "description": inst.description,
        })
    return res


__all__ = ["BaseCharacter", "RobotCharacter", "GhostCharacter", "CatCharacter", "FairyCharacter", "get_character", "list_characters"]
