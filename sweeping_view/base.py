# -*- coding: utf-8 -*-

from io import BytesIO


class BaseReplay:
    def __init__(self, data_buffer, name=None):
        self.name = name
        self.process_buffer(data_buffer)

    def process_buffer(self, data):
        raise NotImplementedError

    def __str__(self):
        return "{}({})".format(type(self).__name__, self.name)

    @classmethod
    def from_file(cls, filename):
        with open(filename, "rb") as file:
            return cls(file, name=filename)

    @classmethod
    def from_bytes(cls, data, name=None):
        return cls(BytesIO(data), name=name)

    @staticmethod
    def read_int(binstr):
        res = 0
        for char in binstr:
            res <<= 8
            res += char
        return res
