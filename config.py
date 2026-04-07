from __future__ import annotations

# display configuration
monitor_name = "asus_oled"
monitor_pixels = [1920, 1080]
default_refresh_hz = 120
monitor_width_cm = 35
viewing_distance_cm = 55
fullscreen = True

# general stimulus configuration
bg_color = (0, 0, 0)
units = "deg"

# stimulus timing and flicker
center_flicker_hz = 3
surround_flicker_hz = 3.75

# flicker type (on_off_flicker or binary_counterphase)
modulation_mode = "on_off_flicker" # str converted to enum in stimuli.py

# stimulus geometry
ecc = 5.0
upper_deg = 20.0
lower_deg = 45.0

center_radius = 0.75
center_sf = 1.0
center_mask = "raisedCos"
center_mask_params = {"fringeWidth": 0.1}
center_oris = [45, 55, 75, 315]

center_surround_gap = 0.5
surround_radius = center_radius + center_surround_gap + 1.5
surround_sf = 1.0
surround_mask = "raisedCos"
surround_mask_params = {"fringeWidth": 0.1}
surround_oris = [None, 45, 315]

surround_hole_radius = (center_radius + center_surround_gap) * 2
surround_hole_mask = "raisedCos"
surround_hole_mask_params = {"fringeWidth": 0.15}

# contrasts
left_center_contrast = 0.75
right_center_contrast = 0.75
left_surround_contrast = 1.0
right_surround_contrast = 1.0

# experiment timing
trial_duration = 8
iti_duration = 1
fallback_refresh_hz = 60.0

# hardware
use_labjack = True
require_triggers = True
labjack_device_type = "T7"
labjack_connection_type = "ANY"
labjack_identifier = "ANY"
labjack_fio_lines = [f"FIO{i}" for i in range(8)]
labjack_fio_mask = 0xFF
stimulus_onset_code = 1
stimulus_offset_code = 2
frame_marker_code = 3
trigger_pulse_width_s = 0.005
trigger_min_gap_s = 0.005
frame_marker_interval = 80
