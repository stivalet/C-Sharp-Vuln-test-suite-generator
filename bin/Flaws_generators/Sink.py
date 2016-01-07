from .Sample import Sample


class SinkSample(Sample):  # Load parameters and code beginning and end
    # new version for new XML
    def __init__(self, sample):  # Add parameters showing the beginning and the end of the sample
        Sample.__init__(self, sample)

        self.input_type = sample.find("input_type").text.lower()
        self.exec_type = sample.find("exec_type").text.lower()
        self.flaw_type = sample.find("flaw_type").text
        self.safe = (sample.find("safe").text == "1")
        self.code = [code.text for code in sample.find("codes").findall("code")]

    def __str__(self):

    def need_exec(self):
        return self.exec_type.lower() != "none"

    def get_exec_type(self):
        return self.exec_type

    def get_input_type(self):
        return self.input_type

    def get_code(self):
        return self.code[0]

    def get_flaw_type(self):
        return self.flaw_type

    def is_safe(self):
        return self.safe

    def compatible_with_filtering(self, filteringSample):
        return filteringSample.contain_flaw_type(self.get_flaw_type()) and (self.input_type == filteringSample.get_output_type())

    def compatible_with_exec_queries(self, exec_queries):
        return self.get_exec_type().lower() == exec_queries.get_type().lower()
