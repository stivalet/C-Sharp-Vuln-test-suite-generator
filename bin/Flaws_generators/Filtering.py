from .InitializeSample import InitialSample

class FilteringSample(InitialSample):  # Initialize rules, safety, code and escape

    # new version for new XML
    def __init__(self, initialSample):  # XML tree in parameter
        InitialSample.__init__(self, initialSample)

        self.flaws = [flaw.text for flaw in initialSample.find("flaws").findall("flaw")]
        self.code = [code.text for code in initialSample.find("codes").findall("code")]

        self.safeties = {}
        tree_safeties = initialSample.find("safeties").findall("safety")
        for safety in tree_safeties:
            # print("S: " + safety.get("flawType"))
            self.safeties[safety.get("flawType")] = {}
            self.safeties[safety.get("flawType")]["safe"] = 0
            self.safeties[safety.get("flawType")]["needQuote"] = 0
            self.safeties[safety.get("flawType")]["noQuote"] = 0
            self.safeties[safety.get("flawType")]["urlSafe"] = 0
            self.safeties[safety.get("flawType")]["errorSafe"] = 0

            if "XSS" in safety.get("flawType"):
                # Universal safe sanitizing (Cast & co)

                if safety.get("safe") is not None:
                    self.safeties[safety.get("flawType")]["safe"] = int(safety.get("safe"))

                # Rule that can be always sanitize (/!\ Format)
                self.safeties[safety.get("flawType")]["rule1"] = 0
                self.safeties[safety.get("flawType")]["rule2"] = 0
                self.safeties[safety.get("flawType")]["rule3"] = 0
                self.safeties[safety.get("flawType")]["rule4"] = 0
                self.safeties[safety.get("flawType")]["rule5"] = 0

                if safety.get("rule1") is not None:
                    self.safeties[safety.get("flawType")]["rule1"] = int(safety.get("rule1"))
                if safety.get("rule2") is not None:
                    self.safeties[safety.get("flawType")]["rule2"] = int(safety.get("rule2"))
                if safety.get("rule3") is not None:
                    self.safeties[safety.get("flawType")]["rule3"] = int(safety.get("rule3"))
                if safety.get("rule4") is not None:
                    self.safeties[safety.get("flawType")]["rule4"] = int(safety.get("rule4"))
                if safety.get("rule5") is not None:
                    self.safeties[safety.get("flawType")]["rule5"] = int(safety.get("rule5"))

                self.addSafetyAttributes(initialSample)

            elif "Injection" in safety.get("flawType"):
                if safety.get("safe") is not None:
                    self.safeties[safety.get("flawType")]["safe"] = int(safety.get("safe"))
                if safety.get("needQuote") is not None:
                    self.safeties[safety.get("flawType")]["needQuote"] = int(safety.get("needQuote"))
                #elif safety.get("needQuote") == "-1":
                #    self.safeties[safety.get("flawType")]["noQuote"] = noQuote
                #else:
                #    self.safeties[safety.get("flawType")]["unsafe"] = unsafe

            elif "IDOR" in safety.get("flawType"):
                #self.safe = safe if safety.get("safe") == "1" else unsafe
                if safety.get("safe") is not None:
                    self.safeties[safety.get("flawType")]["safe"] = int(safety.get("safe"))
                #else:
                #    self.safeties[safety.get("flawType")]["unsafe"] = unsafe

            elif "URF" in safety.get("flawType"):
                if safety.get("urlSafe") is not None:
                    self.safeties[safety.get("flawType")]["urlSafe"] = int(safety.get("urlSafe"))
                if safety.get("safe") is not None:
                    self.safeties[safety.get("flawType")]["safe"] = int(safety.get("safe"))
                if safety.get("needQuote") is not None:
                    self.safeties[safety.get("flawType")]["needQuote"] = int(safety.get("needQuote"))
                #elif safety.get("needQuote") == "-1":
                #    self.safeties[safety.get("flawType")]["noQuote"] = noQuote
                #else:
                #    self.safeties[safety.get("flawType")]["unsafe"] = unsafe

            elif "SM" in safety.get("flawType"):
                if safety.get("errorSafe") is not None:
                    self.safeties[safety.get("flawType")]["errorSafe"] = int(safety.get("errorSafe"))
                if safety.get("safe") is not None:
                    self.safeties[safety.get("flawType")]["safe"] = int(safety.get("safe"))
                #else:
                #    self.safeties[safety.get("flawType")]["unsafe"] = unsafe
                #self.isSafe = safe if safety.get("safe") == "1" else unsafe

            elif "SDE" in safety.get("flawType"):
                #self.safe = safe if safety.get("safe") == "1" else unsafe
                if safety.get("safe") is not None:
                    self.safeties[safety.get("flawType")]["safe"] = int(safety.get("safe"))
                #else:
                #    self.safeties[safety.get("flawType")]["unsafe"] = unsafe

        constraints = initialSample.find("constraints").findall("constraint")
        for constraint in constraints:
            if "Injection" in constraint.get("flawType"):
                self.constraintType = constraint.get("type")
                self.constraintField = constraint.get("field")
            if "URF" in constraint.get("flawType"):
                self.constraintType = constraint.get("type")
                self.constraintField = constraint.get("field")
                # if "IDOR" in constraint.get("flawType"):
                # self.isBlock = block if safety.find("block") == "1" else noBlock


    def __str__(self):
        return "** Filtering ***\n\n{}\n\tflaws : {}\n\tsafeties : {}\n\tconstraint : type {}, field {}\n\tcode : {}\n".format("TODO super", self.flaws, self.safeties, self.constraintType, self.constraintField, self.code)
