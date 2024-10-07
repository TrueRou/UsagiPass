import math

from app.database import async_httpx_ctx
from app.maimai.music import MusicList
from app.logging import log, Ansi


score_rank = "D C B BB BBB A AA AAA S S+ SS SS+ SSS SSS+".split(" ")
combo = " FC FC+ AP AP+".split(" ")
diffs = "Basic Advanced Expert Master Re:Master".split(" ")
music_list: MusicList = None


class ChartInfo(object):
    def __init__(self, idNum: str, diff: int, tp: str, achievement: float, ra: int, comboId: int, scoreId: int, title: str, ds: float, lv: str):
        self.idNum = idNum
        self.diff = diff
        self.tp = tp
        self.achievement = achievement
        self.ra = compute_rating(ds, achievement)
        self.comboId = comboId
        self.scoreId = scoreId
        self.title = title
        self.ds = ds
        self.lv = lv

    def __str__(self):
        return "%-50s" % f"{self.title} [{self.tp}]" + f"{self.ds}\t{diffs[self.diff]}\t{self.ra}"

    def __eq__(self, other):
        return self.ra == other.ra

    def __lt__(self, other):
        return self.ra < other.ra

    @classmethod
    def from_json(cls, data):
        rate = ["d", "c", "b", "bb", "bbb", "a", "aa", "aaa", "s", "sp", "ss", "ssp", "sss", "sssp"]
        ri = rate.index(data["rate"])
        fc = ["", "fc", "fcp", "ap", "app"]
        fi = fc.index(data["fc"])
        if music_list is None:
            log("Music list is not initialized", Ansi.RED)
            raise Exception("Music list is not initialized")
        return cls(
            idNum=music_list.by_title(data["title"]).id,
            title=data["title"],
            diff=data["level_index"],
            ra=data["ra"],
            ds=data["ds"],
            comboId=fi,
            scoreId=ri,
            lv=data["level"],
            achievement=data["achievements"],
            tp=data["type"],
        )


class BestList(object):

    def __init__(self, size: int):
        self.data = []
        self.size = size

    def push(self, elem: ChartInfo):
        if len(self.data) >= self.size and elem < self.data[-1]:
            return
        self.data.append(elem)
        self.data.sort()
        self.data.reverse()
        while len(self.data) > self.size:
            del self.data[-1]

    def pop(self):
        del self.data[-1]

    def __str__(self):
        return "[\n\t" + ", \n\t".join([str(ci) for ci in self.data]) + "\n]"

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index]


def compute_rating(ds: float, achievement: float) -> int:
    base = 22.4
    if achievement < 50:
        base = 7.0
    elif achievement < 60:
        base = 8.0
    elif achievement < 70:
        base = 9.6
    elif achievement < 75:
        base = 11.2
    elif achievement < 80:
        base = 12.0
    elif achievement < 90:
        base = 13.6
    elif achievement < 94:
        base = 15.2
    elif achievement < 97:
        base = 16.8
    elif achievement < 98:
        base = 20.0
    elif achievement < 99:
        base = 20.3
    elif achievement < 99.5:
        base = 20.8
    elif achievement < 100:
        base = 21.1
    elif achievement < 100.5:
        base = 21.6

    return math.floor(ds * (min(100.5, achievement) / 100) * base)


async def get_rating(username: str):
    async with async_httpx_ctx() as client:
        response = await client.post("https://www.diving-fish.com/api/maimaidxprober/query/player", json={"username": username, "b50": True})
        response.raise_for_status()
        scores = response.json()
        sd_best = BestList(35)
        dx_best = BestList(15)
        for score in scores["charts"]["sd"]:
            sd_best.push(ChartInfo.from_json(score))
        for score in scores["charts"]["dx"]:
            dx_best.push(ChartInfo.from_json(score))
        player_rating = sum(compute_rating(sd.ds, sd.achievement) for sd in sd_best) + sum(compute_rating(dx.ds, dx.achievement) for dx in dx_best)
        return player_rating
