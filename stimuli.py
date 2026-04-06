import math
from enum import Enum
from psychopy import visual, monitors
from psychopy.visual.grating import GratingStim



from main import (
    monitor_name,
    monitor_pixels,
    default_refresh_hz,
    monitor_width_cm,
    viewing_distance_cm,
    fullscreen
    )

# ----------------------------
# stimulus configuration
# ----------------------------

bg_color = (0, 0, 0)
units = "deg"

# stim flicker frequency
center_flicker_hz = 3
surround_flicker_hz = 3.75

class ModulationMode(Enum):
    binary_counterphase = "binary_counterphase" # phase reversal 
    on_off_flicker = "on_off_flicker" # contrast gating on/off

modulation_mode = ModulationMode.on_off_flicker # default setting

offset_deg_by_mode = {
    ModulationMode.binary_counterphase: 90,
    ModulationMode.on_off_flicker: 180,
}

# stim location in polar coordinates (r, theta)
ecc = 5.0
upper_deg = 20.0
lower_deg = 45.0

# convert to cartesian coordinates for PsychoPy
ux, uy = polar_to_cartesian(ecc, upper_deg)
lx, ly = polar_to_cartesian(ecc, lower_deg)

def polar_to_cartesian(radius, angle_deg):
    angle_rad = math.radians(angle_deg)
    x = radius * math.cos(angle_rad)
    y = radius * math.sin(angle_rad)
    return x, y

center_positions = {
    "left_upper": (-ux, uy),
    "right_upper": (ux, uy),
    "left_lower": (-lx, -ly), # negated y because lower stimuli below fixation
    "right_lower": (lx, -ly),
}

# center stimuli
center_radius = 0.75
center_sf = 1.0
center_mask, center_mask_params = "raisedCos", {"fringeWidth": 0.1}
center_oris = [45, 55, 75, 315]

# center contrasts by hemifield
left_center_contrast = 0.5
right_center_contrast = 0.5

# surround stimuli
center_surround_gap = 0.5
surround_radius = center_radius + center_surround_gap + 1.5
surround_sf = 1.0
surround_mask = "raisedCos"
surround_mask_params = {"fringeWidth": 0.1}
surround_oris = [None, 45, 315]

# surround contrasts by hemifield
left_surround_contrast = 1.0
right_surround_contrast = 1.0

# surround inner radius mask
surround_hole_radius = (center_radius + center_surround_gap) * 2
surround_hole_mask = "raisedCos"
surround_hole_mask_params = {"fringeWidth": 0.15}


def make_window(
    size=monitor_pixels,
    fullscr=fullscreen,
    monitor_name=monitor_name,
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
            tex=None,
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


def flicker_state(frame_num, refresh_hz, flicker_hz, modulation_mode):
    # for one frame, decide what the upper, lower stimuli should do; 
    # depending on cyc, where we are within the repeating pattern;
    # and offset_deg_by_mode (90 for binary, 180 for on/off)

    cyc = (frame_num * (flicker_hz / 2.0) / refresh_hz) % 1.0 
    
    offset_deg = offset_deg_by_mode[modulation_mode]
    offset_cyc = (offset_deg % 360.0) / 360
    lower_cyc = (cyc + offset_cyc) % 1

    if modulation_mode == ModulationMode.binary_counterphase:
        upper_phase = 0.0 if cyc < 0.5 else 0.5
        lower_phase = 0.0 if lower_cyc < 0.5 else 0.5
        upper_gain, lower_gain = 1.0, 1.0
 
    elif modulation_mode == ModulationMode.on_off_flicker:
        upper_phase, lower_phase = 0.0, 0.0
        upper_gain = 1.0 if cyc < 0.5 else 0.0
        lower_gain = 1.0 if lower_cyc < 0.5 else 0.0
    else:
        raise ValueError(f"Unknown modulation mode: {modulation_mode}")

    return upper_phase, lower_phase, upper_gain, lower_gain



def draw_flicker_frame(
    stims,
    frame_num,
    refresh_hz,
    center_ori,
    surround_ori,
    left_center_contrast=left_center_contrast,
    right_center_contrast=right_center_contrast,
    left_surround_contrast=left_surround_contrast,
    right_surround_contrast=right_surround_contrast,
    center_flicker_hz=center_flicker_hz,
    surround_flicker_hz=surround_flicker_hz,
    modulation_mode=modulation_mode,
):
    set_trial_orientations(stims, center_ori, surround_ori)

    center_upper_phase, center_lower_phase, center_upper_gain, center_lower_gain = flicker_state(
        frame_num=frame_num,
        refresh_hz=refresh_hz,
        flicker_hz=center_flicker_hz,
        modulation_mode=modulation_mode,
    )
    surround_upper_phase, surround_lower_phase, surround_upper_gain, surround_lower_gain = flicker_state(
        frame_num=frame_num,
        refresh_hz=refresh_hz,
        flicker_hz=surround_flicker_hz,
        modulation_mode=modulation_mode,
    )

    stims["centers"]["left_upper"].phase = center_upper_phase
    stims["centers"]["right_upper"].phase = center_upper_phase
    stims["centers"]["left_lower"].phase = center_lower_phase
    stims["centers"]["right_lower"].phase = center_lower_phase

    stims["surrounds"]["left_upper"].phase = surround_upper_phase
    stims["surrounds"]["right_upper"].phase = surround_upper_phase
    stims["surrounds"]["left_lower"].phase = surround_lower_phase
    stims["surrounds"]["right_lower"].phase = surround_lower_phase

    stims["centers"]["left_upper"].contrast = left_center_contrast * center_upper_gain
    stims["centers"]["left_lower"].contrast = left_center_contrast * center_lower_gain
    stims["centers"]["right_upper"].contrast = right_center_contrast * center_upper_gain
    stims["centers"]["right_lower"].contrast = right_center_contrast * center_lower_gain

    stims["surrounds"]["left_upper"].contrast = left_surround_contrast * surround_upper_gain
    stims["surrounds"]["left_lower"].contrast = left_surround_contrast * surround_lower_gain
    stims["surrounds"]["right_upper"].contrast = right_surround_contrast * surround_upper_gain
    stims["surrounds"]["right_lower"].contrast = right_surround_contrast * surround_lower_gain

    if surround_ori is not None:
        for name in stims["surrounds"]:
            stims["surrounds"][name].draw()
            if "surround_holes" in stims:
                stims["surround_holes"][name].draw()

    for center in stims["centers"].values():
        center.draw()

    stims["fixation"].draw()


def draw_trial_frame(
    stims,
    t,
    center_ori,
    surround_ori,
    left_center_contrast=left_center_contrast,
    right_center_contrast=right_center_contrast,
    left_surround_contrast=left_surround_contrast,
    right_surround_contrast=right_surround_contrast,
    refresh_hz=default_refresh_hz,
):
    frame_num = round(t * refresh_hz)

    draw_flicker_frame(
        stims=stims,
        frame_num=frame_num,
        refresh_hz=refresh_hz,
        center_ori=center_ori,
        surround_ori=surround_ori,
        left_center_contrast=left_center_contrast,
        right_center_contrast=right_center_contrast,
        left_surround_contrast=left_surround_contrast,
        right_surround_contrast=right_surround_contrast,
        center_flicker_hz=center_flicker_hz,
        surround_flicker_hz=surround_flicker_hz,
        modulation_mode=modulation_mode,
    )
