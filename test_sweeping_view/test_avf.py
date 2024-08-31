from datetime import datetime

import pytest

from sweeping_view.avf import AVFReplay


def test_avf(replay_path):
    avf = AVFReplay.from_file(replay_path / "test_subject.avf")

    assert avf.name == "Tommy"
    assert avf.properties["level"] == "beginner"
    assert avf.get_boardgen_time() == datetime(2021, 5, 22, 16, 39, 5, 912000)
    assert set(avf.mines) == {
        (4, 1),
        (5, 2),
        (8, 2),
        (2, 3),
        (6, 3),
        (4, 5),
        (8, 5),
        (6, 6),
        (8, 6),
        (4, 7),
    }
