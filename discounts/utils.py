import re

ID_PATTERN = re.compile(r"/(?P<id>\d)/?$")


def get_id_from_path(path: str) -> int:
    """
    Parses detail-view uri-path and returns id
    :params path: URL path
    :type path: str
    :return: Pk from uri-path
    :rtype: int
    """
    match = ID_PATTERN.search(path)
    return int(match.group("id"))
