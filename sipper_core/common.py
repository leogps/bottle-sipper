import os
from sipper_core.constants import get_icons
from sipper_core.html import Icon


def perms_to_string(stat, is_dir):
    directory = 'd' if is_dir else '-'
    mode = oct(stat.st_mode)[-3:]

    permissions = [
        '---', '--x', '-w-', '-wx', 'r--', 'r-x', 'rw-', 'rwx'
    ]

    permission_string = ''.join([permissions[int(n, 8)] for n in mode])

    return directory + permission_string


def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def handle_shortcut_symbols(directory):
    if os.name == 'nt' and directory.startswith('~'):
        return directory.replace('~', os.path.expanduser('~'), 1)
    return directory


def build_icons():
    icons = []
    icons_json = get_icons()
    for ext in icons_json.keys():
        icon = Icon(name=ext, base64_data=icons_json[ext])
        icons.append(icon)
    return icons


def file_exists_and_is_file(file_path):
    return os.path.exists(file_path) and os.path.isfile(file_path)
