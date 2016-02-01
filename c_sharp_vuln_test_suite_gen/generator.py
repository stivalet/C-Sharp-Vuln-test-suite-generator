import time
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
from c_sharp_vuln_test_suite_gen.complexities_generator import ComplexitiesGenerator

import xml.etree.ElementTree as ET


class Generator(object):

    UID = 0

    def __init__(self, date):
        self._max_recursion = 1
        self._number_generated = -1
        self.date = date
        self.dir_name = "CsharpTestSuite_"+date
        self.manifest = Manifest(self.dir_name, self.date)
        self.safe_sample = 0
        self.unsafe_sample = 0
        self.report = {}
        self.flaw_type_user = None
        self.flaw_group_user = None
        self.start = time.time()
        self.end = 0

        self.uid = 0

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
        self.map_CWE_group = {}

    def getUID():
        Generator.UID += 1
        return Generator.UID

    def generate(self, debug=False, generate_safe=True, generate_unsafe=True):

        self.create_map_CWE_group()
        self.manifest.createManifests(self.get_groups_to_generate())
        self.debug = debug
        self.generate_safe = generate_safe
        self.generate_unsafe = generate_unsafe
        self.select_sink()
        self.generation_report()

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
        if self.number_generated == 0:
            return
        self.number_generated -= 1

        # generate with 0,1,2,... level of complexities
        max_rec = self.max_recursion if self.current_sink.need_complexity else 0
        for i in range(0, max_rec+1):
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
                    if curr_complexity.type == "switch":
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
                    if curr_complexity.type == "foreach":
                        var_type = self.current_input.output_type
                        curr_complexity.code = Template(curr_complexity.code, undefined=DebugUndefined).render(id=level, var_type=var_type)
                        self.need_condition(curr_complexity, level)

                if curr_complexity.group == "functions":
                    if curr_complexity.type == "function":
                        self.need_condition(curr_complexity, level)
                if curr_complexity.group == "classes":
                    if curr_complexity.type == "class":
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
                curr_complexity.set_cond_id(cond.id)
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
        var_id = 0
        var_name = {}
        # temporary code

        # if we need to add complexities on input, filtering and sink
        # TODO add complexity for input and/or filtering and/or sink
        # now just filtering

        # COMPLEXITIES
        compl_gen = ComplexitiesGenerator(complexities_array=self.complexities_queue, template_code=self.file_template.code, input_type=self.current_input.output_type, output_type=self.current_sink.input_type, filtering=self.current_filtering)
        self.classes_code = compl_gen.compose()
        classes_imports = []
        for c in self.classes_code:
            classes_imports.append(c['name'])
        self.executed = compl_gen.executed
        self.template_code = compl_gen.get_template()


        # check if we need to generate (if it's only safe/unsafe generation)
        if (self.is_safe_selection() and not self.generate_safe) or (not self.is_safe_selection() and not self.generate_unsafe):
            return

        # INPUT
        input_code = self.current_input.code
        # set output var name
        if self.current_input.output_type != "none":
            input_code = Template(input_code).render(out_var_name=compl_gen.in_ext_name, id=var_id)
        if self.current_input.need_id:
            var_id += 1

        # FILTERING
        # t = Template(self.current_complexity)
        # filtering_code = t.render(placeholder=self.current_filtering.code)
        # set input var name
        filtering_code = self.current_filtering.code
        in_name = ""
        out_name = ""
        if self.current_filtering.input_type != "none":
            in_name = compl_gen.in_int_name
        # set output var name
        if self.current_filtering.output_type != "none":
            out_name = compl_gen.out_int_name
        if self.current_filtering.need_id:
            var_id += 1
        filtering_code = Template(filtering_code, undefined=DebugUndefined).render(in_var_name=in_name, out_var_name=out_name, id=var_id)

        # SINK
        sink_code = self.current_sink.code

        # set input var name
        if self.current_sink.input_type != "none":
            sink_code = Template(sink_code, undefined=DebugUndefined).render(in_var_name=compl_gen.out_ext_name, id=var_id)

        if self.current_sink.need_id:
            var_id += 1

        # EXEC QUERIES
        exec_queries_code = ""
        if self.current_exec_queries:
            exec_queries_code = self.current_exec_queries.code

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
        license_content = ""
        if not self.debug:
            license_content = open("c_sharp_vuln_test_suite_gen/templates/cs_file_rights.txt", "r").read()

        # IMPORTS
        imports_content = set(self.current_input.imports).union(set(self.current_filtering.imports)).union(
            set(self.current_sink.imports))
        if self.current_exec_queries:
            imports_content = imports_content.union(set(self.current_exec_queries.imports))
        imports_content = "\n".join(["using {};".format(import_content) for import_content in imports_content])
        # comments code
        comments_code = "\n".join([self.current_input.comment, self.current_filtering.comment,
                                  self.current_sink.comment])

        # COMPOSE TEMPLATE
        template = Template(self.template_code)
        file_content = template.render(license=license_content, comments=comments_code,
                                       stdlib_imports=imports_content,
                                       namespace_name="default_namespace", main_name="MainClass",
                                       local_var=local_var_code,
                                       input_content=input_code,
                                       filtering_content=filtering_code,
                                       sink_content=sink_code,
                                       flaw=flaw_str,
                                       exec_queries_content=exec_queries_code)

        for i, cl in enumerate(self.classes_code):
            self.classes_code[i]['code'] = Template(cl['code']).render(filtering_content=filtering_code)

        self.current_code = file_content
        self.write_files()

    # eighth step : write on disk and update manifest
    def write_files(self):

        current_flaw_group = self.current_sink.flaw_group.lower()
        current_flaw = self.current_sink.flaw_type
        # Create main file
        filename = self.generate_file_name("File1")
        filemanager = FileManager(filename, self.dir_name,
                                  current_flaw_group,
                                  current_flaw,
                                  self.is_safe_selection(),
                                  self.current_code)
        filemanager.createFile()
        # Create other classes
        for i, cl in enumerate(self.classes_code):
            filename = self.generate_file_name("File"+str(i+2))
            filemanager = FileManager(filename, self.dir_name,
                                      current_flaw_group,
                                      current_flaw,
                                      self.is_safe_selection(),
                                      cl['code'])
            filemanager.createFile()


        if current_flaw_group not in self.report:
            self.report[current_flaw_group] = {}
        if current_flaw not in self.report[current_flaw_group]:
            self.report[current_flaw_group][current_flaw] = {}
            self.report[current_flaw_group][current_flaw]["safe_sample"] = 0
            self.report[current_flaw_group][current_flaw]["unsafe_sample"] = 0

        if self.is_safe_selection():
            self.report[current_flaw_group][current_flaw]["safe_sample"] += 1
        else:
            self.report[current_flaw_group][current_flaw]["unsafe_sample"] += 1

        full_path = filemanager.getPath() + filename
        self.manifest.addTestCase(self.current_input.input_type,
                                  current_flaw_group,
                                  current_flaw,
                                  Generator.findFlaw(full_path),
                                  full_path)

    def get_group_list(self):
        return {sink.flaw_group.lower() for sink in self.tab_sink}

    def get_cwe_list(self):
        return {sink.flaw_type_number() for sink in self.tab_sink}

    def get_uid(self):
        self.uid += 1
        return self.uid

    def is_safe_selection(self):
        return ((self.current_input.is_safe(self.current_sink.flaw_type)
                or (self.current_filtering.is_safe(self.current_sink.flaw_type) and self.executed))
                and (self.current_sink.safe))

    def set_flaw_type_user(self, value):
        self.flaw_type_user = value

    def set_flaw_group_user(self, value):
        self.flaw_group_user = value

    def create_map_CWE_group(self):
        for group in self.get_group_list():
            self.map_CWE_group[group.lower()] = []

        for cwe in self.tab_sink:
            self.map_CWE_group[cwe.flaw_group.lower()].append(cwe.flaw_type_number())

    def get_groups_to_generate(self):
        tmp = []
        if self.flaw_group_user:
            tmp = self.flaw_group_user

        for flaw in self.flaw_type_user:
                for group in self.map_CWE_group:
                    if flaw in self.map_CWE_group[group]:
                        tmp.append(group)

        if tmp:
            return list(set(tmp))  # remove duplicates
        else:
            return list(self.get_group_list())

    def generate_file_name(self, suffix):
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
            name += self.current_exec_queries.type

        # TODO add complexity
        name += "__"
        cplx_name = ""
        for c in self.complexities_queue:
            cplx_name += "-" + c.get_complete_id()

        name += str(self.current_max_rec) + str(cplx_name)
        # suffix
        name += "_"+suffix
        # extension
        name += "."+self.file_template.file_extension
        self.current_complexity_number += 1
        return name

    # TODO:20 move this elsewhere either in the generator either in a new class
    def generation_report(self):
        self.manifest.closeManifests()
        total = 0
        print("Generation report:\n")
        for flaw_group in self.report:
            group_total = 0
            print("\t" + flaw_group.upper() + " group generation report:\n")
            for flaw in self.report[flaw_group]:
                print("\t\t" + flaw.upper() + " generation report:\n")
                print("\t\t\t" + str(self.report[flaw_group][flaw]["safe_sample"]) + " safe samples")
                print("\t\t\t" + str(self.report[flaw_group][flaw]["unsafe_sample"]) + " unsafe samples")
                flaw_total = self.report[flaw_group][flaw]["safe_sample"] + self.report[flaw_group][flaw]["unsafe_sample"]
                group_total += flaw_total
                print("\n\t\t" + str(flaw_total) + " total\n")

            print("\t" + str(group_total) + " total\n")
            total += group_total

        print(str(total) + " total\n")
        self.end = time.time()
        print("Generation time " + time.strftime("%H:%M:%S", time.gmtime(self.end - self.start)))


    @staticmethod
    def findFlaw(fileName):
        sample = open(fileName, 'r')
        i = 0
        for line in sample.readlines():
            i += 1
            if line[:6] == "//flaw":
                break
        if i == len(sample.readlines()):
            return 0
        else:
            return i + 1

    @property
    def max_recursion(self):
        return self._max_recursion

    @max_recursion.setter
    def max_recursion(self, value):
        self._max_recursion = value

    @property
    def number_generated(self):
        return self._number_generated

    @number_generated.setter
    def number_generated(self, value):
        self._number_generated = value
