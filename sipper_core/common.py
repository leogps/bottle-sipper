import hashlib
import os
from sipper_core.constants import get_icons


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


class Icon:
    def __init__(self, name, base64_data):
        self.name = name
        self.base64_data = base64_data


class FileDetails:
    def __init__(self,
                 is_dir,
                 file_icon_style_class,
                 file_icon_base64,
                 last_modified_date,
                 file_permissions,
                 file_size,
                 file_link,
                 file_name):
        self.is_dir = is_dir
        self.file_icon_style_class = file_icon_style_class
        self.file_icon_base64 = file_icon_base64
        self.last_modified_date = last_modified_date
        self.file_permissions = file_permissions
        self.file_size = file_size
        self.file_link = file_link
        self.file_name = file_name
        b = ':'.join([
            self.file_name,
            str(self.is_dir),
            self.file_permissions,
            str(self.file_size),
            str(is_dir)
        ]).encode('utf-8')
        hash_digest = hashlib.sha256(b).hexdigest()
        self.hash = hash_digest

    def to_json(self):
        return {
            "hash": self.hash,
            "isDir": self.is_dir,
            "fileIconStyleClass": self.file_icon_style_class,
            "fileIconBase64": self.file_icon_base64,
            "lastModifiedDate": self.last_modified_date,
            "filePermissions": self.file_permissions,
            "fileSize": self.file_size,
            "fileLink": self.file_link,
            "fileName": self.file_name
        }
