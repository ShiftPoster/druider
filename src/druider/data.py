import csv
from enum import IntEnum, auto
from typing import Tuple
from pathlib import Path

DataType = Tuple[Tuple[str]]


class Column(IntEnum):
    _name = 0
    cr = auto()
    xp = auto()
    race = auto()
    class1 = auto()
    class1_lvl = auto()
    class2 = auto()
    class2_lvl = auto()
    alignment = auto()
    size = auto()
    type = auto()
    subtype1 = auto()
    subtype2 = auto()
    subtype3 = auto()
    subtype4 = auto()
    subtype5 = auto()
    subtype6 = auto()
    ac = auto()
    ac_touch = auto()
    ac_flat_footed = auto()
    hp = auto()
    hd = auto()
    fort = auto()
    ref = auto()
    will = auto()
    melee = auto()
    ranged = auto()
    space = auto()
    reach = auto()
    _str = auto()
    dex = auto()
    con = auto()
    int = auto()
    wis = auto()
    cha = auto()
    feats = auto()
    skills = auto()
    racialmods = auto()
    languages = auto()
    sq = auto()
    environment = auto()
    organization = auto()
    treasure = auto()
    group = auto()
    gear = auto()
    othergear = auto()
    characterflag = auto()
    companionflag = auto()
    speed = auto()
    base_speed = auto()
    fly_speed = auto()
    maneuverability = auto()
    climb_speed = auto()
    swim_speed = auto()
    burrow_speed = auto()
    speed_special = auto()
    speed_land = auto()
    fly = auto()
    climb = auto()
    burrow = auto()
    swim = auto()
    variantparent = auto()
    classarchetypes = auto()
    companionfamiliarlink = auto()
    alternatenameform = auto()
    id = auto()
    uniquemonster = auto()
    mr = auto()
    mythic = auto()
    mt = auto()
    source = auto()

    @property
    def title(self) -> str:
        title = self.name.split('_')
        title = filter(bool, title)
        title = map(str.capitalize, title)
        return ' '.join(title)

    @property
    def key(self) -> str:
        return self.name


def load_data(file: Path) -> Tuple[Tuple[str]]:
    data = []
    header = True
    with file.open() as fh:
        for entry in csv.reader(fh):
            if header is True:
                header = False
            else:
                data.append(tuple(entry))
    return tuple(data)
