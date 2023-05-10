import pytest
from glob import glob
from moments.moment import GRAMMAR
from pathlib import Path


def get_mdls():
    p = Path(__file__).with_name("good") / "*.mdl"
    filelist = glob(p.absolute().as_posix())
    mdls = []
    for file in filelist:
        with open(file, "r", encoding="utf-8") as f:
            mdls.append(f.read())
    return mdls


class TestGrammar:
    def test_load_grammar(self):
        assert GRAMMAR

    @pytest.mark.parametrize("mdl", get_mdls())
    def test_good(self, mdl):
        assert GRAMMAR.parse(mdl) is not None
