# -*- coding: utf-8 -*-
"""
Mission Requirements Model

@author: Sarah
"""

import math

class Mission:
    """
    Represents mission-level requirements for propulsion design.

    This class does NOT know about engines or hardware.
    It only encodes what the mission requires.
    
    All equations and infomration derived from:
        edited by Ronald W. Humble, Gary N. Henry, Wiley J. Larson. Space Propulsion Analysis and Design. New York :McGraw-Hill, 2007.
    """

    G0 = 9.80665  # Standard gravity [m/s^2]

    def __init__(self,
                 delta_v_required,
                 min_thrust_to_weight=0.0,
                 max_burn_time=None,
                 gravity_loss=0.0,
                 margin=0.0):
        """
        Parameters
        ----------
        delta_v_required : float
            Required ideal mission Δv [m/s]
        min_thrust_to_weight : float, optional
            Minimum thrust-to-weight ratio
        max_burn_time : float or None, optional
            Maximum allowable burn time [s]
        gravity_loss : float, optional
            Estimated gravity losses [m/s]
        margin : float, optional
            Δv margin (fraction, e.g. 0.1 = 10%)
        """
        self.delta_v_required = delta_v_required
        self.min_tw = min_thrust_to_weight
        self.max_burn_time = max_burn_time
        self.gravity_loss = gravity_loss
        self.margin = margin

    def total_delta_v_required(self):
        """
        Total required Δv including losses and margin.
        """
        dv = self.delta_v_required + self.gravity_loss
        return dv * (1.0 + self.margin)

    def achieved_delta_v(self, isp, m0, mf):
        """
        Compute achievable Δv using Tsiolkovsky equation.

        Δv = g₀ Isp ln(m₀ / m_f)
        """
        if m0 <= mf:
            raise ValueError("Initial mass must exceed final mass.")

        return self.G0 * isp * math.log(m0 / mf)

    def delta_v_satisfied(self, isp, m0, mf):
        """
        Check if mission Δv requirement is met.
        """
        dv_achieved = self.achieved_delta_v(isp, m0, mf)
        return dv_achieved >= self.total_delta_v_required()

    def thrust_to_weight_satisfied(self, thrust, mass):
        """
        Check thrust-to-weight constraint.
        """
        if self.min_tw <= 0.0:
            return True

        weight = mass * self.G0
        return thrust / weight >= self.min_tw

    def burn_time_satisfied(self, burn_time):
        """
        Check burn time constraint.
        """
        if self.max_burn_time is None:
            return True
        return burn_time <= self.max_burn_time
    
    def propellant_for_delta_v(self, isp, dry_mass, payload_mass, delta_v=None):
        """
        Compute required propellant mass to achieve a specified Δv.

        Parameters
        ----------
        isp : float
            Engine specific impulse [s]
        dry_mass : float
            Stage dry mass [kg]
        payload_mass : float
            Payload mass [kg]
        delta_v : float, optional
            Desired Δv [m/s]. If None, uses mission total Δv required.

        Returns
        -------
        float
            Required propellant mass [kg]
        """
        dv = delta_v if delta_v is not None else self.total_delta_v_required()
        
        if isp <= 0:
            raise ValueError("Isp must be positive.")

        m0_without_prop = dry_mass + payload_mass
        # Solve Tsiolkovsky equation for propellant mass
        # m0 = mf + m_prop = m0_without_prop + m_prop
        m_prop = m0_without_prop * (math.exp(dv / (self.G0 * isp)) - 1)
        return m_prop
