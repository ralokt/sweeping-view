# -*- coding: utf-8 -*-

from datetime import datetime
import logging

from .base import BaseReplay
from .exceptions import InvalidReplayError, UnknownFormatVersionError

logger = logging.getLogger(__name__)


class RMVReplay(BaseReplay):
    MODES = {
        0: "normal",
        1: "UPK",
        2: "cheat",
        3: "density",
    }

    LEVELS = {
        0: "beginner",
        1: "intermediate",
        2: "expert",
        3: "custom",
    }

    MOUSE_EVENT_TYPES = {
        1: "move",
        2: "lmb_down",
        3: "lmb_up",
        4: "rmb_down",
        5: "rmb_up",
        6: "mmb_down",
        7: "mmb_up",
        28: "move",  # reduced version
    }

    BOARD_EVENT_TYPES = {
        9: "pressed",
        10: "pressed_qm",
        11: "closed",
        12: "qm",
        13: "flag",
        14: "open",
        18: "open_0",
        19: "open_1",
        20: "open_2",
        21: "open_3",
        22: "open_4",
        23: "open_5",
        24: "open_6",
        25: "open_7",
        26: "open_8",
        27: "open_blast",
    }

    TERMINATION_EVENT_TYPES = {
        15: "blast",
        16: "win",
        17: "other",
    }

    PLAYER_FIELDS = (
        "name",
        "nickname",
        "country",
        "token",
    )

    def process_buffer(self, data):
        # header 1
        extension = data.read(4)
        ftype = self.read_int(data.read(2))

        if not (1 <= ftype <= 2):
            raise UnknownFormatVersionError(self, ftype)

        if ftype >= 2:
            clone_id = self.read_int(data.read(1))
            major_version_of_clone = self.read_int(data.read(1))

        filesize = self.read_int(data.read(4))

        # header 2
        if ftype == 1:
            result_str_size = self.read_int(data.read(2))
        version_info_size = self.read_int(data.read(2))
        player_info_size = self.read_int(data.read(2))
        board_size = self.read_int(data.read(2))
        preflagged_size = self.read_int(data.read(2))
        properties_size = self.read_int(data.read(2))
        if ftype >= 2:
            extension_properties_size = self.read_int(data.read(2))
        vid_size = self.read_int(data.read(4))
        checksum_size = self.read_int(data.read(2))

        if ftype == 1:
            # result string
            result_str = data.read(result_str_size)

        # version information
        self.version_info = data.read(version_info_size)

        # player fields
        num_player_fields = self.read_int(data.read(2))
        player_fields = []
        player_data = {}
        for _ in range(num_player_fields):
            field_size = ord(data.read(1))
            player_fields.append(data.read(field_size))

        for field_name, field_value in zip(self.PLAYER_FIELDS, player_fields):
            player_data[field_name] = field_value

        # board
        self.timestamp_boardgen = self.read_int(data.read(4))
        self.cols = ord(data.read(1))
        self.rows = ord(data.read(1))
        self.num_mines = self.read_int(data.read(2))
        self.mines = []
        for _ in range(self.num_mines):
            col = ord(data.read(1))
            row = ord(data.read(1))
            self.mines.append((row, col))

        # preflagged
        self.preflags = []
        if preflagged_size:
            num_preflags = self.read_int(data.read(2))
            for _ in range(num_preflags):
                col = ord(data.read(1))
                row = ord(data.read(1))
                self.preflags.append((row, col))

        # properties
        properties = []
        self.properties = {}
        for _ in range(properties_size):
            properties.append(ord(data.read(1)))

        utf8 = ftype >= 2
        self.square_size = 16
        bbbv = None

        self.properties["questionmarks"] = bool(properties[0])
        self.properties["nonflagging"] = bool(properties[1])
        try:
            self.properties["mode"] = self.MODES[properties[2]]
        except KeyError:
            raise InvalidReplayError(self, message="Invalid mode!")
        try:
            self.properties["level"] = self.LEVELS[properties[3]]
        except KeyError:
            raise InvalidReplayError(self, message="Invalid level!")
        if ftype == 1 and properties_size > 4:
            utf8 = properties[4]
        if ftype >= 2:
            bbbv = properties[4] + properties[5] << 8
            self.square_size = properties[6]

        # TODO: verify that cp1252 is correct, or add encoding parameter
        encoding = "utf-8" if utf8 else "cp1252"

        self.player_data = {
            name: value.decode(encoding) for name, value in player_data.items()
        }

        result_str_field_list = (
            [i.strip() for i in result_str.decode(encoding).split("#") if i.strip()]
            if ftype == 1
            else []
        )
        self.result_str_dict = {
            key.strip(): value.strip()
            for key, value in (field.split(":") for field in result_str_field_list)
        }
        self.bbbv = int(self.result_str_dict["3BV"]) if bbbv is None else bbbv

        self.extension_properties = {}
        if ftype >= 2:
            num_properties = self.read_int(data.read(2))
            for _ in range(num_properties):
                key_size = ord(data.read(1))
                key = data.read(key_size).decode(encoding)
                value_size = ord(data.read(1))
                value = data.read(value_size)
                self.extension_properties[key] = value

        self.events = []
        xpos = None
        ypos = None
        gametime = None
        nFlags = None
        (xoffs, yoffs) = (12, 56) if ftype == 1 else (0, 0)
        while data:
            evcode = ord(data.read(1))
            if evcode == 0:
                logger.warning("Warning, timestampchange is deprecated!")
                new_timestamp = self.read_int(data.read(4))
                self.events.append(
                    {
                        "type": "timestamp_change",
                        "new_timestamp": new_timestamp,
                    }
                )
            elif 1 <= evcode <= 7 or evcode == 28:
                if evcode == 28:
                    if gametime is None or xpos is None or ypos is None:
                        raise InvalidReplayError(
                            self,
                            message="first mouse event was reduced mouse move",
                        )
                    gametime += ord(data.read(1))
                    mv = ord(data.read(1))
                    # two 4bit two's complement signed integers
                    # n & 7 = last three digits
                    # n & 8 = the leading digit (that has a negative weight in
                    # two's complement)
                    # and of course the xpos change gets shifted into place
                    xpos += (mv >> 4) & 7
                    xpos -= (mv >> 4) & 8
                    ypos += mv & 7
                    ypos -= mv & 8
                else:
                    gametime = self.read_int(data.read(3))
                    nFlags = ord(data.read(1))
                    xpos = self.read_int(data.read(2))
                    ypos = self.read_int(data.read(2))
                self.events.append(
                    {
                        "type": "mouse",
                        "subtype": self.MOUSE_EVENT_TYPES[evcode],
                        "gametime": gametime,
                        "nFlags": nFlags,
                        # in RMV v1, these coordinates are relative to the top
                        # right corner of the client area (ie, the whole UI,
                        # including borders and top bar)
                        # in later versions, they are relative to the top left
                        # corner of the board
                        "xpos": xpos - xoffs,
                        "ypos": ypos - yoffs,
                    }
                )

            elif 9 <= evcode <= 14 or 18 <= evcode <= 27:
                col = ord(data.read(1))
                row = ord(data.read(1))
                self.events.append(
                    {
                        "type": "board",
                        "subtype": self.BOARD_EVENT_TYPES[evcode],
                        "col": col,
                        "row": row,
                    }
                )

            elif 15 <= evcode <= 17:
                self.events.append(
                    {
                        "type": "terminate",
                        "how": self.TERMINATION_EVENT_TYPES[evcode],
                    }
                )
                break
            else:
                raise InvalidReplayError(self)

        self.timeth = self.read_int(data.read(3))
        self.checksum = data.read(checksum_size)

    def get_best_token_source(self):
        token = self.player_data.get("token", None)
        if token is None:
            token = self.result_str_dict["NICK"]
        return token

    def get_boardgen_time(self):
        return datetime.fromtimestamp(self.timestamp_boardgen)
