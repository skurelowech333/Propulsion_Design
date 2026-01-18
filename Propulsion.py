# -*- coding: utf-8 -*-
"""
Propulsion Design Toolbox (Guarded State-Based System)

@author: Sarah
"""

class Propulsion:
    """ 
    All equations and infomration derived from:
        edited by Ronald W. Humble, Gary N. Henry, Wiley J. Larson. Space Propulsion Analysis and Design. New York :McGraw-Hill, 2007.
    """

    G0 = 9.80665  # Standard gravity [m/s^2]

    def __init__(self,
                 mass_flow_rate=None,
                 exit_velocity=None,
                 efficiency=1.0,
                 exit_pressure=None,
                 ambient_pressure=0.0,
                 exit_area=None):

        self.mdot = mass_flow_rate
        self.ve = exit_velocity
        self.eta = efficiency
        self.p_e = exit_pressure
        self.p_a = ambient_pressure
        self.A_e = exit_area
        
    def _require(self, **kwargs):
        """
        Ensure required quantities are defined (not None).
        """
        missing = [name for name, value in kwargs.items() if value is None]
        if missing:
            raise ValueError(f"Missing required parameter(s): {', '.join(missing)}")

    def momentum_thrust(self):
        """
        Momentum thrust component: ṁ v_e
        """
        self._require(mdot=self.mdot, ve=self.ve)
        return self.mdot * self.ve

    def pressure_thrust(self):
        """
        Pressure thrust component: (p_e − p_a) A_e

        Returns zero if pressure terms are undefined.
        """
        if self.p_e is None or self.A_e is None:
            return 0.0
        return (self.p_e - self.p_a) * self.A_e

    def total_thrust(self):
        """
        Total thrust:

        T = η [ ṁ v_e + (p_e − p_a) A_e ]
        """
        self._require(mdot=self.mdot, ve=self.ve)
        return self.eta * (self.momentum_thrust() + self.pressure_thrust())

    def specific_impulse(self):
        """
        Specific impulse:

        Isp = T / (ṁ g₀)
        """
        self._require(mdot=self.mdot)
        T = self.total_thrust()
        return T / (self.mdot * self.G0)

    def effective_exhaust_velocity(self):
        """
        Effective exhaust velocity:

        c_eff = T / ṁ
        """
        self._require(mdot=self.mdot)
        return self.total_thrust() / self.mdot
