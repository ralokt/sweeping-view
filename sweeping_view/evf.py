from datetime import datetime

from .base import BaseReplay
from .exceptions import InvalidReplayError


class EVFBoard:
    def __init__(self, data, cols):
        self.data = data
        self.cols = cols

    def __getitem__(self, item):
        (xx, yy) = item
        bit_index = yy * self.cols + xx
        byte_index = bit_index // 8
        return bool(self.data[byte_index] & (128 >> (bit_index % 8)))


class EVFReplay(BaseReplay):
    MODES = {
        0: "normal",
        1: "UPK",
        2: "cheat",
        3: "density",
        4: "win7",
        5: "competitive_solvable",
        6: "strong_solvable",
        7: "weak_solvable",
        8: "to_be_solvable",
        9: "strong_guessable",
        10: "weak_guessable",
        11: "chording_recursive",
        12: "flag_recursive",
        13: "chording_flag_recursive",
    }

    MOUSE_EVENT_TYPES = {
        1: "move",
        2: "lmb_down",
        3: "lmb_up",
        4: "rmb_down",
        5: "rmb_up",
        6: "mmb_down",
        7: "mmb_up",
        8: "preflag",
        9: "chord",
        10: "lmb",
        11: "rmb",
        12: "mmb",
    }

    def process_buffer(self, data):
        version_number = self.read_int(data.read(1))
        if version_number != 3:
            raise UnknownFormatVersionError(self, version_number)

        summary = self.read_int(data.read(1))
        self.completed = bool(summary & (127 >> 0))
        self.official = bool(summary & (127 >> 1))
        self.fair = bool(summary & (127 >> 2))
        nf = bool(summary & (127 >> 3))

        settings = self.read_int(data.read(1))
        qm_disabled = bool(settings & (127 >> 0))
        board_clip = bool(settings & (127 >> 1))
        loss_autorestart = bool(settings & (127 >> 2))

        self.rows = self.read_int(data.read(1))
        self.cols = self.read_int(data.read(1))
        self.num_mines = self.read_int(data.read(2))
        self.cell_size = self.read_int(data.read(1))
        game_mode_raw = self.read_int(data.read(2))
        self.bbbv = self.read_int(data.read(2))
        self.timeth = self.read_int(data.read(3))
        self.version_info = self.read_c_string(data)
        self.user_identifier = self.read_c_string(data)
        self.competition_identifier = self.read_c_string(data)
        self.unique_identifier = self.read_c_string(data)
        self.start_ts = self.read_c_string(data)
        self.end_ts = self.read_c_string(data)
        self.country_code = self.read_c_string(data)
        self.uuid = self.read_c_string(data)
        board = EVFBoard(data.read((self.cols * self.rows - 1) // 8 + 1), self.cols)

        game_mode = self.MODES.get(game_mode_raw, None)
        if game_mode is None:
            raise InvalidReplayError(
                f"Invalid game mode {game_mode_raw}!",
            )

        num_mines = 0
        self.mines = []
        for xx in range(self.cols):
            for yy in range(self.rows):
                if board[xx, yy]:
                    num_mines += 1
                    self.mines.append((yy, xx))
        if num_mines != self.num_mines:
            raise InvalidReplayError(
                "Number of mines in header field is inconsistent with the board!",
            )

        self.events = []
        while True:
            op = self.read_int(data.read(1))
            if op in (0, 255):
                break
            ts = self.read_int(data.read(3))
            xx = self.read_int(data.read(2))
            yy = self.read_int(data.read(2))
            st = self.MOUSE_EVENT_TYPES.get(op, None)
            if st is None:
                raise InvalidReplayError(f"Unknown mouse operation {op}")
            self.events.append(
                {
                    "type": "mouse",
                    "subtype": st,
                    "gametime": ts,
                    "xpos": xx,
                    "ypos": yy,
                }
            )
        if op == 0:
            self.checksum = data.read(32)
        else:
            self.checksum = None

        level = {
            (8, 8, 10): "beginner",
            (16, 16, 40): "intermediate",
            (30, 16, 40): "expert",
        }.get(
            (
                self.cols,
                self.rows,
                self.num_mines,
            ),
            "custom",
        )

        self.properties = {
            "questionmarks": not qm_disabled,
            "nonflagging": nf,
            "mode": game_mode,
            "level": level,
        }

    def read_c_string(self, data):
        return self.read_bin_c_string(data).decode("utf-8")

    def read_bin_c_string(self, data):
        result = []
        while True:
            next = data.read(1)
            if next == b"\0":
                break
            if next == b"":
                raise InvalidReplayError("EOF while reading null-terminated string")
            result.append(next)
        return b"".join(result)

    def get_best_token_source(self):
        return self.competition_identifier

    def get_boardgen_time(self):
        return datetime.fromtimestamp(int(self.start_ts) // 1000000)
