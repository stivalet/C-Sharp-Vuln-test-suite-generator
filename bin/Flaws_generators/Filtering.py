from .Sample import Sample


class FilteringSample(Sample):  # Initialize rules, safety, code and escape

    # new version for new XML
    def __init__(self, sample):  # XML tree in parameter
        Sample.__init__(self, sample)

        self.input_type = sample.find("input_type").text.lower()
        self.output_type = sample.find("output_type").text.lower()
        self.code = [code.text for code in sample.find("codes").findall("code")]
        self.flaws = {}
        for flaw in sample.find("flaws").findall("flaw"):
            flaw_type = flaw.get("flaw_type")
            self.flaws[flaw_type] = {}
            self.flaws[flaw_type]["safe"] = (flaw.get("safe") == "1")
            # optional attr: self.flaws[flaw_type]["attr"] = option["attr"] if "attr" in option["attr"] else None

    def __str__(self):
        return "*** Filtering ***\n{}\n\tinput type : {}\n\toutput type : {}\n\tflaws : {}\n\tcode : {}\n\
            \n".format(super(FilteringSample, self).__str__(),
                       self.input_type,
                       self.output_type,
                       self.flaws,
                       self.get_code())

    def get_input_type(self):
        return self.input_type

    def get_output_type(self):
            return self.output_type

    def get_flaws(self):
        return self.flaws.keys()

    def get_code(self):
        return self.code[0]

    def contain_flaw_type(self, flaw_type):
        return flaw_type in self.get_flaws()

    def is_safe(self, flaw_type):
        if flaw_type in self.get_flaws():
            return self.flaws[flaw_type]["safe"]
        return None

    def compatible_with(self, inputSample):
        return self.input_type == inputSample.get_output_type()
