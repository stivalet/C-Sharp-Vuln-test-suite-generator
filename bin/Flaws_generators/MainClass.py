

class MainClassSample:

    def __init__(self, main_class_sample):
        self._file_extension = main_class_sample.find("file_extension").text
        self._code = main_class_sample.find("code").text
        self._comment = {}
        self._comment['open'] = main_class_sample.find("comment").find("open").text
        self._comment['close'] = main_class_sample.find("comment").find("close").text
        self._comment['inline'] = main_class_sample.find("comment").find("inline").text

    @property
    def code(self):
        return self._code

    @property
    def file_extension(self):
        return self._file_extension

    @property
    def comment(self):
        return self._comment
