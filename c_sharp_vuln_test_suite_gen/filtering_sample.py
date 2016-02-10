"""
Filtering Class (TODO DOC)
"""

from c_sharp_vuln_test_suite_gen.sample import Sample


class FilteringSample(Sample):  # Initialize rules, safety, code and escape

    # new version for new XML
    def __init__(self, sample):  # XML tree in parameter
        Sample.__init__(self, sample)
        self._input_type = sample.find("input_type").text.lower()
        """ Type of input variable """
        self._output_type = sample.find("output_type").text.lower()
        """ Type of output variable """
        self._code = [code.text for code in sample.find("codes").findall("code")]
        """ Code of filtering """
        self._flaws = {}
        """ List of flaws for this filtering with safety """
        for flaw in sample.find("flaws").findall("flaw"):
            flaw_type = flaw.get("flaw_type").lower()
            self._flaws[flaw_type] = {}
            self._flaws[flaw_type]["safe"] = (flaw.get("safe") == "1")
            # optional attr: self.flaws[flaw_type]["attr"] = option["attr"] if "attr" in option["attr"] else None

    def __str__(self):
        return "*** Filtering ***\n{}\n\tinput type : {}\n\toutput type : {}\n\tflaws : {}\n\tcode : {}\n\
            \n".format(super(FilteringSample, self).__str__(),
                       self.input_type,
                       self.output_type,
                       self.flaws,
                       self.code)

    @property
    def input_type(self):
        return self._input_type

    @property
    def output_type(self):
            return self._output_type

    @property
    def flaws(self):
        return self._flaws

    def get_flaws_types(self):
        return self.flaws.keys()

    @property
    def code(self):
        return self._code[0]

    def contains_flaw_type(self, flaw_type):
        return "all" in self.flaws.keys() or flaw_type in self.flaws

    def is_safe(self, flaw_type):
        """ Check if current filtering is safe for a flaw type """
        if flaw_type in self.get_flaws_types():
            return self.flaws[flaw_type]["safe"]
        if "all" in self.get_flaws_types():
            return self.flaws["all"]["safe"]
        return None

    def compatible_with_sink(self, sink_sample):
        """ Check if current filtering is compatible with sink """
        return (self.output_type == sink_sample.input_type or self.output_type == "nofilter") and \
            self.contains_flaw_type(sink_sample.flaw_type)
