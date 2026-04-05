from psychopy import core, event

from stimuli import (
    make_window,
    make_stimuli,
    draw_trial_frame,
    left_center_contrast,
    right_center_contrast,
    left_surround_contrast,
    right_surround_contrast,
)

# Example trial to inspect visually
center_ori = 45
surround_ori = 45  # use None, 45, or 315

trial_duration = 10.0  # seconds, just for inspection

win = make_window()
stims = make_stimuli(win)

trial_clock = core.Clock()

while trial_clock.getTime() < trial_duration:
    t = trial_clock.getTime()

    draw_trial_frame(
        stims=stims,
        t=t,
        center_ori=center_ori,
        surround_ori=surround_ori,
        left_center_contrast=left_center_contrast,
        right_center_contrast=right_center_contrast,
        left_surround_contrast=left_surround_contrast,
        right_surround_contrast=right_surround_contrast,
    )
    win.flip()

    keys = event.getKeys()
    if "escape" in keys:
        break

win.close()
core.quit()