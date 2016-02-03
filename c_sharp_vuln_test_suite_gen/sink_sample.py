from c_sharp_vuln_test_suite_gen.sample import Sample


class SinkSample(Sample):  # Load parameters and code beginning and end
    # new version for new XML
    def __init__(self, sample):  # Add parameters showing the beginning and the end of the sample
        Sample.__init__(self, sample)
        self._input_type = sample.find("input_type").text.lower()
        self._exec_type = sample.find("exec_type").text.lower()
        self._flaw_type = sample.find("flaw_type").text.lower()
        self._flaw_group = sample.find("flaw_type").get("flaw_group").lower()
        # self._safe = (sample.find("safe").text == "1")
        self._need_complexity = True
        if sample.findall("options") and sample.findall("options")[0].get("need_complexity"):
            self._need_complexity = (sample.findall("options")[0].get("need_complexity") == "1")
        self._code = [code.text for code in sample.find("codes").findall("code")]

    def __str__(self):
        return "*** Sink ***\n{}\n\tinput type : {}\n\texec type : {}\n\tflaw type : {}\n\t" \
               "flaw group : {}\n\tsafe : {}\n\tcode : {}\n\n".format(super(SinkSample, self).__str__(),
                                                                      self.input_type,
                                                                      self.exec_type,
                                                                      self.flaw_type,
                                                                      self.flaw_group,
                                                                      self.safe,
                                                                      self.code)

    @property
    def need_complexity(self):
        return self._need_complexity

    def need_exec(self):
        return self.exec_type != "none"

    @property
    def input_type(self):
        return self._input_type

    @property
    def exec_type(self):
        return self._exec_type

    @property
    def code(self):
        return self._code[0]

    @property
    def flaw_type(self):
        return self._flaw_type

    def flaw_type_number(self):
        return int(self._flaw_type[4:])

    @property
    def flaw_group(self):
        return self._flaw_group

    # @property
    # def safe(self):
        # return self._safe

    def compatible_with_exec_queries(self, exec_queries):
        return self.exec_type.lower() == exec_queries.type.lower()
