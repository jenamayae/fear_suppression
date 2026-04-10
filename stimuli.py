import math
from enum import Enum
from psychopy import visual, monitors
from psychopy.visual.grating import GratingStim
from config import (
    bg_color,
    units,
    fallback_refresh_hz,
    center_flicker_hz,
    surround_flicker_hz,
    ecc,
    upper_deg,
    lower_deg,
    center_radius,
    center_sf,
    center_mask,
    center_mask_params,
    center_oris,
    center_contrast,
    center_surround_gap,
    surround_radius,
    surround_sf,
    surround_mask,
    surround_mask_params,
    surround_oris,
    surround_contrast,
    surround_hole_radius,
    surround_hole_mask,
    surround_hole_mask_params,
)

# ----------------------------
# stimulus configuration
# ----------------------------

class ModulationMode(Enum):
    phase_reversal = "phase_reversal" # 
    on_off_flicker = "on_off_flicker" # contrast gating on/off

class UpperLowerPhaseMode(Enum):
    synchronized = "synchronized"
    offset = "offset"

offset_deg_by_mode = {
    ModulationMode.phase_reversal: 90,
    ModulationMode.on_off_flicker: 180,
}

def polar_to_cartesian(radius, angle_deg):
    angle_rad = math.radians(angle_deg)
    x = radius * math.cos(angle_rad)
    y = radius * math.sin(angle_rad)
    return x, y

# convert to cartesian coordinates for PsychoPy
ux, uy = polar_to_cartesian(ecc, upper_deg)
lx, ly = polar_to_cartesian(ecc, lower_deg)

center_positions = {
    "left_upper": (-ux, uy),
    "right_upper": (ux, uy),
    "left_lower": (-lx, -ly), # negated y because lower stimuli below fixation
    "right_lower": (lx, -ly),
}

def make_window(
    size,
    fullscr,
    monitor_name,
    monitor_width_cm,
    viewing_distance_cm,
):
    mon = monitors.Monitor(monitor_name)
    mon.setSizePix(size)
    mon.setWidth(monitor_width_cm)
    mon.setDistance(viewing_distance_cm)

    return visual.Window(
        size=size,
        fullscr=fullscr,
        monitor=mon,
        units=units,
        color=bg_color,
    )

def make_stimuli(win):
    fixation = visual.TextStim(
        win=win,
        text="+",
        pos=(0, 0),
        height=0.5,
        color="white",
        autoLog=False,
    )

    centers = {}
    surrounds = {}
    surround_holes = {}

    for name, pos in center_positions.items():
        centers[name] = GratingStim(
            win=win,
            tex="sin",
            mask=center_mask,
            maskParams=center_mask_params,
            size=center_radius * 2,
            sf=center_sf,
            contrast=1.0,
            ori=0,
            phase=0.0,
            pos=pos,
            autoLog=False,
        )
        surrounds[name] = GratingStim(
            win=win,
            tex="sin",
            mask=surround_mask,
            maskParams=surround_mask_params,
            size=surround_radius * 2,
            sf=surround_sf,
            contrast=1.0,
            ori=0,
            phase=0.0,
            pos=pos,
            autoLog=False,
        )
        surround_holes[name] = GratingStim(
            win=win,
            tex=None, # pyright: ignore 
            color=bg_color,
            mask=surround_hole_mask,
            maskParams=surround_hole_mask_params,
            size=surround_hole_radius,
            pos=pos,
            sf=0,
            autoLog=False,
        )

    return {
        "fixation": fixation,
        "centers": centers,
        "surrounds": surrounds,
        "surround_holes": surround_holes,
    }

def set_trial_orientations(stims, center_ori, surround_ori):
    for center in stims["centers"].values():
        center.ori = center_ori

    if surround_ori is not None:
        for surround in stims["surrounds"].values():
            surround.ori = surround_ori

def cycle_position(frame_num, refresh_hz, flicker_hz):
    return (frame_num * flicker_hz / refresh_hz) % 1.0

def cycle_value(frame_num, refresh_hz, flicker_hz):
    return frame_num * flicker_hz / refresh_hz

def phase_reversal_output(cycle_index):
    phase = 0.0 if cycle_index % 2 == 0 else 0.5
    gain = 1.0
    return phase, gain

def on_off_output(cyc):
    phase = 0.0
    gain = 1.0 if cyc < 0.5 else 0.0
    return phase, gain

def modulation_mode_dispatcher(cyc, cycle_index, modulation_mode):
    if modulation_mode == ModulationMode.phase_reversal:
        return phase_reversal_output(cycle_index)
    if modulation_mode == ModulationMode.on_off_flicker:
        return on_off_output(cyc)
    raise ValueError(f"Unknown modulation mode: {modulation_mode}")

def upper_lower_coordinator(frame_num, refresh_hz, flicker_hz, modulation_mode, upper_lower_phase_mode):
    upper_cycle_value = cycle_value(frame_num, refresh_hz, flicker_hz)
    upper_cyc = upper_cycle_value % 1.0
    upper_cycle_index = int(upper_cycle_value)

    if upper_lower_phase_mode == UpperLowerPhaseMode.synchronized:
        lower_cycle_value = upper_cycle_value
    elif upper_lower_phase_mode == UpperLowerPhaseMode.offset:
        offset_deg = offset_deg_by_mode[modulation_mode]
        offset_cyc = (offset_deg % 360.0) / 360.0
        lower_cycle_value = upper_cycle_value + offset_cyc
    else:
        raise ValueError(f"Unknown upper/lower phase mode: {upper_lower_phase_mode}")

    lower_cyc = lower_cycle_value % 1.0
    lower_cycle_index = int(lower_cycle_value)

    upper_phase, upper_gain = modulation_mode_dispatcher(
        upper_cyc,
        upper_cycle_index,
        modulation_mode,
    )
    lower_phase, lower_gain = modulation_mode_dispatcher(
        lower_cyc,
        lower_cycle_index,
        modulation_mode,
    )

    return upper_phase, lower_phase, upper_gain, lower_gain

def draw_flicker_frame(
    stims,
    frame_num,
    refresh_hz,
    center_ori,
    surround_ori,
    modulation_mode,
    upper_lower_phase_mode,
    center_contrast=center_contrast,
    surround_contrast=surround_contrast,
    center_flicker_hz=center_flicker_hz,
    surround_flicker_hz=surround_flicker_hz,
):
    set_trial_orientations(stims, center_ori, surround_ori)

    center_upper_phase, center_lower_phase, center_upper_gain, center_lower_gain = upper_lower_coordinator(
        frame_num=frame_num,
        refresh_hz=refresh_hz,
        flicker_hz=center_flicker_hz,
        modulation_mode=modulation_mode,
        upper_lower_phase_mode=upper_lower_phase_mode,
    )
    surround_upper_phase, surround_lower_phase, surround_upper_gain, surround_lower_gain = upper_lower_coordinator(
        frame_num=frame_num,
        refresh_hz=refresh_hz,
        flicker_hz=surround_flicker_hz,
        modulation_mode=modulation_mode,
        upper_lower_phase_mode=upper_lower_phase_mode,
    )

    stims["centers"]["left_upper"].phase = center_upper_phase
    stims["centers"]["right_upper"].phase = center_upper_phase
    stims["centers"]["left_lower"].phase = center_lower_phase
    stims["centers"]["right_lower"].phase = center_lower_phase

    stims["surrounds"]["left_upper"].phase = surround_upper_phase
    stims["surrounds"]["right_upper"].phase = surround_upper_phase
    stims["surrounds"]["left_lower"].phase = surround_lower_phase
    stims["surrounds"]["right_lower"].phase = surround_lower_phase

    stims["centers"]["left_upper"].contrast = center_contrast * center_upper_gain
    stims["centers"]["left_lower"].contrast = center_contrast * center_lower_gain
    stims["centers"]["right_upper"].contrast = center_contrast * center_upper_gain
    stims["centers"]["right_lower"].contrast = center_contrast * center_lower_gain

    stims["surrounds"]["left_upper"].contrast = surround_contrast * surround_upper_gain
    stims["surrounds"]["left_lower"].contrast = surround_contrast * surround_lower_gain
    stims["surrounds"]["right_upper"].contrast = surround_contrast * surround_upper_gain
    stims["surrounds"]["right_lower"].contrast = surround_contrast * surround_lower_gain

    if surround_ori is not None:
        for name in stims["surrounds"]:
            stims["surrounds"][name].draw()
            if "surround_holes" in stims:
                stims["surround_holes"][name].draw()

    for center in stims["centers"].values():
        center.draw()

    stims["fixation"].draw()
