class ITag:
    def __init__(self, style_classes):
        self.style_classes = style_classes

    def add_style_class(self, style_class):
        self.style_classes.append(style_class)


class AnchorHtmlTag:
    def __init__(self, link, link_text):
        self.link = link
        self.link_text = link_text


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


class FileRow:
    def __init__(self, file_details, cols):
        self.file_details = file_details
        self.cols = cols


class FileColumn:
    def __init__(self, name, value, col_template_file, style_class='', is_link=False,
                 is_itag=False, link_template_file=None,
                 itag_template_file=None):
        self.name = name
        self.style_class = style_class
        self.value = value
        self.col_template_file = col_template_file
        self.is_link = is_link
        self.is_itag = is_itag
        self.link_template_file = link_template_file
        self.itag_template_file = itag_template_file
