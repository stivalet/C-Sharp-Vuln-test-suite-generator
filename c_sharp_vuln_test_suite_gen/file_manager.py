"""
FileManager Class (TODO DOC)
"""

import os


class FileManager(object):

    def __init__(self, filename, dir_name, flaw_group, flaw_type, is_safe, content):
        self.filename = filename
        """ The filename of current test case """
        self.dir_name = dir_name
        """ The directory of current test case """
        self.flaw_group = flaw_group
        """ Flaw group of current test case """
        self.flaw_type = flaw_type
        """ Flaw type of current test case """
        self.safe = "safe" if is_safe else "unsafe"
        """ If true the current test case is safe """
        self.content = content
        """ Code of current test case """
        self.path = dir_name + "/" + flaw_group + "/" + flaw_type + "/" + self.safe + "/"
        """ Path of current test case """

    def createFile(self, debug=False):
        """ Create the file with code on them """
        # check if the directory exists
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        # create the file
        createdFile = open(self.path + "/" + self.filename, "w")
        # write code
        createdFile.write(self.content)
        createdFile.close()
        if debug:
            print("file : "+self.filename+" created")

    _xml = {
        "input": "input.xml",
        "filtering": "filtering.xml",
        "sink": "sink.xml",
        "exec_queries": "exec_queries.xml",
        "file_template": "file_template.xml",
        "complexities": "complexities.xml",
    }

    @classmethod
    def getXML(cls, xmlfile, language="cs"):
        """ Return the path to selected xml file for the specified language """
        return "c_sharp_vuln_test_suite_gen/templates/" + language + "/" + cls._xml[xmlfile]

    # Getters and setters
    def setPath(self, path):
        self.path = path

    def addPath(self, path):
        self.path += "/" + path

    def getPath(self):
        return self.path

    def setName(self, filename):
        self.filename = filename

    def getName(self):
        return self.filename

    def addContent(self, content):
        self.content += content
