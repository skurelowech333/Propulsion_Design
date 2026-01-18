# -*- coding: utf-8 -*-
"""
Created on Sun Jan 18 18:02:58 2026

@author: Sarah
"""

class LaunchVehicle:
    """
    Represents a multi-stage launch vehicle.
    Stages should be ordered from bottom (first stage) to top (last stage).
    """

    def __init__(self, stages):
        """
        Parameters
        ----------
        stages : list of Stage
            Ordered bottom → top
        """
        self.stages = stages

    # ----------------------------
    # Mass stacking logic
    # ----------------------------
    def stack_masses(self):
        """
        Assign payload mass of each stage to include all upper stages.
        """
        upper_mass = 0.0
        for stage in reversed(self.stages):
            stage.m_payload = stage.m_payload + upper_mass
            upper_mass = stage.initial_mass()

    # ----------------------------
    # Performance
    # ----------------------------
    def total_delta_v(self):
        """
        Total Δv capability of the vehicle.
        """
        return sum(stage.delta_v() for stage in self.stages)

    def stage_delta_vs(self):
        """
        Δv contribution of each stage.
        """
        return [stage.delta_v() for stage in self.stages]

    def total_initial_mass(self):
        """
        Lift-off mass of the vehicle.
        """
        return self.stages[0].initial_mass()

