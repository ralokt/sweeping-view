from .avf import AVFReplay
from .exceptions import MimeTypeNotImplemented, UnknownMimeType
from .rmv import RMVReplay

MIME_TYPES = {
    "application/x-minesweeper-arbiter": AVFReplay,
    "application/x-viennasweeper": RMVReplay,
    "application/x-minesweeper-x": NotImplemented,
}


def get_class(mime_type):
    cls_or_nimpl = MIME_TYPES.get(mime_type, None)
    if cls_or_nimpl is None:
        raise UnknownMimeType(mime_type)
    if cls_or_nimpl is NotImplemented:
        raise MimeTypeNotImplemented(mime_type)
    return cls_or_nimpl


def supported():
    return [mt for mt, cls in MIME_TYPES.items() if cls is not NotImplemented]
