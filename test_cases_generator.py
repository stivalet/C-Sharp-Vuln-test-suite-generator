import sys
import getopt
import time
from c_sharp_vuln_test_suite_gen.generator import Generator


def main(argv):
    debug = False
    safe = True
    unsafe = True
    date = time.strftime("%m-%d-%Y_%Hh%Mm%S")
    g = Generator(date)

    # List of flaws
    flaw_list = g.get_group_list()
    flaw_group_user = []
    cwe_list = g.get_cwe_list()
    flaw_type_user = []

    # Gets options & arguments
    try:
        opts, args = getopt.getopt(argv, "dusc:r:g:f:h", ["max_recursion=", "number_generated=", "debug", "unsafe",
                                                          "safe", "cwe=", "flaws=", "help"])
    except getopt.GetoptError:
        print('Invalid argument')
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-f", "--flaws"):  	# Select flaws
            flaw_group_user = [x.lower() for x in arg.split(',')]
        elif opt in ("-c", "--cwe"):	 # Select CWEs
            flaw_type_user = arg.split(',')
        elif opt in ("-s", "--safe"):
            safe = True
            unsafe = False
        elif opt in ("-u", "--unsafe"):
            unsafe = True
            safe = False
        elif opt in ("-d", "--debug"):
            debug = True
        elif opt in ("-h", "--help"):  	# Show usage
            usage()
            return 0
        elif opt in ("-r", "--max_recursion"):
            g.max_recursion = int(arg)
        elif opt in ("-g", "--number_generated"):
            g.number_generated = int(arg)
        else:				# Default
            usage()
            return 0

    # check -f param
    for flaw in flaw_group_user:
        if flaw.lower() not in flaw_list:
            usage()
            return 0

    # check -c param
    for cwe in flaw_type_user:
        if cwe not in cwe_list:
            usage()
            return 0

    # set user list
    g.set_flaw_type_user(flaw_type_user)
    g.set_flaw_group_user(flaw_group_user)

    # run generation
    g.generate(debug=debug, generate_safe=safe, generate_unsafe=unsafe)


# TODO:90 update at the end of project
def usage():
    flaw = "-f flaws to generate (flaw1,flaw2,flaw3,...):\
                \n\tIDOR      :\tInsecure Direct Object Reference\
                \n\tInjection :\tInjection (SQL,LDAP,XPATH)\
                \n\tSDE       :\tSensitive Data Exposure\
                \n\tSM        :\tSecurity Misconfiguration\
                \n\tURF       :\tURL Redirects and Forwards\
                \n\tXSS       :\tCross-site Scripting\
                \n\tMFE       :\tMalicious File Execution\
                \n\tICS       :\tInsecure Cryptographic Storage"

    cweparams = "-c generate particular CWE:\
                    \n\t22        :\tPath Traversal\
                    \n\t78        :\tCommand OS Injection\
                    \n\t79        :\tXSS\
                    \n\t89        :\tSQL Injection\
                    \n\t90        :\tLDAP Injection\
                    \n\t91        :\tXPath Injection\
                    \n\t95        :\tCode Injection\
                    \n\t98        :\tFile Injection\
                    \n\t209       :\tInformation Exposure Through an Error Message\
                    \n\t311       :\tMissing Encryption of Sensitive Data\
                    \n\t327       :\tUse of a Broken or Risky Cryptographic Algorithm\
                    \n\t601       :\tURL Redirection to Untrusted Site\
                    \n\t862       :\tInsecure Direct Object References"

    example = "Exemple :\
               \n\t$python3 test_cases_generator.py -f Injection \t// generate test cases with Injection flaws\
               \n\t$python3 test_cases_generator.py -c 79 \t\t// generate test cases with cross site scripting."
    print("\nusage: [-r max_recursion | -g number_generated | -f flaw | -c cwe ] [arg]\nOptions and arguments:\n\n{}\n\n{}\n\n{}\n"
          .format(flaw, cweparams, example))


if __name__ == "__main__":
    main(sys.argv[1:])
