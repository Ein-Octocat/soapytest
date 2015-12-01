import numpy

from soapy import atmosphere

from aotools.circle import zernike

import matplotlib.pylab as plt
from astropy.io import fits

import os
FILEPATH = os.path.dirname(os.path.abspath(__file__))

def getZernCoeffs(nZerns, nScrns, scrnSize, subScrnSize, r0):

    Zs = zernike.zernikeArray(nZerns+1, subScrnSize)[1:]

    Zs.shape = nZerns, subScrnSize*subScrnSize

    subsPerScrn = scrnSize/subScrnSize
    zCoeffs = numpy.zeros((nZerns, nScrns*(subsPerScrn**2)))

    i = 0
    for n in range(nScrns):
        # Make one big screen
        scrn = atmosphere.ft_phase_screen(
                r0, scrnSize, 1./subScrnSize, 100., 0.01)

        # Pick out as many sub-scrns as possible to actually test
        for x in range(subsPerScrn):
            for y in range(subsPerScrn):
                subScrn = scrn[
                        x*subScrnSize: (x+1)*subScrnSize,
                        y*subScrnSize: (y+1)*subScrnSize]
                subScrn = subScrn.reshape(subScrnSize*subScrnSize)

                # Turn into radians. r0 defined at 500nm, scrns in nm
                subScrn /= (500/(2*numpy.pi))

                # Dot with zernikes to get powerspec
                zCoeffs[:, i] = (Zs*subScrn).sum(1)
                i+=1

    return zCoeffs


def loadNoll(nZerns):
    """
    Loads the noll reference values for Zernike variance in Kolmogorov turbulence.
    """
    nollPath = os.path.join(FILEPATH, "../resources/noll.fits")
    noll = fits.getdata(nollPath)

    return noll.diagonal()[:nZerns]


def testZernSpec(nZerns, nScrns, scrnSize, subScrnSize, r0):

    noll = loadNoll(nZerns)
    zCoeffs = getZernCoeffs(nZerns, nScrns, scrnSize, subScrnSize, r0)
    zVar = zCoeffs.var(1)

    return zVar, noll

def plotZernSpec(zVar, noll):

    plt.figure()
    plt.semilogy(zVar, label="Phase Screens")
    plt.semilogy(noll, label="Noll reference")

    plt.xlabel("Zernike mode index")
    plt.ylabel("Power ($rad^2$)")

    plt.show()

if __name__=="__main__":

    # Number of scrns to average over
    nScrns = 10000
    r0 = 1. # R0 value to use in test
    nZerns = 50
    subScrnSize = 256
    scrnSize = 512


    zVar, noll = testZernSpec(nZerns, nScrns, scrnSize, subScrnSize, r0)
    plotZernSpec(zVar, noll)