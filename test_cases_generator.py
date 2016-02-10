""" Test Cases Generator

Usage:
    test_cases_generator.py
    test_cases_generator.py [-f FLAW_GROUP ...] [-c CWE ...] [-r DEPTH] [-g NUMBER_GENERATED] [-s | -u] [-d]
    test_cases_generator.py (-h | --help)
    test_cases_generator.py (-d | --debug)
    test_cases_generator.py --version


Options:
    -h, --help                                                    Show this message
    --version                                                     Show version
    -f FLAW_GROUP --flaw-group=FLAW_GROUP                  Generate files with vulnerabilities concerning the specified  flaw group, from the OWASP Top Ten (can be repeated)
    -c CWE --cwe=CWE                                          Generate files with vulnerabilities concerning the specified CWE (can be repeated)
    -s --safe                                                    Generate the safe samples
    -u --unsafe                                                  Generate the unsafe samples
    -d --debug                                                   Debug Mode
    -r DEPTH --depth=DEPTH                                 Depth of the Complexities (Default: 1)
    -g NUMBER_GENERATED --number-generated=NUMBER_GENERATED   Number of combination of input, filtering and sink used to generate (Default: -1, it means all)

List of flaw groups:
    \n\tIDOR      \tInsecure Direct Object Reference\
    \n\tInjection \tInjection (SQL,LDAP,XPATH)\
    \n\tSDE       \tSensitive Data Exposure\
    \n\tSM        \tSecurity Misconfiguration\
    \n\tURF       \tURL Redirects and Forwards\
    \n\tXSS       \tCross-site Scripting\
    \n\tMFE       \tMalicious File Execution\
    \n\tICS       \tInsecure Cryptographic Storage\
    \n\tUCWKV     \tUsing Components With Known Vulnerabilities

List of CWEs:
    \n\t22        \tPath Traversal\
    \n\t78        \tCommand OS Injection\
    \n\t79        \tXSS\
    \n\t89        \tSQL Injection\
    \n\t90        \tLDAP Injection\
    \n\t91        \tXPath Injection\
    \n\t95        \tCode Injection\
    \n\t98        \tFile Injection\
    \n\t209       \tInformation Exposure Through an Error Message\
    \n\t311       \tMissing Encryption of Sensitive Data\
    \n\t327       \tUse of a Broken or Risky Cryptographic Algorithm\
    \n\t476       \tNULL Pointer Dereference
    \n\t601       \tURL Redirection to Untrusted Site\
    \n\t862       \tInsecure Direct Object References"

Examples:

    test_cases_generator.py                         (generate files with all CWE registered, safe and unsafe, complexity depth = 1)
    test_cases_generator.py -f IDOR                 (generate files with all CWE belonging to IDOR group, and other options to default)
    test_cases_generator.py -f IDOR -f Injection    (generate files with all CWE belonging to IDOR group and Injection)
    test_cases_generator.py -c 89                   (generate files with the CWE 354)
    test_cases_generator.py -c 89 -c 78             (generate files with the CWE 89 and CWE 78)
    test_cases_generator.py -r 2                    (generate all files with the complexity depth equals to 2, two level of imbrication)
    test_cases_generator.py -g 1                    (generate all files with only one combination of input, filtering and sink for all CWE)
    test_cases_generator.py -s                      (generate all files where the vulnerabilities have been fixed)
    test_cases_generator.py -u                      (generate all files where there is still vulnerabilities)

    All these options can be combinated (except for -s and -u).

    For example:

        test_cases_generator.py -c 78 -f IDOR -r 1 -g 1 -s
"""


import sys
import time
from docopt import docopt
from c_sharp_vuln_test_suite_gen.generator import Generator


def main():
    debug = False
    safe = True
    unsafe = True
    date = time.strftime("%m-%d-%Y_%Hh%Mm%S")
    g = Generator(date, language="php")

    # List of flaws
    flaw_list = g.get_group_list()
    cwe_list = g.get_cwe_list()

    args = docopt(__doc__, version='0.1')

    flaw_group_user = [x.lower() for x in args["--flaw-group"]]
    for flaw in flaw_group_user:
        if flaw.lower() not in flaw_list:
            print("There is no flaws associated with the given flaw group (-f {} option).\
                  See --help.".format(flaw.lower()))
            return 0
    try:
        flaw_type_user = [int(x) for x in args["--cwe"]]
    except ValueError:
        print("Invalid format. Value of the -c option must be an integer. See --help")
        sys.exit(1)
    for cwe in flaw_type_user:
        if cwe not in cwe_list:
            print("There is no flaws associated with the given CWE (-c {} option). See --help.".format(cwe))
            return 0
    if args["--safe"]:
        safe = True
        unsafe = False
    if args["--unsafe"]:
        safe = False
        unsafe = True
    debug = args["--debug"]
    try:
        arg = args["--depth"]
        g.max_recursion = int(arg) if arg is not None else 1
    except ValueError:
        print("Invalid format. Value of the -r option must be an integer. See --help")
        sys.exit(1)
    try:
        arg = args["--number-generated"]
        g.number_generated = int(arg) if arg is not None else -1
    except ValueError:
        print("Invalid format. Value of the -l option must be 'cs' or 'php'. See --help")
        sys.exit(1)

    # set user list
    g.set_flaw_type_user(flaw_type_user)
    g.set_flaw_group_user(flaw_group_user)

    # run generation
    g.generate(debug=debug, generate_safe=safe, generate_unsafe=unsafe)


if __name__ == "__main__":
    main()
