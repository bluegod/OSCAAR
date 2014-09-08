'''oscaar v2.0
    Module for differential photometry
    Extends dataBank functionality to output the graph to the filesystem.
    '''
from matplotlib import pyplot as plt
from dataBank import dataBank

class dataBankFileOutput(dataBank):

    def __init__(self, initParFilePath=None, imageFilePath=None):
        self.imageFilePath = imageFilePath
        dataBank.__init__(self, initParFilePath)

    def plotLightCurve_multirad_output(self):
        print "Saving plot... %s" % self.imageFilePath
        plt.savefig(self.imageFilePath)
