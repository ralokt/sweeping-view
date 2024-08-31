# -*- coding: utf-8 -*-
from datetime import datetime

from io import SEEK_CUR
from itertools import count

from .base import BaseReplay
from .exceptions import InvalidReplayError


class AVFReplay(BaseReplay):
    MOUSE_EVENT_TYPES = {
        1: "move",
        3: "lmb_down",
        5: "lmb_up",
        9: "rmb_down",
        17: "rmb_up",
        33: "mmb_down",
        65: "mmb_up",
        145: "rmb_up",
        193: "mmb_up",
        11: "shift_lmb_down",
        21: "lmb_up",
    }

    LEVELS = {
        3: "beginner",
        4: "intermediate",
        5: "expert",
        6: "custom",
    }

    def process_buffer(self, data):
        self.properties = {}
        # version
        self.version = ord(data.read(1))
        self.is_freesweeper = not self.version

        # no idea what these bytes do
        data.read(4)
        level = ord(data.read(1))
        try:
            self.properties["level"] = self.LEVELS[level]
        except KeyError:
            raise InvalidReplayError(self, message="Invalid level!")

        if level == 3:
            self.cols = 8
            self.rows = 8
            self.num_mines = 10
        elif level == 4:
            self.cols = 16
            self.rows = 16
            self.num_mines = 40
        elif level == 5:
            self.cols = 30
            self.rows = 16
            self.num_mines = 99
        elif level == 6:
            self.cols = ord(data.read(1)) + 1
            self.rows = ord(data.read(1)) + 1
            self.num_mines = self.read_int(data.read(2))

        self.mines = []
        for ii in range(self.num_mines):
            row = ord(data.read(1))
            col = ord(data.read(1))
            self.mines.append((row, col))

        while data.read(1) != b"[":
            pass

        data.seek(-3, SEEK_CUR)
        self.properties["questionmarks"] = ord(data.read(1)) == 17

        # read past opening "["
        data.read(2)

        info = b""
        while True:
            char = data.read(1)
            if char == b"]":
                break
            info += char
        # TODO: make sure this is always correct/add encoding param
        # TODO: split this info into bits and make usable
        self.ts_info = info.decode("cp1252")
        ts_fields = self.ts_info.split("|")
        self.bbbv = ts_fields[-1][1:].split("T")[0]
        # cus [<mode>|<custom_data>|<timestamp>]
        # beg/int/exp [<mode>|<timestamp>]
        ts_boardgen = ts_fields[2 if level == 6 else 1]
        # dd[.mm.yyyy].hh:mm:ss:<millisecond_garbage (see below)>
        *date_parts, time_parts = ts_boardgen.split(".")
        time_parts = time_parts.split(":")
        milliseconds_str = time_parts.pop()
        time_parts = list(map(int, time_parts))
        date_parts = (list(map(int, date_parts)) + [None, None])[:3]
        year = date_parts[2] or 1970
        month = date_parts[1] or 1
        day = date_parts[0]
        # wtf?
        # arbiter generates the milliseconds string as a string concatenation of
        #   MS div 100
        #   MS div 10
        #   MS mod 10
        # if the leading digit is nonzero, MS div 10 has 2 digits, and the leading
        # digit appears twice
        # this is conveniently the case where we have 4 digits, and the leading
        # digit will be the first one -> cut it off
        microseconds = int(milliseconds_str[-3:]) * 1000
        self.boardgen_time = datetime(year, month, day, *time_parts[:3], microseconds)

        last = ord(data.read(1))
        while True:
            cur = ord(data.read(1))
            if last == 0 and cur == 1:
                break
            last = cur
        data.seek(-3, SEEK_CUR)

        self.events = []
        while True:
            mouse, x1, s2, x2, hun, y1, s1, y2 = tuple(data.read(8))
            xpos = (x1 << 8) + x2
            ypos = (y1 << 8) + y2
            sec = (s1 << 8) + s2 - 1
            gametime = 1000 * sec + 10 * hun
            self.events.append(
                {
                    "type": "mouse",
                    "subtype": self.MOUSE_EVENT_TYPES[mouse],
                    "gametime": gametime,
                    "xpos": xpos,
                    "ypos": ypos,
                }
            )
            if sec < 0:
                break

        last2, last1 = data.read(2)
        ref = tuple(b"cs=")
        while True:
            cur = ord(data.read(1))
            if cur == b"":
                raise InvalidReplayError(self)
            if (last2, last1, cur) == ref:
                break
            last2, last1 = last1, cur
        if self.is_freesweeper:
            for event in self.events:
                ths = ord(data.read(1)) & 0xF
                event["gametime"] += ths
        data.read(17)
        if self.is_freesweeper:
            while ord(data.read(1)) != 13:
                pass
        footer = data.read()
        footer_fields = footer.split(b"\r")
        footer_meta_info = {}
        footer_positional = []
        for field in footer_fields:
            key, *value = field.split(b":", 2)
            if value:
                (value,) = value
                # TODO: make sure this is always correct/add encoding param
                footer_meta_info[key] = value.decode("cp1252").strip()
            else:
                # TODO: make sure this is always correct/add encoding param
                footer_positional.append(key.decode("cp1252"))
        # the last event will have -1 to signal the end of the events
        # section => extract game time from the second to last event
        self.timeth = self.events[-2]["gametime"]
        self.name, self.version_info = footer_positional

    def get_best_token_source(self):
        return self.name

    def get_boardgen_time(self):
        return self.boardgen_time


if __name__ == "__main__":
    main()
