from __future__ import annotations

# Display configuration
monitor_name = "asus_oled"
monitor_pixels = [1920, 1080]
default_refresh_hz = 120
monitor_width_cm = 35
viewing_distance_cm = 55
fullscreen = True

bg_color = (0, 0, 0)
units = "deg"

# Stimulus flicker frequency
center_flicker_hz = 3
surround_flicker_hz = 3.75

# Flicker type (on_off_flicker or phase_reversal)
modulation_mode = "phase_reversal" # str converted to enum in stimuli.py
upper_lower_phase_mode = "offset" # str converted to enum in stimuli.py

# Stimulus location
ecc = 5.0 # polar coordinates converted to cartesion coordinates in stimuli.py
upper_deg = 20.0
lower_deg = 45.0

# Center geometry
center_radius = 0.75
center_sf = 1.0
center_mask = "raisedCos"
center_mask_params = {"fringeWidth": 0.1}
center_oris = [45]

# Surround geometry
center_surround_gap = 0.5
surround_radius = center_radius + center_surround_gap + 1.5
surround_sf = 1.0
surround_mask = "raisedCos"
surround_mask_params = {"fringeWidth": 0.1}
surround_oris = [None, 45, 315]

surround_hole_radius = (center_radius + center_surround_gap) * 2
surround_hole_mask = "raisedCos"
surround_hole_mask_params = {"fringeWidth": 0.15}

# Contrasts
center_contrast = 0.75
surround_contrast = 1.0

# Experiment timing
trial_duration = 8
iti_duration = 2
fallback_refresh_hz = 120.0
trials_per_condition = 5

# Hardware
use_labjack = True
require_triggers = True
simulate_labjack = True

labjack_device_type = "T7"
labjack_connection_type = "ANY"
labjack_identifier = "ANY"
labjack_fio_lines = [f"FIO{i}" for i in range(8)]
labjack_fio_mask = 0xFF

# Event codes
stimulus_onset_code = 1
stimulus_offset_code = 2
frame_marker_code = 3

trigger_pulse_width_s = 0.005
trigger_min_gap_s = 0.005
frame_marker_interval = 80
