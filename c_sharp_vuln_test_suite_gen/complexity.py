import copy


class ComplexitySample:

    def __init__(self, xml_compl):
        self._code = xml_compl.find("code").text
        self._type = xml_compl.get("type").lower()
        self._group = xml_compl.get("group").lower()
        self._executed = xml_compl.get("executed").lower()
        self._need_condition = False
        if "condition" in self._executed or self._group == "conditionals" or xml_compl.get("need_condition") == "1":
            self._need_condition = True
        self._need_id = False
        if xml_compl.get("need_id") == "1":
            self._need_id = True

    def __str__(self):
        return "*** Complexity ***\n\ttype : {}\n\tgroup : {}\n\texecuted : {}\n\tcode : {}\n\
            \n".format(self.type,
                       self.group,
                       self.is_executed(),
                       self.code)

    @property
    def need_id(self):
        return self._need_id

    def need_condition(self):
        return self._need_condition

    def set_condition(self, condition):
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

    @code.setter
    def code(self, value):
        self._code = value

    def is_executed(self):
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
