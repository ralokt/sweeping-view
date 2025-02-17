from datetime import datetime

from sweeping_view.rmv import RMVReplay

def test_rmv(replay_path):
    rmv = RMVReplay.from_file(replay_path / "test_subject.rmv")

    assert rmv.player_data["name"] == "tkolar"
    assert rmv.properties["level"] == "beginner"
    assert rmv.get_boardgen_time() == datetime(2020, 9, 19, 21, 41, 17)
    assert set(rmv.mines) == {
        (1, 3),
        (2, 3),
        (4, 2),
        (4, 3),
        (4, 4),
        (4, 5),
        (4, 6),
        (5, 4),
        (6, 6),
        (7, 6),
    }


def test_rmv2(replay_path):
    rmv = RMVReplay.from_file(replay_path / "test_subject_2.rmv")

    assert rmv.clone_id == 1
    assert rmv.major_version_of_clone == 5
    assert rmv.format_version == 2
    assert rmv.player_data["name"] == "Thomas Kolar"
    assert rmv.player_data["nickname"] == "ralokt"
    assert rmv.properties["level"] == "beginner"
    assert rmv.extension_properties["vsweep_skin_fname"] == b"24px_new.bmp"
    assert set(rmv.mines) == {
        (0, 2),
        (0, 6),
        (1, 5),
        (2, 3),
        (3, 6),
        (5, 2),
        (5, 3),
        (6, 0),
        (6, 1),
        (6, 6),
    }
    assert rmv.events[-2:] == [
        {'col': 7, 'row': 7, 'subtype': 'open_1', 'type': 'board'},
        {'how': 'win', 'type': 'terminate'},
    ]
