import os
import numpy

from soapy import lineofsight, confParse, atmosphere


SOAPYTEST_DIR = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "../../")
SOAPY_CONF = os.path.join(SOAPYTEST_DIR, "conf/lineofsight/phasevariance.yaml")

# Paramters to be used in automated tests
R0_RANGE = numpy.array([0.05, 0.1, 0.15, 0.2, 0.5])

class TestPhaseVariance(object):

    def __init__(self, configfile=None):
        if configfile is None:
            configfile = SOAPY_CONF
        self.configfile = configfile                

        self.loadConfig()

        self.initLOS()

    def loadConfig(self):
        self.config = confParse.loadSoapyConfig(self.configfile)

    def initAtmos(self):
        self.atmos = atmosphere.atmos(self.config)

    def initLOS(self):
        self.los = lineofsight.LineOfSight(self.config.scis[0], self.config)


    def testPhaseVariance(self, r0):

        self.config.atmos.r0 = r0
        self.initAtmos()

        phase_variance = numpy.zeros((self.config.sim.nIters))
        for i in range(self.config.sim.nIters):
            scrns = self.atmos.moveScrns()

            phase = self.los.frame(scrns)

            # Convert phase from rad @ sci wvl to rad @ 500nm
            phase *= self.config.scis[0].wavelength/500e-9


            phase_variance[i] = phase.var()

        return phase_variance.mean(), phase_variance.var()

    def testR0Range(self, r0_range):
        """
        Finds the phase variance through the lineof sight for a given range of r0 values
        
        Parameters:
            r0_range(ndarray): A 1-d array of r0 values (in metres) to TestPhaseVariance

        Return:
            ndarray: 2-d array of variances, and variance of phase variances over nIters
        """
        phase_variance = numpy.zeros((2, len(r0_range)))
        for i, r0 in enumerate(r0_range):
            print("\nTest R0: {}".format(r0))
            phase_variance[:, i] = self.testPhaseVariance(r0)
        
        return phase_variance


if __name__ == "__main__":
    test = TestPhaseVariance()
    phase_variance = test.testR0Range(R0_RANGE)
