import copy


class ComplexitySample:

    def __init__(self, xml_compl):
        self._code = xml_compl.find("code").text
        self._type = xml_compl.get("type").lower()
        self._group = xml_compl.get("group").lower()
        self._executed = xml_compl.get("executed").lower()

    def need_condition(self):
        if self._group == "conditional":
            return True
        return False

    def set_contition(self, condition):
        self.condition = condition

    @property
    def type(self):
        return self._type

    @property
    def group(self):
        return self._group

    @property
    def code(self):
        return self._code

    @property
    def executed(self):
        if self._executed == "condition":
            return self.condition
        elif self._executed == "not_condition":
            return not self.condition
        elif self._executed == "1":
            return True
        elif self._executed == "0":
            return False
        return False

    def clone(self):
        return copy.deepcopy(self)