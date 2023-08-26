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


class FileRow:
    def __init__(self, cols):
        self.cols = cols


class FileColumn:
    def __init__(self, value, col_template_file, style_class='', is_link=False,
                 is_itag=False, link_template_file=None,
                 itag_template_file=None):
        self.style_class = style_class
        self.value = value
        self.col_template_file = col_template_file
        self.is_link = is_link
        self.is_itag = is_itag
        self.link_template_file = link_template_file
        self.itag_template_file = itag_template_file
