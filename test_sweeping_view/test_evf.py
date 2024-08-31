
import pytest

from sweeping_view.evf import EVFReplay


def test_evf(replay_path):
    evf = EVFReplay.from_file(replay_path / "test_subject.evf")

    assert evf.user_identifier == "Szymon_M"
    assert evf.competition_identifier == ""
    assert evf.unique_identifier == ""
    assert evf.timeth == 69597
    assert evf.bbbv == 167
    assert set(evf.mines) == {
        (4, 0),
        (10, 0),
        (12, 0),
        (14, 0),
        (6, 1),
        (7, 2),
        (9, 2),
        (10, 2),
        (15, 2),
        (5, 3),
        (6, 3),
        (10, 3),
        (2, 4),
        (7, 4),
        (8, 4),
        (11, 4),
        (13, 4),
        (8, 5),
        (11, 5),
        (8, 6),
        (13, 6),
        (5, 7),
        (6, 7),
        (8, 7),
        (10, 7),
        (12, 7),
        (2, 8),
        (3, 8),
        (7, 8),
        (7, 9),
        (2, 10),
        (3, 10),
        (5, 10),
        (7, 10),
        (3, 11),
        (11, 11),
        (13, 11),
        (6, 12),
        (7, 12),
        (8, 12),
        (11, 12),
        (3, 13),
        (9, 13),
        (11, 13),
        (9, 14),
        (14, 14),
        (0, 15),
        (8, 15),
        (8, 16),
        (9, 16),
        (3, 17),
        (5, 17),
        (7, 17),
        (9, 18),
        (10, 18),
        (13, 18),
        (6, 19),
        (7, 19),
        (9, 19),
        (12, 19),
        (4, 20),
        (7, 20),
        (14, 20),
        (15, 20),
        (0, 21),
        (3, 21),
        (6, 21),
        (8, 21),
        (10, 21),
        (13, 21),
        (4, 22),
        (7, 22),
        (8, 22),
        (9, 22),
        (10, 22),
        (14, 22),
        (2, 23),
        (7, 23),
        (8, 23),
        (9, 23),
        (12, 24),
        (13, 24),
        (1, 25),
        (2, 25),
        (5, 25),
        (10, 25),
        (15, 25),
        (11, 26),
        (14, 26),
        (1, 27),
        (5, 27),
        (8, 27),
        (14, 27),
        (1, 28),
        (11, 28),
        (2, 29),
        (9, 29),
        (13, 29),
        (14, 29),
    }
