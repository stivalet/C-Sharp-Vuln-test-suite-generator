

class MainClassSample:

    def __init__(self, main_class_sample):
        self._file_extension = main_class_sample.find("file_extension").text
        self._code = main_class_sample.find("code").text

    @property
    def code(self):
        return self._code

    @property
    def file_extension(self):
        return self._file_extension
