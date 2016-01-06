
class ExecQuerySample:

    # new version for new XML
    def __init__(self, sample):  # XML tree in parameter

        self.type = sample.get("type")
        self.code = sample.find("code").text

    def __str__(self):
        return "*** ExecQuery ***\n{}\n\type : {}\n\tcode : {}\n\
            \n".format(self.type,
                       self.get_code())

    def get_type(self):
        return self.type

    def get_code(self):
        return self.code[0]
