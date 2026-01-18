# -*- coding: utf-8 -*-
"""
Created on Sun Jan 18 17:09:53 2026

@author: Sarah
"""
from Propulsion import Propulsion
from Stage import Stage
from Mission import Mission
from LaunchVehicle import LaunchVehicle

import itertools
import numpy as np

def clone_vehicle(vehicle):
    """Deep copy a LaunchVehicle and its stages/engines."""
    new_stages = []
    for s in vehicle.stages:
        new_engine = Propulsion(
            mass_flow_rate=s.engine.mdot,
            exit_velocity=s.engine.ve,
            efficiency=s.engine.eta,
            exit_pressure=s.engine.p_e,
            ambient_pressure=s.engine.p_a,
            exit_area=s.engine.A_e
        )
        new_stage = Stage(
            engine=new_engine,
            propellant_mass=s.m_prop,
            dry_mass=s.m_dry,
            payload_mass=s.m_payload
        )
        new_stages.append(new_stage)
    return LaunchVehicle(new_stages)

def evaluate_mission(vehicle, mission):
    """
    Evaluate an N-stage vehicle against a mission.
    Returns per-stage metrics, total Δv, and overall feasibility.
    """
    vehicle.stack_stages()  # ensure correct payload stacking

    dv_total = 0.0
    stage_results = []

    for idx, stage in enumerate(vehicle.stages):
        engine = stage.engine
        m0 = stage.initial_mass()
        mf = stage.final_mass()
        isp = engine.specific_impulse()
        thrust = engine.total_thrust()
        burn_time = stage.burn_time()
        dv = mission.achieved_delta_v(isp, m0, mf)
        dv_total += dv

        # Only Stage 1 T/W enforced
        tw_ok = mission.thrust_to_weight_satisfied(thrust, m0) if idx == 0 else True
        bt_ok = mission.burn_time_satisfied(burn_time)

        stage_results.append({
            "stage": idx + 1,
            "dv": dv,
            "thrust": thrust,
            "Isp": isp,
            "burn_time": burn_time,
            "tw_ok": tw_ok,
            "burn_time_ok": bt_ok
        })

    dv_ok = dv_total >= mission.total_delta_v_required()
    stage1_ok = stage_results[0]["tw_ok"] and stage_results[0]["burn_time_ok"]
    upper_stages_ok = all(s["burn_time_ok"] for s in stage_results[1:])
    mission_ok = dv_ok and stage1_ok and upper_stages_ok

    # Debug prints
    print(f"Total Δv achieved: {dv_total:.1f} m/s (required: {mission.total_delta_v_required():.1f} m/s)")
    for s in stage_results:
        tw = s["thrust"]/(s["dv"]/mission.G0 if s["dv"]>0 else 1)
        print(f"Stage {s['stage']}: dv={s['dv']:.1f}, T/W OK={s['tw_ok']}, burn OK={s['burn_time_ok']}")

    return {
        "stages": stage_results,
        "dv_total": dv_total,
        "mission_satisfied": mission_ok
    }

def n_stage_engine_sweep(vehicle_template, mission, stage_sweeps):
    """
    Sweep engine parameters for all stages.
    Returns list of feasible designs.
    """
    assert len(stage_sweeps) == len(vehicle_template.stages)

    # Build Cartesian product of engine parameter choices
    sweep_grids = [list(itertools.product(s["ve"], s["mdot"])) for s in stage_sweeps]

    feasible_designs = []

    for engine_choices in itertools.product(*sweep_grids):
        vehicle = clone_vehicle(vehicle_template)

        for i, (ve, mdot) in enumerate(engine_choices):
            vehicle.stages[i].engine.ve = ve
            vehicle.stages[i].engine.mdot = mdot

        results = evaluate_mission(vehicle, mission)

        if results["mission_satisfied"]:
            feasible_designs.append({
                "engine_choices": engine_choices,
                "results": results
            })

    return feasible_designs

# ----------------------------
# Build vehicle
# ----------------------------
engine1 = Propulsion(mass_flow_rate=35, exit_velocity=4000, efficiency=0.95)
engine2 = Propulsion(mass_flow_rate=8,  exit_velocity=3600, efficiency=0.96)
engine3 = Propulsion(mass_flow_rate=3,  exit_velocity=3800, efficiency=0.97)

stage1 = Stage(engine1, propellant_mass=6000, dry_mass=900, payload_mass=0.0)
stage2 = Stage(engine2, propellant_mass=2500, dry_mass=350, payload_mass=0.0)
stage3 = Stage(engine3, propellant_mass=1000, dry_mass=150, payload_mass=500)

vehicle_template = LaunchVehicle([stage1, stage2, stage3])

# ----------------------------
# Define mission
# ----------------------------
mission = Mission(
    delta_v_required=6000,  # achievable with stacked propellant
    min_thrust_to_weight=0.8,
    max_burn_time=450,
    gravity_loss=0,  # for testing
    margin=0.05
)

# ----------------------------
# Sweep ranges for engines
# ----------------------------
stage_sweeps = [
    {"ve": np.linspace(3800, 4200, 3), "mdot": np.linspace(28, 35, 3)},
    {"ve": np.linspace(3700, 4000, 3), "mdot": np.linspace(8, 10, 3)},
    {"ve": np.linspace(3800, 4200, 3), "mdot": np.linspace(3, 4, 2)}
]

# ----------------------------
# Run sweep
# ----------------------------
feasible_designs = n_stage_engine_sweep(vehicle_template, mission, stage_sweeps)

print(f"\nFound {len(feasible_designs)} feasible designs\n")

for d in feasible_designs:
    print("Engine choices (ve, mdot):", d["engine_choices"])
    print("Total Δv:", d["results"]["dv_total"])
    print("---")
