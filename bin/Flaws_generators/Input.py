from .InitializeSample import InitialSample

class InputSample(InitialSample):  # Initialize the type of input and the code parameters of the class
    # compatible with new structure
    def __init__(self, initialSample):  # XML tree in parameter
        InitialSample.__init__(self, initialSample)
        self.inputType = initialSample.find("inputType").text
        self.code = initialSample.find("code").text
