import os

from .Generator_Abstract_Class import *
from .InitializeSample import *
from Classes.File import *

#select = 0
#order = 0
#safety = "safety"

#Constants
#safe = "safe"
#unsafe = "unsafe"

#Gets copyright header from file
header = open("./rights.txt", "r")
copyright = header.readlines()
header.close()

#def setRelevancy(R) :
#   global select
#   select = int(R)

#def setOrder(O) :
#   if O==1 :
#      global order
#      order = safety


#Manages final samples, by a combination of 3 initialSample
class GeneratorIDOR(Generator) :

    ##Initializes counters
    #safe_Sample = 0
    #unsafe_Sample = 0

    def __init__(self, manifest, fileManager, select, ordered):
        Generator.__init__(self, manifest, fileManager, select, ordered)

    #def __init__(self, manifest, fileManager, select, ordered):
    #    self.select = select
    #    self.ordered = ordered
    #    self.manifest = manifest
    #    self.fileManager = fileManager

    def getType(self):
        return ['SQL_IDOR', 'XPath_IDOR', 'Fopen']

    def testSafety(self, flaw, sanitize, construction) :
        if sanitize.safe == safe or construction.safe == safe :
            self.safe_Sample +=1
            return 1

        self.unsafe_Sample +=1
        return 0

    def findFlaw(self, fileName) :
       sample = open(fileName, 'r')
       i = 0
       for line in sample.readlines() :
          i += 1
          if line[:6] == "//flaw" :
             break
       return i + 1
	   
	#def testIsBlock(self) :
    #    if self.sanitize.isBlock == block :
    #        return 1
    #    return 0

    def testIsPrepared(self, construction) :
        if construct.prepared == prepared :
          return 1
        return 0

	def generate(self):
        self.generateWithType("fopen")
        self.generateWithType("SQL")
        self.generateWithType("XPath")
        self.manifest.close()   
	   
    #Generates final sample
    def generateWithType(self, IDOR) :
        #Gets query execution code
        #2 types normal query and prepared query
        fileQuery = open("./execQuery_"+IDOR+ ".txt", "r")
        execQuery = fileQuery.readlines()
        fileQuery.close()

        execQueryPrepared =""
        if IDOR == "SQL":
        	fileQuery = open("./execQuery_"+IDOR+ "_prepared.txt", "r")
        	execQueryPrepared = fileQuery.readlines()
        	fileQuery.close()
        
		for f in ET.parse(self.fileManager.getXML("construction")).getroot():
            flaw = Flaws(f)
            if injection+"_IDOR" in flaw.flaws:
                for s in ET.parse(self.fileManager.getXML("sanitize")).getroot():
                    sanitize = Sanitize(s)
                    if injection+"_IDOR" in sanitize.flaws:
                        for i in ET.parse(self.fileManager.getXML("input")).getroot():
                            Input = InputSample(i)
                            self.manifest.beginTestCase(Input.inputType)
                    		file = File()

							# test if the samples need to be generated
                            input_R = Input.relevancy
                            sanitize_R = sanitize.relevancy
                            file_R = flaw.relevancy

							#Relevancy test
							if(input_R * sanitize_R * construct_R < select) :
								continue
						
							#Build constraints
							safe = self.testSafety() #1 : safe ,0 : unsafe
							if IDOR=="SQL":
							    #block = self.testIsBlock() #1 : block, 0 : noBlock
			                    prepared = self.testIsPrepared() #1 : prepared, 0 : noPrepared

							#Creates folder tree and sample files if they don't exists
							file.addPath("generation")
							file.addPath("IDOR")
							file.addPath(IDOR)
					
							#sort by safe/unsafe
							if order == safety :
							   if safe :
								  path = path + "/safe"
							   else :
								  path = path + "/unsafe"

							for dir in self.construct.path :
								file.addPath(dir)

							for dir in self.input.path:
								file.addPath(dir)

							for i in range(len(self.sanitize.path)-1) :
								dir = self.sanitize.path[i]
								file.addPath(file)

							file.setName(sanitize.path[-1])

							#Adds comments
							file.addContent("<?php \n")
							file.addContent("/*\n")

							file.addContent("un" if !safe + "safe sample")  

							file.addContent(flaw.comment + "\n" 
								+ Input.comment + "\n" 
								+ sanitize.comment + "\n" 
								+ " */")

							#Writes copyright statement in the sample file
                            file.addContent("\n\n")
                            for line in copyright:
                                file.addContent(line)

                        	#Writes the code in the sample file
                            file.addContent("\n\n")
                            file.addContent(Input.code + "\n"
                                            + sanitize.code[0] + "\n"
                                            + flaw.code[0] + "\n\n")

							if prepare == 0:
								for line in execQuery :
									file.addContent(line)
							else:
								for line in execQueryPrepared :
									 file.addContent(line)

							#if IDOR=="XPath":
							#	for line in execQuery :
							#		 sample.write(line)
							#elif IDOR == "SQL":

							file.addContent("\n ?>")
							self.fileManager.createFile(file)

							 if safe:
                                flawLine = 0
                            else:
                                flawLine = self.findFlaw(file.getPath() + "/" + file.getName())

							self.manifest.addFileToTestCase(file.getPath() + "/" + file.getName(), flawLine)
                            self.manifest.endTestCase()