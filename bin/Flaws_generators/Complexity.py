

class ComplexitySample:

    def __init__(self, xml_compl):
        self.code = xml_compl.find("code").text
        self.type = xml_compl.get("type").lower()
        self.group = xml_compl.get("group").lower()

    def get_type(self):
        return self.type

    def get_group(self):
        return self.group
