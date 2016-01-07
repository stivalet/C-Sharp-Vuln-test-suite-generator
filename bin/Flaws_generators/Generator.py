import shutil
from Classes.Manifest import Manifest
from .Input import InputSample
from .Filtering import FilteringSample
from .Sink import SinkSample
from .ExecQuery import ExecQuerySample
from .Complexity import ComplexitySample
from .MainClass import MainClassSample
from Classes.FileManager import FileManager
import xml.etree.ElementTree as ET


class Generator():

    MAX_RECURSION = 1
    # HACK  >=0 : generate NUMBER_GENERATE of trio (input,filtering,sink) , -1 : unlimited
    NUMBER_GENERATE = -1

    def __init__(self, date):
        self.date = date
        # TODO:60 readd this for manifest generation
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
        tree_complexities = ET.parse(FileManager.getXML("complexities")).getroot()
        self.tab_complexity = [ComplexitySample(complexity) for complexity in tree_complexities.find("complexities")]
        self.main_class = MainClassSample(ET.parse(FileManager.getXML("main_class")).getroot())
        # set current samples
        self.current_input = None
        self.current_filtering = None
        self.current_sink = None
        self.current_exec_queries = None
        self.current_code = None
        # HACK
        self.number_generate = Generator.NUMBER_GENERATE

    def get_group_list(self):
        return {sink.flaw_group.upper() for sink in self.tab_sink}

    def get_cwe_list(self):
        return {sink.flaw_type[4:] for sink in self.tab_sink}

    def is_safe_selection(self):
        return (self.current_input.is_safe(self.current_sink.flaw_type)
                or self.current_filtering.is_safe(self.current_sink.flaw_type) or
                self.current_sink.safe)

    def generate(self):
        # TODO:50 check params : ex CWE_XXX, URF, ...
        self.select_sink()

    # fist step : browse sink
    def select_sink(self):
        for sink in self.tab_sink:
            self.current_sink = sink
            # TODO:40 check if sink need filtering or input
            self.select_filtering()

    # second step : browse filtering
    def select_filtering(self):
        # select filtering
        for filtering in self.tab_filtering:
            self.current_filtering = filtering
            # check if sink and filtering are compatibles
            if filtering.compatible_with_sink(self.current_sink):
                # TODO:30 check if filtering need input
                self.select_input()

    # third step : browse input
    def select_input(self):
        # select input
        for inp in self.tab_input:
            if inp.compatible_with_filtering_sink(self.current_filtering, self.current_sink):
                self.current_input = inp
                self.recursion_level()

    # fouth step : compute recursion level
    def recursion_level(self):
        # HACK
        if self.number_generate == 0:
            return
        self.number_generate -= 1

        for i in range(0, Generator.MAX_RECURSION+1):
            self.select_complexities(i)

    # fourth step bis : browse complexities
    def select_complexities(self, level):
        print(level)
        if level == 0:
            self.select_exec_queries()
        else:
            # Select complexity for this level
            for complexity in self.tab_complexity:
                self.select_complexities(level-1)

    # fifth step : browse exec_queries
    def select_exec_queries(self):
        if self.current_sink.need_exec():
            # select exec_queries
            for exec_query in self.tab_exec_queries:
                if self.current_sink.compatible_with_exec_queries(exec_query):
                    self.current_exec_queries = exec_query
                    self.compose()
        else:
            self.current_exec_queries = None
            self.compose()

    # seventh step : compose previous code chunks
    def compose(self):
        # TODO:70 replace placeholder on complexities by input/filtering/sink/exec_queries
        # temporary code
        self.current_code = ""
        self.current_code += str(self.current_input.code)
        self.current_code += str(self.current_filtering.code)
        self.current_code += str(self.current_sink.code)
        if self.current_exec_queries:
            self.current_code += str(self.current_exec_queries.code)
        self.write_files()

    # eighth step : write on disk and update manifest
    def write_files(self):
        # TODO:80 write on file
        filename = self.generate_file_name()
        print(filename)
        print("#########################################")
        print("safe : "+str(self.is_safe_selection()))
        print(self.current_code)
        print("#########################################")
        # TODO:60 update Manifest
        # self.manifest.addFileToTestCase(self.current_sink.flaw_group)

    def getType(self):
        pass

    def generate_file_name(self):
        # CWE input filtering sink [exec] complexity
        name = self.current_sink.flaw_type
        name += "__"
        name += self.current_input.generate_file_name()
        name += "__"
        name += self.current_filtering.generate_file_name()
        name += "__"
        name += self.current_sink.generate_file_name()
        name += "."+self.main_class.file_extension

        if self.current_exec_queries is not None:
            name += "__"
            name += self.exec_query.type

        # TODO add complexity
        return name

    # TODO:20 move this elsewhere either in the generator either in a new class
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
