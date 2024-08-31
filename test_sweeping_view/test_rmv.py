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
