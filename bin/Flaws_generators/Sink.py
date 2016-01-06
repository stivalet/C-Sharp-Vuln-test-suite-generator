from .InitializeSample import InitialSample


class SinkSample(InitialSample):  # Load parameters and code beginning and end
    # new version for new XML
    def __init__(self, initialSample):  # Add parameters showing the beginning and the end of the sample
        InitialSample.__init__(self, initialSample)

        self.flaws = [flaw.text for flaw in initialSample.find("flaws").findall("flaw")]
        self.code = [code.text for code in initialSample.find("codes").findall("code")]

        self.safe = False
        if initialSample.find("safeties") is not None and initialSample.find("safeties").find("safety") is not None:
            self.safe =  (initialSample.find("safeties").find("safety").text == 1)

        self.quote = False
        if initialSample.find("safeties") is not None and initialSample.find("safeties").find("quote") is not None:
            self.quote =  (initialSample.find("safeties").find("quote").text == 1)

        self.needErrorSafe = False
        if initialSample.find("safeties") is not None and initialSample.find("safeties").find("needErrorSafe") is not None:
            self.needErrorSafe =  (initialSample.find("safeties").find("needErrorSafe").text == 1)

        constraints = initialSample.find("constraints").findall("constraint")
        for constraint in constraints:
            if "Injection" in constraint.get("flawType"):
                self.constraintType = constraint.get("type")
                self.constraintField = constraint.get("field")
            if "IDOR" in constraint.get("flawType"):
                self.prepared = prepared if constraint.find("prepared") == "1" else noPrepared
            if "URF" in constraint.get("flawType"):
                self.constraintType = constraint.get("type")
                self.constraintField = constraint.get("field")

    def __str__(self):
        return "*** Sink ***\n{}\n\tflaws : {}\n\tsafe : {}\n\tconstraint : type '{}', field '{}'\n\tcode : {}\n".format(super(SinkSample, self).__str__(), self.flaws, self.safe, self.constraintType, self.constraintField, self.code)

    def get_cwe(self):
        return self.flaws[0]

    def is_safe(self):
        return self.safe

    def compatible_with(self, filteringSample):
        return filteringSample.contain_cwe(self.flaws[0])
