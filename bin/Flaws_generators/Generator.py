import shutil
from Classes.Manifest import Manifest
from .Input import InputSample
from .Filtering import FilteringSample
from .Sink import SinkSample
from .ExecQuery import ExecQuerySample
from Classes.FileManager import FileManager
from Classes.File import File
import xml.etree.ElementTree as ET


class Generator():

    def __init__(self, date):
        self.date = date
        # TODO
        # self.manifest = Manifest(date, flaw)
        self.safe_Sample = 0
        self.unsafe_Sample = 0
        # parse XML files
        tree_input = ET.parse(FileManager.getXML("input")).getroot()
        self.tab_input = [InputSample(inp) for inp in tree_input]
        tree_filtering = ET.parse(FileManager.getXML("filtering")).getroot()
        self.tab_filtering = [FilteringSample(filtering) for filtering in tree_filtering]
        tree_sink = ET.parse(FileManager.getXML("sink")).getroot()
        self.tab_sink = [SinkSample(sink) for sink in tree_sink]
        tree_exec_query = ET.parse(FileManager.getXML("exec_queries")).getroot()
        self.tab_exec_queries = [ExecQuerySample(exec_query) for exec_query in tree_exec_query]
        # set current samples
        self.current_input = None
        self.current_filtering = None
        self.current_sink = None
        self.current_exec_queries = None

    def is_safe_selection(self):
        return self.current_input.is_safe() or self.current_filtering.is_safe(self.current_sink.get_flaw_type()) or self.current_sink.is_safe()

    def generate(self):
        # TODO check params : ex CWE_XXX, URF, ...
        self.select_sink()

    def select_sink(self):
        for sink in self.tab_sink:
            # TODO check if sink need filtering or input
            # select filtering
            for filtering in self.tab_filtering:
                # check if sink and filtering are compatibles
                if sink.compatible_with(filtering):
                    # TODO check if filtering need input
                    # select input
                    for inp in self.tab_input:
                        if filtering.get_input_type() == inp.get_output_type():
                            self.current_input = inp
                            self.current_filtering = filtering
                            self.current_sink = sink
                            self.decorator()

    # TODO complexities
    def decorator(self):
        print("#########################")
        print("safe : "+str(self.is_safe_selection()))
        print(self.current_input)
        print(self.current_filtering)
        print(self.current_sink)

    def getType(self):
        pass

    def generateFileName(self, params, name):
        for param in params:
            name += "__"
            for dir in param.path:
                    name += dir+"-"
            name = name[:-1]
        return name

    def onDestroy(self, flaw):
        self.manifest.close()
        if self.safe_Sample+self.unsafe_Sample > 0:
            print(flaw + " generation report:")
            print(str(self.safe_Sample) + " safe samples")
            print(str(self.unsafe_Sample) + " unsafe samples")
            print(str(self.unsafe_Sample + self.safe_Sample) + " total\n")
        else:
            shutil.rmtree("../CsharpTestSuite_"+self.date+"/"+flaw)

    @staticmethod
    def findFlaw(fileName):
        sample = open(fileName, 'r')
        i = 0
        for line in sample.readlines():
            i += 1
            if line[:6] == "//flaw":
                break
        return i + 1
