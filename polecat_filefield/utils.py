from pathlib import Path

MEDIA_PREFIX = 'media'
TMPFILE_PREFIX = 'tmpfile'


def temporary_path_from_file_id(file_id):
    path = prefix_with_media(TMPFILE_PREFIX, str(file_id))
    return ensure_leading_slash(path)


def destination_path_from_filename(filename):
    path = prefix_with_media(filename)
    return ensure_leading_slash(path)


def prefix_with_media(*args):
    return str(Path(MEDIA_PREFIX).joinpath(*args))


def ensure_leading_slash(path):
    return ('/' + path) if (path and path[0] != '/') else '/'


def remove_leading_slash(path):
    if path and len(path) and path[0] == '/':
        path = path[1:]
    return path
