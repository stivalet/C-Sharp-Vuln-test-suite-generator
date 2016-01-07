
class ExecQuerySample:

    # new version for new XML
    def __init__(self, sample):  # XML tree in parameter
        self.type = str(sample.get("type"))
        self.imports = []
        if sample.find("imports"):
            self.imports = [imp.text for imp in sample.find("imports").findall("import")]
        self.code = sample.find("code").text

    def __str__(self):
        return "*** ExecQuery ***\n\ttype : {}\n\timorts : {}\n\tcode : {}\n\
            \n".format(self.type,
                       self.imports,
                       self.get_code())

    def get_type(self):
        return self.type

    def get_code(self):
        return self.code[0]