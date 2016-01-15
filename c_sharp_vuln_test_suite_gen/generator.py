import shutil
from jinja2 import Template, DebugUndefined
from c_sharp_vuln_test_suite_gen.manifest import Manifest
from c_sharp_vuln_test_suite_gen.file_manager import FileManager
from c_sharp_vuln_test_suite_gen.input_sample import InputSample
from c_sharp_vuln_test_suite_gen.filtering_sample import FilteringSample
from c_sharp_vuln_test_suite_gen.sink_sample import SinkSample
from c_sharp_vuln_test_suite_gen.exec_query import ExecQuerySample
from c_sharp_vuln_test_suite_gen.complexity import ComplexitySample
from c_sharp_vuln_test_suite_gen.condition import ConditionSample
from c_sharp_vuln_test_suite_gen.file_template import FileTemplate

import xml.etree.ElementTree as ET


class Generator():

    MAX_RECURSION = 2
    # HACK  >=0 : generate NUMBER_GENERATE of trio (input,filtering,sink) , -1 : unlimited
    NUMBER_GENERATE = -1


    def __init__(self, date):
        self.date = date
        self.dir_name = "CsharpTestSuite_"+date
        # TODO:60 readd this for manifest generation
        # self.manifest = Manifest(date, flaw)
        self.safe_Sample = 0
        self.unsafe_Sample = 0
        self.flaw_type_user = None
        self.flaw_group_user = None

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
        tree_condition = ET.parse(FileManager.getXML("complexities")).getroot()
        self.tab_condition = [ConditionSample(condition) for condition in tree_condition.find("conditions")]

        self.file_template = FileTemplate(ET.parse(FileManager.getXML("file_template")).getroot())

        # set current samples
        self.current_input = None
        self.current_filtering = None
        self.current_sink = None
        self.current_exec_queries = None
        self.current_code = None
        self.complexities_queue = []
        # HACK
        self.number_generate = Generator.NUMBER_GENERATE

    def generate(self, debug=False, generate_safe=True, generate_unsafe=True):
        self.debug = debug
        self.generate_safe = generate_safe
        self.generate_unsafe = generate_unsafe
        self.select_sink()

    # fist step : browse sink
    def select_sink(self):
        for sink in self.tab_sink:
            if ((not self.flaw_type_user or sink.flaw_type_number() in self.flaw_type_user)
               and (not self.flaw_group_user or sink.flaw_group in self.flaw_group_user)):
                self.current_sink = sink
                self.select_filtering()

    # second step : browse filtering
    def select_filtering(self):
        # select filtering
        for filtering in self.tab_filtering:
            self.current_filtering = filtering
            # check if sink and filtering are compatibles
            if filtering.compatible_with_sink(self.current_sink):
                self.select_input()

    # third step : browse input
    def select_input(self):
        # select input
        for inp in self.tab_input:
            if inp.compatible_with_filtering_sink(self.current_filtering, self.current_sink):
                self.current_input = inp
                self.select_exec_queries()

    # fourth step : browse exec_queries
    def select_exec_queries(self):
        if self.current_sink.need_exec():
            # select exec_queries
            for exec_query in self.tab_exec_queries:
                if self.current_sink.compatible_with_exec_queries(exec_query):
                    self.current_exec_queries = exec_query
                    self.recursion_level()
        else:
            self.current_exec_queries = None
            self.recursion_level()

    # fouth step : compute recursion level
    def recursion_level(self):
        # HACK
        if self.number_generate == 0:
            return
        self.number_generate -= 1

        # generate with 0,1,2,... level of complexities
        for i in range(0, Generator.MAX_RECURSION+1):
            self.current_max_rec = i
            self.current_complexity_number = 1
            self.select_complexities(i)

    # fifth step bis : browse complexities
    def select_complexities(self, level):
        if level == 0:
            self.compose_complexities()
        else:
            # Select complexity for this level
            for complexity in self.tab_complexity:
                curr_complexity = complexity.clone()
                # add current complexity
                self.complexities_queue.append(curr_complexity)
                # pretraitment per type before recursive call
                # Conditionnals
                if curr_complexity.group == "conditionals":
                    if curr_complexity.type == "if":
                        self.need_condition(curr_complexity, level)

                # Jumps
                if curr_complexity.group == "jumps":
                    if curr_complexity.type == "goto":
                        self.need_condition(curr_complexity, level)

                # Loops
                if curr_complexity.group == "loops":
                    if curr_complexity.type == "for":
                        self.need_condition(curr_complexity, level)
                    if curr_complexity.type == "while":
                        self.need_condition(curr_complexity, level)

                # remove current complexity
                self.complexities_queue.pop()

    def need_condition(self, curr_complexity, level):
        if curr_complexity.need_condition():
            svg_cmpl = curr_complexity.code
            # add tabulation for indent
            # for the beauty of python :)
            # svg_cmpl = ''.join([''.join(['\t'*(self.current_max_rec - level), x.strip(), '\n']) for x in svg_cmpl.split('\n')])
            svg_cmpl = ('\n'+'\t'*(self.current_max_rec - level)).join(svg_cmpl.splitlines())
            for cond in self.tab_condition:
                curr_complexity.set_condition(cond.value)
                t = Template(svg_cmpl, undefined=DebugUndefined)
                curr_complexity.code = t.render(condition=cond.code)
                # recursive call
                self.select_complexities(level-1)
        else:
            self.select_complexities(level-1)

    # compose previous selected complexities
    def compose_complexities(self):
        self.compose()

    # seventh step : compose previous code chunks
    def compose(self):
        id_num = 0
        var_num = 0
        var_name = {}
        # temporary code
        template = Template(self.file_template.code)

        # if we need to add complexities on input, filtering and sink
        # TODO add complexity for input and/or filtering and/or sink
        # now just filtering
        # COMPLEXITIES
        self.current_complexity = "{{placeholder}}"
        self.executed = True
        for c in self.complexities_queue:
            # put complexity i+1 into i
            self.executed = self.executed and c.is_executed()
            t = Template(self.current_complexity, undefined=DebugUndefined)
            self.current_complexity = t.render(placeholder=c.code, id=id_num)
            t = Template(self.current_complexity, undefined=DebugUndefined)
            self.current_complexity = t.render(id=id_num)
            if c.need_id:
                id_num += 1

        # check if we need to generate (if it's only safe/unsafe generation)
        if (self.is_safe_selection() and not self.generate_safe) or (not self.is_safe_selection() and not self.generate_unsafe):
            return

        # INPUT
        input_code = self.current_input.code
        # set output var name
        if self.current_input.output_type is not "none":
            name = "tainted_"+str(var_num)
            input_code = Template(input_code).render(out_var_name=name, id=id_num)
            if self.current_input.output_type not in var_name:
                var_name[self.current_input.output_type] = set()
            var_name[self.current_input.output_type].add(name)
        if self.current_input.need_id:
            id_num += 1


        # FILTERING
        t = Template(self.current_complexity)
        filtering_code = t.render(placeholder=self.current_filtering.code)
        # set input var name
        if self.current_filtering.input_type is not "none":
            name = "tainted_"+str(var_num)
            filtering_code = Template(filtering_code, undefined=DebugUndefined).render(in_var_name=name, id=id_num)
            if self.current_filtering.input_type not in var_name:
                var_name[self.current_filtering.input_type] = set()
            var_name[self.current_filtering.input_type].add(name)
            var_num += 1
        # set output var name
        if self.current_filtering.output_type is not "none":
            name = "tainted_"+str(var_num)
            filtering_code = Template(filtering_code, undefined=DebugUndefined).render(out_var_name=name, id=id_num)
            if self.current_filtering.output_type not in var_name:
                var_name[self.current_filtering.output_type] = set()
            var_name[self.current_filtering.output_type].add(name)
        if self.current_filtering.need_id:
            id_num += 1

        # SINK
        sink_code = self.current_sink.code

        # set input var name
        if self.current_sink.input_type is not "none":
            sink_code = Template(sink_code, undefined=DebugUndefined).render(in_var_name="tainted_"+str(var_num), id=id_num)
            if self.current_sink.input_type not in var_name:
                var_name[self.current_sink.input_type] = set()
            var_name[self.current_sink.input_type].add(name)
        if self.current_sink.need_id:
            id_num += 1

        # EXEC QUERIES
        exec_queries_code = ""
        if self.current_exec_queries:
            exec_queries_code = self.current_exec_queries

        # LOCAL VARS
        local_var_code = ""
        for t in var_name:
            init = ""
            if t == "string":
                local_var_code += "string "
                init = "null"
            elif t == "int":
                local_var_code += "int "
                init = "0"
            else:
                local_var_code += "//ERROR type '" + t + "' "
            for i, n in enumerate(list(var_name[t])):
                local_var_code += n + " = "+init
                if i < len(var_name[t])-1:
                    local_var_code += ", "
                else:
                    local_var_code += ";\n"

        # TODO SEE IF USEFUL
        flaw_str = ""
        if not self.is_safe_selection():
            flaw_str = "//flaw"

        # LICENCE
        license_content = open("rights.txt", "r").read()

        # IMPORTS
        imports_content = set(self.current_input.imports).union(set(self.current_filtering.imports)).union(
            set(self.current_sink.imports))
        comments_code = "\n".join([self.current_input.comment, self.current_filtering.comment,
                                   self.current_sink.comment])
        imports_content = "\n".join(["using {};".format(import_content) for import_content in imports_content])

        # COMPOSE TEMPLATE
        file_content = template.render(license=license_content, comments=comments_code,
                                       stdlib_imports=imports_content,
                                       namespace_name="default_namespace", main_name="MainClass",
                                       local_var=local_var_code,
                                       input_content=input_code,
                                       filtering_content=filtering_code,
                                       sink_content=sink_code,
                                       flaw=flaw_str,
                                       exec_queries_content=exec_queries_code)

        self.current_code = file_content
        self.write_files()

    # eighth step : write on disk and update manifest
    def write_files(self):
        filename = self.generate_file_name()
        filemanager = FileManager(filename, self.dir_name,
                                  self.current_sink.flaw_group.upper(),
                                  self.current_sink.flaw_type,
                                  self.is_safe_selection(),
                                  self.current_code)
        filemanager.createFile()
        # TODO:60 update Manifest
        # self.manifest.addFileToTestCase(self.current_sink.flaw_group)

    def get_group_list(self):
        return {sink.flaw_group.upper() for sink in self.tab_sink}

    def get_cwe_list(self):
        return {sink.flaw_type_number() for sink in self.tab_sink}

    def is_safe_selection(self):
        return (self.current_input.is_safe(self.current_sink.flaw_type)
                or (self.current_filtering.is_safe(self.current_sink.flaw_type) and self.executed)
                or (self.current_sink.safe))

    def set_flaw_type_user(self, value):
        self.flaw_type_user = value

    def set_flaw_group_user(self, value):
        self.flaw_group_user = value

    def generate_file_name(self):
        # CWE input filtering sink [exec] complexity
        name = self.current_sink.flaw_type
        name += "__"
        name += self.current_input.generate_file_name()
        name += "__"
        name += self.current_filtering.generate_file_name()
        name += "__"
        name += self.current_sink.generate_file_name()

        if self.current_exec_queries is not None:
            name += "__"
            name += self.exec_query.type

        # TODO add complexity
        name += "__"
        name += str(self.current_max_rec) + "-" + str(self.current_complexity_number)
        self.current_complexity_number += 1
        # extension
        name += "."+self.file_template.file_extension
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
