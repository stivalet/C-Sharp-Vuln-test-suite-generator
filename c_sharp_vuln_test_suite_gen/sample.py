

class Sample:  # Initialize path and comment
    # compatible with new structure
    def __init__(self, sample):  # XML tree in parameter
        self._path = []
        tree_path = sample.find("path").findall("dir")
        for dir in tree_path:
            self.path.append(dir.text)

        self._comment = sample.find("comment").text

        self._imports = []
        if sample.find("imports"):
            self._imports = [imp.text for imp in sample.find("imports").findall("import")]

        self._need_id = False
        if sample.get("need_id") == "1":
            self._need_id = True

    def __str__(self):
        return "\tpath : {}\n\tcomment : {}\n\timports : {}\
                ".format(self.path,
                         self.comment,
                         self.imports)

    @property
    def need_id(self):
        return self._need_id

    def generate_file_name(self):
        name = ""
        for directory in self.path:
            name += directory+"-"
        name = name[:-1]
        return name

    @property
    def path(self):
        return self._path

    @property
    def imports(self):
        return self._imports

    @imports.setter
    def imports(self, value):
        self._imports = value

    @property
    def comment(self):
        return self._comment
