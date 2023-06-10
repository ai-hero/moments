import pytest
import difflib
from glob import glob
from moments.moment import Moment
from pathlib import Path


def get_mdls():
    p = Path(__file__).with_name("good") / "*.mdl"
    filelist = glob(p.absolute().as_posix())
    mdls = []
    for file in filelist:
        with open(file, "r", encoding="utf-8") as f:
            mdls.append(f.read())
    return mdls


class TestMoments:
    @pytest.mark.parametrize("mdl", get_mdls())
    def test_good(self, mdl: str):
        parsed = Moment.parse(mdl)
        assert parsed is not None
        the_difference = difflib.unified_diff(mdl.split("\n"), str(parsed).split("\n"))
        has_difference = False
        for text in the_difference:
            if text[:3] not in ("+++", "---", "@@ "):
                print(text)
                has_difference = True
        assert has_difference is False
