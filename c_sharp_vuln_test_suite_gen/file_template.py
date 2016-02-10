"""
FileTemplate Class (TODO DOC)
"""

class FileTemplate(object):

    def __init__(self, file_template):
        self._language_name = file_template.get("name")
        """ Name of language """
        self._file_extension = file_template.find("file_extension").text
        """ File extention """
        self._code = file_template.find("code").text
        """ Template code """
        self._comment = {}
        """ Structure for comment (inline, multiline)"""
        self._comment['open'] = file_template.find("comment").find("open").text
        self._comment['close'] = file_template.find("comment").find("close").text
        self._comment['inline'] = file_template.find("comment").find("inline").text
        self._prefix = file_template.find("variables").get("prefix")
        """ Variables prefix """
        self._variables = {}
        """ Identifier and initializer for variables """
        for v in file_template.find("variables"):
            self._variables[v.get("type")] = {"code": v.get("code"), "init": v.get("init")}

    @property
    def prefix(self):
        return self._prefix

    def get_type_var_code(self, type_v):
        """ Return the statement code of specified variable """
        if type_v in self._variables:
            return self._variables[type_v]["code"]
        else:
            return ""

    def get_init_var_code(self, type_v):
        """ Return the init code of specified variable """
        if type_v in self._variables:
            return self._variables[type_v]["init"]
        else:
            return ""


    @property
    def code(self):
        return self._code

    @property
    def file_extension(self):
        return self._file_extension

    @property
    def comment(self):
        return self._comment
