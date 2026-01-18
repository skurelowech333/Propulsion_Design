# -*- coding: utf-8 -*-
"""
Created on Sun Jan 18 17:09:53 2026

@author: Sarah
"""
from Propulsion import Propulsion
from Stage import Stage
from Mission import Mission
import matplotlib.pyplot as plt

import numpy as np

""" 
Driver function for propulsion design analysis
"""

def vectorized_sweep(engine_template, stage_template, mission,
                     ve_range, mdot_range):
    """
    Vectorized sweep of exhaust velocity and mass flow rate.

    Parameters
    ----------
    engine_template : Propulsion
        Template engine
    stage_template : Stage
        Stage with mass properties
    mission : Mission
        Mission requirements
    ve_range : 1D array-like
        Exhaust velocity values [m/s]
    mdot_range : 1D array-like
        Mass flow rate values [kg/s]

    Returns
    -------
    dict
        {
            "ve": 2D array,
            "mdot": 2D array,
            "dv": 2D array,
            "tw": 2D array,
            "burn_time": 2D array,
            "feasible": 2D boolean array
        }
    """
    ve_grid, mdot_grid = np.meshgrid(ve_range, mdot_range, indexing='ij')

    dv_grid = np.zeros_like(ve_grid, dtype=float)
    tw_grid = np.zeros_like(ve_grid, dtype=float)
    burn_grid = np.zeros_like(ve_grid, dtype=float)
    feasible_grid = np.zeros_like(ve_grid, dtype=bool)

    m0 = stage_template.initial_mass()
    mf = stage_template.final_mass()

    for i in range(ve_grid.shape[0]):
        for j in range(ve_grid.shape[1]):
            ve = ve_grid[i, j]
            mdot = mdot_grid[i, j]

            # Create engine instance
            engine = Propulsion(
                mass_flow_rate=mdot,
                exit_velocity=ve,
                efficiency=engine_template.eta,
                exit_pressure=engine_template.p_e,
                ambient_pressure=engine_template.p_a,
                exit_area=engine_template.A_e
            )

            # Compute performance metrics
            try:
                thrust = engine.total_thrust()
                isp = engine.specific_impulse()
                burn_time = stage_template.m_prop / mdot
                dv = mission.achieved_delta_v(isp, m0, mf)
                tw = thrust / (m0 * 9.80665)
            except ValueError:
                dv = np.nan
                tw = np.nan
                burn_time = np.nan

            # Save metrics
            dv_grid[i, j] = dv
            tw_grid[i, j] = tw
            burn_grid[i, j] = burn_time

            # Check feasibility
            feasible = True
            if np.isnan(dv) or dv < mission.total_delta_v_required():
                feasible = False
            if np.isnan(tw) or tw < mission.min_tw:
                feasible = False
            if mission.max_burn_time is not None and (np.isnan(burn_time) or burn_time > mission.max_burn_time):
                feasible = False

            feasible_grid[i, j] = feasible

    return {
        "ve": ve_grid,
        "mdot": mdot_grid,
        "dv": dv_grid,
        "tw": tw_grid,
        "burn_time": burn_grid,
        "feasible": feasible_grid
    }


def evaluate_stage_mission(engine, stage, mission):
    """
    Evaluate a stage and engine against mission requirements.

    Parameters
    ----------
    engine : PropulsionSystem
        The engine instance
    stage : Stage
        The stage instance (propellant + dry + payload)
    mission : Mission
        Mission requirements (delta_v, T/W, burn time)

    Returns
    -------
    dict
        Dictionary containing metrics and feasibility checks
    """
    # Masses
    m0 = stage.initial_mass()
    mf = stage.final_mass()

    # Burn time
    try:
        burn_time = stage.burn_time()
    except ValueError as e:
        burn_time = None

    # Engine performance
    try:
        thrust = engine.total_thrust()
        isp = engine.specific_impulse()
    except ValueError as e:
        thrust = None
        isp = None

    # Δv achieved
    try:
        dv_achieved = mission.achieved_delta_v(isp, m0, mf) if isp is not None else None
    except ValueError as e:
        dv_achieved = None

    # Constraint checks
    dv_ok = mission.delta_v_satisfied(isp, m0, mf) if dv_achieved is not None else False
    tw_ok = mission.thrust_to_weight_satisfied(thrust, m0) if thrust is not None else False
    bt_ok = mission.burn_time_satisfied(burn_time) if burn_time is not None else False
    mission_ok = dv_ok and tw_ok and bt_ok

    # Package results
    results = {
        "initial_mass": m0,
        "final_mass": mf,
        "burn_time": burn_time,
        "thrust": thrust,
        "Isp": isp,
        "achieved_delta_v": dv_achieved,
        "delta_v_ok": dv_ok,
        "thrust_to_weight_ok": tw_ok,
        "burn_time_ok": bt_ok,
        "mission_satisfied": mission_ok
    }

    return results

# Engine template
engine_template = Propulsion(
    efficiency=0.95,
    exit_pressure=101325,
    ambient_pressure=0.0,
    exit_area=0.2
)

# Stage template
stage_template = Stage(
    engine=engine_template,
    propellant_mass=2000,
    dry_mass=800,
    payload_mass=500
)

# Mission
mission = Mission(
    delta_v_required=4500,
    min_thrust_to_weight=1.2,
    max_burn_time=400,
    gravity_loss=300,
    margin=0.1
)

# Sweep ranges (choose higher mdot and ve to satisfy T/W)
ve_range = np.linspace(3200, 3800, 7)   # m/s
mdot_range = np.linspace(8, 15, 8)      # kg/s

# Run sweep
results = vectorized_sweep(engine_template, stage_template, mission, ve_range, mdot_range)

# Plot feasible designs
plt.figure(figsize=(8,6))
plt.contourf(results["ve"], results["mdot"], results["feasible"], levels=[0,0.5,1],
             colors=["lightcoral","lightgreen"])
plt.xlabel("Exhaust Velocity [m/s]")
plt.ylabel("Mass Flow Rate [kg/s]")
plt.title("Feasible Engine Designs (green = feasible)")
plt.colorbar(label="Feasible")
plt.show()
