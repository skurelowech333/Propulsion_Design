# -*- coding: utf-8 -*-
"""
Created on Sun Jan 18 17:07:42 2026

@author: Sarah
"""
from math import log

class Stage:
    """ 
    All equations and infomration derived from:
        edited by Ronald W. Humble, Gary N. Henry, Wiley J. Larson. Space Propulsion Analysis and Design. New York :McGraw-Hill, 2007.
    """
    
    G0 = 9.80665  # Standard gravity [m/s^2]
    
    def __init__(self, engine, propellant_mass, dry_mass, payload_mass=0.0):
        """
        Parameters
        ----------
        engine : PropulsionSystem
            Engine instance
        propellant_mass : float
            Mass of propellant in stage [kg]
        dry_mass : float
            Structural mass of stage [kg]
        payload_mass : float, optional
            Payload above this stage [kg]
        """
        self.engine = engine
        self.m_prop = propellant_mass
        self.m_dry = dry_mass
        self.m_payload = payload_mass

    def initial_mass(self):
        """Initial mass at start of burn [kg]"""
        return self.m_prop + self.m_dry + self.m_payload

    def final_mass(self):
        """Final mass at end of burn [kg]"""
        return self.m_dry + self.m_payload

    def burn_time(self):
        """
        Compute burn time [s].

        t_burn = propellant_mass / mass_flow_rate
        """
        if self.engine.mdot is None or self.engine.mdot <= 0:
            raise ValueError("Engine mass flow rate (mdot) must be defined and positive.")
        return self.m_prop / self.engine.mdot

    def thrust_to_weight(self, g0=9.80665):
        """
        Compute stage thrust-to-weight ratio (dimensionless).

        T/W = T / (m0 * g0)
        """
        if self.engine.total_thrust() is None:
            raise ValueError("Engine total thrust must be defined.")

        m0 = self.initial_mass()
        if m0 <= 0:
            raise ValueError("Stage initial mass must be positive.")

        return self.engine.total_thrust() / (m0 * g0)
    
    def delta_v(self):
        """
        Compute Δv delivered by this stage.
        """
        if self.engine is None:
            raise ValueError("Stage has no engine.")

        isp = self.engine.specific_impulse()
        m0 = self.initial_mass()
        mf = self.final_mass()
        return self.G0 * isp * log(m0 / mf)
