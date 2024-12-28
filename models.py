from enum import Enum

class Models(Enum):
    つくよみちゃん_れいせい = 0

    @classmethod
    def get_values(cls) -> list:
        return [i.value for i in cls]