"""
OSCAAR/Code/differentialPhotometry.py

Calls differentialPhotometryExecutor to load the images and
proceed with the analysis.
It provides command line options to set the output (file/screen)
and the init configuration file.

"""

from differentialPhotometryExecutor import differentialPhotometryExecutor
from dataBank import dataBank
from dataBankFileOutput import dataBankFileOutput
import sys
import getopt

def main(argv):
    data = None
    conf = None
    try:
        opts, args = getopt.getopt(argv, "hf:i:", ["file=:init="])
    except getopt.GetoptError:
        print 'differentialPhotometry.py [-f <outputfile>] [-i <initfile file>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print '(Show light curve on screen) -> differentialPhotometry.py'
            print '(Save light curve on file)   -> differentialPhotometry.py [-f <outputfile>]'
            print '(Set init config file)       -> differentialPhotometry.py [-i <initfile>]'
            sys.exit()
        elif opt in ("-i", "--init"):
            conf = arg
        elif opt in ("-f", "--file"):
            data = dataBankFileOutput(conf, arg)

    if data is None:
        data = dataBank(conf)

    differentialExecutor = differentialPhotometryExecutor(data)
    differentialExecutor.executeDifferentialPhotometry()

if __name__ == "__main__":
    main(sys.argv[1:])
else:
    main('')