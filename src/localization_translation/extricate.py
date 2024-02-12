#!/usr/bin/env python3
# Extricate - Take apart and put back together dictionaries

"""Take apart dictionaries"""

# Programmed by CoolCat467

__title__ = "Extricate"
__author__ = "CoolCat467"
__version__ = "0.0.2"

from collections.abc import Callable, Collection
from typing import Any, Final


def wrap_quotes(text: str, quotes: str = '"') -> str:
    """Return text wrapped in quotes"""
    return f"{quotes}{text}{quotes}"


def unwrap_quotes(text: str, layers: int = 1) -> str:
    """Unwrap given layers of quotes"""
    return text[layers:-layers]


def list_or(values: Collection[str]) -> str:
    """Return comma separated listing of values joined with ` or `"""
    if len(values) <= 2:
        return " or ".join(values)
    copy = list(values)
    copy[-1] = f"or {copy[-1]}"
    return ", ".join(copy)


TYPE_CHAR: Final = {
    "str": "!",
    "int": "@",
    "float": "#",
    "bool": "$",
    "dict": "%",
    "list": "^",
    "NoneType": "&",
}
CHAR_TYPE: Final = {v: k for k, v in TYPE_CHAR.items()}

SEP: Final = "*"


def dict_to_list(data: Any) -> tuple[list[str], list[str]]:
    """Convert dictionary to two lists, one of keys, one of values."""

    def read_block(data: Any) -> tuple[list[str], list[str]]:
        """Read block"""
        keys: list[str] = []
        values: list[str] = []

        match type(data).__name__:
            case "dict" as dtype:
                assert isinstance(data, dict)  # Mypy doesn't understand
                # If empty dict
                if not data:
                    keys.append(wrap_quotes(f"{SEP}", TYPE_CHAR[dtype]))
                    values.append("")
                # Will not run if no data to enumerate
                for key, value in data.items():
                    # Ensure key won't break everything
                    intersect = set(str(key)) & (set(CHAR_TYPE) | {SEP})
                    if intersect:
                        raise ValueError(
                            'Dict key contains CHAR_TYPE value(s) "'
                            f"{''.join(intersect)}" + '"',
                        )

                    key = wrap_quotes(key, TYPE_CHAR[type(key).__name__])
                    for block_k, block_v in zip(
                        *read_block(value), strict=True,
                    ):
                        keys.append(
                            wrap_quotes(
                                f"{key}{SEP}{block_k}", TYPE_CHAR[dtype],
                            ),
                        )
                        values.append(block_v)
            case "list" as dtype:
                assert isinstance(data, list)  # Mypy doesn't understand
                # If empty list
                if not data:
                    keys.append(wrap_quotes(f"{SEP}", TYPE_CHAR[dtype]))
                    values.append("")
                # Will not run if no data to enumerate
                for key, value in enumerate(data):
                    for block_k, block_v in zip(
                        *read_block(value), strict=True,
                    ):
                        keys.append(
                            wrap_quotes(
                                f"{key}{SEP}{block_k}", TYPE_CHAR[dtype],
                            ),
                        )
                        values.append(block_v)
            case "str" | "int" | "bool" | "float" | "NoneType" as dtype:
                keys.append(wrap_quotes("", TYPE_CHAR[dtype]))
                values.append(str(data))
            case _ as dtype:
                raise TypeError(
                    f'Expected type {list_or(TYPE_CHAR)}, got "{dtype}"',
                )
        return keys, values

    return read_block(data)


class Segment:
    """Segment with item. Basically like a pointer"""
    __slots__ = ("item",)

    def __init__(self, item: Any = None) -> None:
        self.item = item

    def __repr__(self) -> str:
        if self.item is None:
            return "Segment()"
        return f"Segment({self.item!r})"

    def is_container(self) -> bool:
        """Return if is container"""
        return isinstance(self.item, list | dict)

    def unwrap(self) -> Any:
        """Unwrap contained item"""
        if not self.is_container():
            return self.item
        match type(self.item).__name__:
            case "dict":
                assert isinstance(self.item, dict)  # Mypy doesn't understand
                dict_data = {}
                for key, item in self.item.items():
                    if isinstance(item, Segment):
                        dict_data[key] = item.unwrap()
                        continue
                    dict_data[key] = item
                return dict_data
            case "list":
                assert isinstance(self.item, list)  # Mypy doesn't understand
                list_data = []
                for item in self.item:
                    if isinstance(item, Segment):
                        list_data.append(item.unwrap())
                        continue
                    list_data.append(item)
                return list_data
            case _ as dtype:
                raise ValueError(f'Expected dict or list, got "{dtype}"')


def list_to_dict(keys: list[str], values: list[str]) -> Any:
    """Convert split lists of compiled keys and values back into dictionary"""

    def handle_map(
        segment: Segment, key: str, value: str, map_func: Callable[[Any], Any],
    ) -> None:
        """Unwrap key and either set segment item or continue to unwrap"""
        index = unwrap_quotes(key)
        if index == "":
            segment.item = map_func(value)
            return
        unwrap_key(segment, index, map_func(value))

    def unwrap_key(segment: Segment, key: str, value: Any) -> None:
        """Take apart key and set segment item to value in the right place"""
        head = key[0]
        if head == "":
            segment.item = value
            return
        if head not in CHAR_TYPE:
            raise ValueError(f'Key type character "{head}" unrecognized')
        match CHAR_TYPE[head]:
            case "dict":
                if not isinstance(segment.item, dict):
                    segment.item = {}
                raw_key, index = unwrap_quotes(key).split(SEP, 1)

                if raw_key:
                    dkey: int | str
                    if raw_key[0] not in CHAR_TYPE:
                        raise ValueError(
                            f'Key type character "{raw_key[0]}" unrecognized',
                        )
                    match CHAR_TYPE[raw_key[0]]:
                        case "str":
                            dkey = unwrap_quotes(raw_key)
                        case "int":
                            dkey = int(unwrap_quotes(raw_key))
                        case _ as dtype:
                            raise TypeError(
                                f'Expected str or int, got "{dtype}"',
                            )

                    if dkey not in segment.item:
                        segment.item[dkey] = Segment()
                    unwrap_key(segment.item[dkey], index, value)
            case "list":
                if not isinstance(segment.item, list):
                    segment.item = []
                indice_str, index = unwrap_quotes(key).split(SEP, 1)
                if indice_str:
                    indice = int(indice_str)
                    while indice >= len(segment.item):
                        segment.item.append(Segment())
                    unwrap_key(segment.item[indice], index, value)
            case "str":
                handle_map(segment, key, value, str)
            case "int":
                handle_map(segment, key, value, int)
            case "bool":
                handle_map(segment, key, value, bool)
            case "float":
                handle_map(segment, key, value, float)
            case "NoneType":
                handle_map(segment, key, value, lambda x: None)
            case _ as dtype:
                raise TypeError(
                    f'Expected type {list_or(TYPE_CHAR)}, got "{dtype}"',
                )

    data = Segment()
    for key, value in zip(keys, values, strict=True):
        unwrap_key(data, key, value)
    return data.unwrap()


def run() -> None:
    """Run test of module"""
    test_v = {
        "cat": {
            3: "5",
            7: [4, 3, 3],
            4: ["cat", {"meep": "e", "a": 3, "": [235, "woe", [], None, {}]}],
        },
        "meep": [1, 2, [2, 3, "4"]],
    }
    ##    test_v = [
    ##        'cat'
    ##    ]
    ##    test_v = 5
    ##    test_v = 'cat'
    ##    test_v = ['cat', 'bean', {3: 'mouse', 'mouse': 4}, 17]
    ##    test_v = [[[['cat', 0], 4], '8'], ['3', 'nine', ['14']]]
    ##    test_v = {'success': True, 'result': {'file_id': 1609, 'publication_name': 'Notepad+', 'source_url': 'https://raw.githubusercontent.com/kogtyvPl/numpade/main/main.lua', 'path': 'Main.lua', 'version': 1.07, 'user_name': 'kogtyv', 'whats_new': 'Добавлены расширения файлов: .txt .num .ntxt .npd', 'whats_new_version': 1.07, 'category_id': 1, 'license_id': 1, 'timestamp': 1630854990, 'initial_description': 'Програма для редактирования текстовых файлов (.txt) идея: Bumer_32. приложение создал: kogtyv. Редактируй свои красивые тексты :)', 'translated_description': 'Програма для редактирования текстовых файлов (.txt) идея: Bumer_32. приложение создал: kogtyv. Редактируй свои красивые тексты :)', 'icon_url': 'https://raw.githubusercontent.com/kogtyvPl/numpade/main/Icon.pic', 'average_rating': 3.0, 'dependencies': [1610, 100, 1403, 1685, 1686, 1687, 1688], 'dependencies_data': {'100': {'source_url': 'https://raw.githubusercontent.com/IgorTimofeev/MineOS/master/Libraries/GUI.lua', 'path': 'GUI.lua', 'publication_name': 'GUI', 'category_id': 2, 'version': 1.83}, '73': {'source_url': 'https://raw.githubusercontent.com/IgorTimofeev/MineOS/master/Libraries/Image.lua', 'path': 'Image.lua', 'publication_name': 'Image', 'category_id': 2, 'version': 1.18}, '92': {'source_url': 'https://raw.githubusercontent.com/IgorTimofeev/MineOS/master/Libraries/Color.lua', 'path': 'Color.lua', 'publication_name': 'Color', 'category_id': 2, 'version': 1.14}, '1062': {'source_url': 'https://raw.githubusercontent.com/IgorTimofeev/MineOS/master/Libraries/Bit32.lua', 'path': 'Bit32.lua', 'publication_name': 'Bit32', 'category_id': 2, 'version': 1.01}, '97': {'source_url': 'https://raw.githubusercontent.com/IgorTimofeev/MineOS/master/Libraries/Screen.lua', 'path': 'Screen.lua', 'publication_name': 'Screen', 'category_id': 2, 'version': 1.21}, '1058': {'source_url': 'https://raw.githubusercontent.com/IgorTimofeev/MineOS/master/Libraries/Paths.lua', 'path': 'Paths.lua', 'publication_name': 'Paths', 'category_id': 2, 'version': 1.04}, '1059': {'source_url': 'https://raw.githubusercontent.com/IgorTimofeev/MineOS/master/Libraries/Text.lua', 'path': 'Text.lua', 'publication_name': 'Text', 'category_id': 2, 'version': 1.01}, '1060': {'source_url': 'https://raw.githubusercontent.com/IgorTimofeev/MineOS/master/Libraries/Number.lua', 'path': 'Number.lua', 'publication_name': 'Number', 'category_id': 2, 'version': 1.01}, '1403': {'source_url': 'https://raw.githubusercontent.com/IgorTimofeev/MineOS/master/Libraries/Filesystem.lua', 'path': 'Filesystem.lua', 'publication_name': 'Filesystem', 'category_id': 2, 'version': 1.02}, '1610': {'source_url': 'https://raw.githubusercontent.com/kogtyvPl/numpade/main/Icon.pic', 'path': 'Icon.pic', 'version': 1.07}, '1685': {'source_url': 'https://github.com/kogtyvPl/numpade/raw/main/Extensions%20files/num/Icon.pic', 'path': 'Extensions/.num/Icon.pic', 'version': 1}, '1686': {'source_url': 'https://github.com/kogtyvPl/numpade/raw/main/Extensions%20files/txt/Icon.pic', 'path': 'Extensions/.txt/Icon.pic', 'version': 1}, '1687': {'source_url': 'https://github.com/kogtyvPl/numpade/raw/main/Extensions%20files/npd/Icon.pic', 'path': 'Extensions/.npd/Icon.pic', 'version': 1}, '1688': {'source_url': 'https://github.com/kogtyvPl/numpade/raw/main/Extensions%20files/ntxt/Icon.pic', 'path': 'Extensions/.ntxt/Icon.pic', 'version': 1}}, 'all_dependencies': [100, 73, 92, 1062, 97, 1058, 1059, 1060, 1403, 1610, 1685, 1686, 1687, 1688]}}
    print(f"{test_v = }\n")
    keys, values = dict_to_list(test_v)
    ##    print((keys, values))
    for key, value in zip(keys, values, strict=True):
        print(f"{key} = {value}")
    result = list_to_dict(keys, values)
    print(f"\n{result = }\n")
    print(f"{test_v == result = }")


if __name__ == "__main__":
    print(f"{__title__}\nProgrammed by {__author__}.\n")
    run()
