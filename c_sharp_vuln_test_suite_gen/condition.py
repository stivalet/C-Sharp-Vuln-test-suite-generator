"""
Condition Class (TODO DOC)
"""

class ConditionSample(object):

    def __init__(self, xml_cond):
        self._id = xml_cond.get("id")
        """ id of condition """
        self._code = xml_cond.find("code").text
        """ code of condition """
        self._value = xml_cond.find("value").text.lower() == "true"
        """ value of condition """

    @property
    def id(self):
        return self._id

    @property
    def code(self):
        return self._code

    @property
    def value(self):
        return self._value
