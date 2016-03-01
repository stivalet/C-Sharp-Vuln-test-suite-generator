"""
Complexity Class (TODO DOC)
"""

import copy
import c_sharp_vuln_test_suite_gen.generator


class ComplexitySample(object):

    def __init__(self, xml_compl):
        self._id = xml_compl.get("id")
        """ id of complexity """
        self._cond_id = None
        """ id of condition """
        self._code = xml_compl.find("code").text
        self._code = c_sharp_vuln_test_suite_gen.generator.Generator.remove_indent(self._code)
        """ code of complexity """
        self._type = xml_compl.get("type").lower()
        """ type of complexity (if, switch, for, function, classe, ...) """
        self._group = xml_compl.get("group").lower()
        """ group of complexity (conditionnals, loops, functions, classes, ...) """
        self._executed = xml_compl.get("executed").lower()
        """ if True the placeholder is executed """
        self._need_condition = False
        """ if True the complexity need a condition (set _cond_id) """
        if "condition" in self._executed or self._group == "conditionals" or xml_compl.get("need_condition") == "1":
            self._need_condition = True
        self._need_id = False
        """ if True the complexity need uniq id """
        if xml_compl.get("need_id") == "1":
            self._need_id = True
        self._in_out_var = False
        """ specify where is the placeholder in the complexity for variables name setting (in, trasversal, out) """
        if xml_compl.get("in_out_var"):
            self._in_out_var = xml_compl.get("in_out_var")
        self._indirection = ""
        """ if True, the complexity need to have a body """
        if xml_compl.get("indirection"):
            self._indirection = xml_compl.get("indirection")
        # TODO check if indirection is True, complexity need to have a body
        self._body = ""
        """ if specify, it's the second part of complexity """
        if xml_compl.find("body") is not None:
            self._body = xml_compl.find("body").text
            self._body = c_sharp_vuln_test_suite_gen.generator.Generator.remove_indent(self._body)


    def __str__(self):
        return "*** Complexity ***\n\ttype : {}\n\tgroup : {}\n\texecuted : {}\n\tcode : {}\n\
            \n".format(self.type,
                       self.group,
                       self.is_executed(),
                       self.code)

    @property
    def id(self):
        return self._id

    def get_complete_id(self):
        """ return the complete id of complexity (in case with conditional) """
        if self._cond_id:
            return self._id+"."+self._cond_id
        else:
            return self._id

    def set_cond_id(self, nb):
        self._cond_id = nb

    @property
    def body(self):
        return self._body

    @property
    def indirection(self):
        return self._indirection

    @body.setter
    def body(self, value):
        self._body = value

    @property
    def in_out_var(self):
        return self._in_out_var

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
        """ compute if the placeholder is executed """
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
