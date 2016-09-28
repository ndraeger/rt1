"""
Core module for 1st order scattering simulations using arbitrary BRDF and phase functions

References
----------
Quast & Wagner (2016): doi:10.1364/AO.55.005379

"""

###todo implement unittests

import numpy as np
from surface import Isotropic



class RT1(object):
    """
    main class to perform RT simulations
    """
    def __init__(self, I0, mu_0, mu_ex, RV=None, SRF=None, nmax=10, Fn=None):
        """
        Parameters
        ----------
        I0 : float
            incidence radiation
        RV : Volume
            random volume object
        """
        self.I0 = I0
        self.mu_0 = mu_0
        self.mu_ex = mu_ex

        self.RV = RV
        assert self.RV is not None, 'ERROR: needs to provide volume information'

        self.SRF = SRF
        assert self.SRF is not None, 'ERROR: needs to provide surface information'

        self._nmax = nmax
        self.Fn = Fn

    def cos_theta(self, mu_i, mu_s, phi_i, phi_s):
        """
        A14

        Parameters
        ----------
        mu_i : float
            cosine of incidence angle
        mu_s : float
            cosine of scattering angle
        phi_i : float
            incident azimuth angle [rad]
        phi_s : float
            scattering azimuth angle [rad]
        """
        ctheta = mu_i*mu_s + np.sin(np.arccos(mu_i))*np.sin(np.arccos(mu_s))*np.cos(phi_i-phi_s)
        return ctheta

    def cos_theta_prime(self, mu_i, mu_s, phi_i, phi_s):
        """
        A15
        """
        ctheta_prime = -mu_i*mu_s + np.sin(np.arccos(mu_i))*np.sin(np.arccos(mu_s))*np.cos(phi_i-phi_s)
        return ctheta_prime


    def calc(self):
        # (16)
        Isurf = self.surface()
        Ivol = self.volume()
        Iint = self.interaction()
        return Isurf + Ivol + Iint, Isurf, Ivol, Iint

    def surface(self):
        """
        (17)
        """

        #  todo ctheta or ctheta_prime ???
        phi_i = 0.
        phi_s = 0.  # todo
        ctheta = self.cos_theta(-self.mu_0, self.mu_ex, phi_i, phi_s)

        return I0 * np.exp(-(self.tau / self.mu_0) - (self.tau/self.mu_ex)) * self.mu_0 * self.SRF.brdf(ctheta)

    def volume(self):
        """
        (18)
        """
        return (self.I0*self.omega*self.mu_0/(self.mu_0+self.mu_ex)) * (1.-np.exp(-(self.tau/self.mu_0)-(self.tau/self.mu_ex))) * self.phase(ctheta)

    def interaction(self):
        """
        (19)
        """
        Fint1 = self._calc_Fint(self.mu_0, self.mu_ex)
        Fint2 = self._calc_Fint(self.mu_ex, self.mu_0)
        return self.I0 * self.mu_0 * self.RV.omega * (np.exp(-self.RV.tau/self.mu_ex) * Fint1 + np.exp(-self.RV.tau/self.mu_0)*Fint2 )

    def _calc_Fint(self, mu1, mu2):
        """
        (37)
        """

        # todo
        # how to truncate infinite sum ????

        S = 0.
        fn = self.Fn.fn(self._nmax)

        for n in xrange(self._nmax):
            S2 = 0.
            for k in xrange(1,(n+1)+1):
                E_k1 = todo
                S2 += mu1**(-k) * (E_k1 - np.exp(-self.RV.tau/mu1)/k)

            # final sum
            # todo check once more the function
            S += fn[n] * mu1**(n+1) * (np.exp(-self.RV.tau/mu1)*np.log(mu1/(1.-mu1)) - expi(-self.RV.tau) + np.exp(-self.RV.tau/mu1)*expi(self.RV.tau/mu1-self.RV.tau) + S2)




from volume import Rayleigh
from coefficients import RayleighIsotropic

# Example1, Fig.7
I0=1.
inc = np.arange(0.,90.,5.)

V = Rayleigh(tau=0.7, omega=0.3)
SRF = Isotropic()

Itot = np.ones_like(inc)*np.nan
Isurf = np.ones_like(inc)*np.nan
Iint = np.ones_like(inc)*np.nan
Ivol = np.ones_like(inc)*np.nan
for i in xrange(len(inc)):
    mu_0 = inc[i]
    mu_ex = mu_0*1.

    R = RT1(I0, mu_0, mu_ex, RV=V, SRF=SRF)
    Itot[i], Isurf[i], Ivol[i], Iint[i] = R.calc()


