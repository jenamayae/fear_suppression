from __future__ import annotations
from enums import SurroundCondition

# display configuration
monitor_name = "asus_oled"
monitor_pixels = [1920, 1080] # actual [2560, 1440]
fallback_refresh_hz = 120.0
monitor_width_cm = 52.7
viewing_distance_cm = 80
fullscreen = True
bg_color = (0, 0, 0)
units = "deg"

# stimulation frequencies
center_flicker_hz = 6
surround_flicker_hz = 7.5

# location & size
ecc = 10 # converted to cartesian in stimuli.py
upper_deg = 20.0
lower_deg = 45.0
center_radius = 0.75
center_surround_gap = 0.5
surround_radius = center_radius + center_surround_gap + 1.5

# center
center_orientations = [45]
center_sf = 1.0
center_contrast = 0.75
center_mask, center_mask_params = "raisedCos", {"fringeWidth": 0.1}

# surround conditions
surround_orientations = [45]
surround_conditions = [
    SurroundCondition.absent,
    SurroundCondition.static,
    SurroundCondition.dynamic,
]
surround_sf = 1.0
surround_contrast = 1.0
surround_mask, surround_mask_params = "raisedCos", {"fringeWidth": 0.1}

# surround inner radius
surround_hole_radius = (center_radius + center_surround_gap) * 2
surround_hole_mask, surround_hole_mask_params = "raisedCos", {"fringeWidth": 0.15}

# trials
trial_duration = 10
iti_duration = 2
trials_per_condition = 10

# labjack
use_labjack = True
require_triggers = True
simulate_labjack = True

labjack_device_type = "T7"
labjack_connection_type = "ANY"
labjack_identifier = "ANY"
labjack_fio_lines = [f"FIO{i}" for i in range(8)]
labjack_fio_mask = 0xFF

# event codes
stimulus_onset_code = 1
stimulus_offset_code = 2
frame_marker_code = 3
on_off_flicker_code = 4
phase_reversal_code = 5

trigger_pulse_width_s = 0.005
trigger_min_gap_s = 0.005
frame_marker_interval = 80
