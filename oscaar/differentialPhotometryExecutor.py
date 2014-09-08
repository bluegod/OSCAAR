"""
OSCAAR/Code/differentialPhotometryExecutor.py

Load in the images and analysis parameters set in the Code/init.par
file, loop through each star within each image, for all images, and
measure the stellar centroid positions and fluxes. Save these data
to the oscaar.dataBank() object, and save that out to a binary
"pickle".


Core developer: Brett Morris
"""

from matplotlib import pyplot as plt

import oscaar
import astrometry
import photometry
import dataBank
import systematics
import pyfits
import IO


class differentialPhotometryExecutor:
    def __init__(self, dataBank):
        self.data = dataBank

    def executeDifferentialPhotometry(self):
        global allStars, outputPath, N_exposures, meanDarkFrame, masterFlat, plottingThings, statusBarFig, statusBarAx, expNumber, image, star, est_x, est_y, x, y, radius, trackFlag, fluxes, errors, photFlags, photFlag, meanComparisonStars, meanComparisonStarErrors, lightCurves, lightCurveErrors
        # Turn on interactive plots
        plt.ion()
        # Store initialized dictionary
        allStars = self.data.getDict()
        outputPath = self.data.outputPath
        N_exposures = len(self.data.getPaths())
        # Prepare systematic corrections: dark frame, flat field
        meanDarkFrame = self.data.getMeanDarkFrame()
        masterFlat = self.data.masterFlat
        # Tell oscaar what figure settings to use
        plottingThings, statusBarFig, statusBarAx = \
            IO.plottingSettings(self.data.trackPlots, self.data.photPlots)
        # Main loop: iterate through each exposures
        for expNumber in xrange(N_exposures):
            if statusBarAx is not None and expNumber % 15 == 0:
                # Prepare some plotting settings here
                plt.cla()
                statusBarAx.set_title('oscaar2.0 is running...')
                statusBarAx.set_xlim([0, 100])
                statusBarAx.set_xlabel('Percent Complete (%)')
                statusBarAx.get_yaxis().set_ticks([])
                statusBarAx.barh([0], [100.0 * expNumber / len(self.data.getPaths())],
                                 [1], color='k')

            # Open image from FITS file
            image = (pyfits.getdata(self.data.getPaths()[expNumber]) - meanDarkFrame) \
                    / masterFlat
            # Store the exposure time from the FITS header
            self.data.storeTime(expNumber)

            # Iterate through each star in each exposure
            for star in allStars:
                est_x, est_y = self.data.centroidInitialGuess(expNumber, star)
                # Find the stellar centroid
                x, y, radius, trackFlag = astrometry.trackSmooth(image, est_x, est_y,
                                                                 self.data.smoothConst,
                                                                 plottingThings,
                                                                 zoom=self.data.trackingZoom,
                                                                 plots=self.data.trackPlots)
                # Store the centroid positions
                self.data.storeCentroid(star, expNumber, x, y)
                # Measure the flux and uncertainty, centered on the previously found
                # stellar centroid
                fluxes, errors, photFlags = photometry.multirad(image, x, y,
                                                                self.data.apertureRadii,
                                                                plottingThings,
                                                                ccdGain=self.data.ccdGain,
                                                                plots=self.data.photPlots)
                photFlag = any(photFlags)
                # Store the flux and uncertainty in the data object
                self.data.storeFluxes(star, expNumber, fluxes, errors)

                if trackFlag or photFlag and not self.data.getFlag():
                    # Store error flags
                    self.data.setFlag(star, False)
                if self.data.trackPlots or self.data.photPlots:
                    # More plotting settings
                    plt.draw()

            if statusBarAx is not None and expNumber % 15 == 0:
                # More plotting settings
                plt.draw()
        plt.close()
        # Compute the scaled fluxes of each comparison star
        self.data.scaleFluxes_multirad()
        # Calculate a composite comparison star by combining all comparisons
        meanComparisonStars, meanComparisonStarErrors = \
            self.data.calcMeanComparison_multirad(ccdGain=self.data.ccdGain)
        # Calculate the light curve
        lightCurves, lightCurveErrors = self.data.computeLightCurve_multirad(meanComparisonStars,
                                                                             meanComparisonStarErrors)
        # Save the dataBank object for later use
        IO.save(self.data, outputPath)

        # Plot the resulting light curve
        self.data.plotLightCurve_multirad()