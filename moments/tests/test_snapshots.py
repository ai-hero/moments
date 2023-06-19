import pytest
import difflib
from glob import glob
from moments.snapshot import Snapshot
from pathlib import Path


def get_mdls():
    p = Path(__file__).with_name("snapshots") / "*.mdl"
    filelist = glob(p.absolute().as_posix())
    mdls = []
    for file in filelist:
        with open(file, "r", encoding="utf-8") as f:
            mdls.append(f.read())
    return mdls


class TestMoments:
    @pytest.mark.parametrize("mdl", get_mdls())
    def test_good(self, mdl: str):
        parsed = Snapshot.parse(mdl)
        assert parsed is not None
        the_difference = difflib.unified_diff(
            mdl.split("\n"), str(parsed).replace("\\\\", "\\").split("\n")
        )
        has_difference = False
        for text in the_difference:
            if text[:3] not in ("+++", "---", "@@ "):
                print(text)
                has_difference = True
        assert has_difference is False
