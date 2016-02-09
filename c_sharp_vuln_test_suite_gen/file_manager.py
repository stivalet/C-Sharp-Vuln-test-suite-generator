import os


class FileManager(object):

    def __init__(self, filename, dir_name, flaw_group, flaw_type, is_safe, content):
        self.filename = filename
        self.dir_name = dir_name
        self.flaw_group = flaw_group
        self.flaw_type = flaw_type
        self.safe = "safe" if is_safe else "unsafe"
        self.content = content
        self.path = dir_name + "/" + flaw_group + "/" + flaw_type + "/" + self.safe + "/"

    def createFile(self, debug=False):
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        createdFile = open(self.path + "/" + self.filename, "w")
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
