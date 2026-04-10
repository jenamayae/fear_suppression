from psychopy import core, event, visual

from config import (
    monitor_name,
    monitor_width_cm,
    viewing_distance_cm,
    center_flicker_hz,
    surround_flicker_hz,
    center_contrast,
    surround_contrast,
)
from stimuli import (
    make_window,
    make_stimuli,
    draw_flicker_frame,
    center_oris,
    surround_oris,
    ModulationMode,
    UpperLowerPhaseMode,
)


# ---------------------------------
# demo configuration
# ---------------------------------
window_size = (1400, 900)
fallback_refresh_hz = 60.0
forced_refresh_hz = 120
use_forced_refresh = False

modulation_modes = [
    ModulationMode.phase_reversal,
    ModulationMode.on_off_flicker,
]
upper_lower_phase_modes = [
    UpperLowerPhaseMode.synchronized,
    UpperLowerPhaseMode.offset,
]

def cycle_value(values, current, step=1):
    i = values.index(current)
    return values[(i + step) % len(values)]


def get_refresh_hz(win, fallback_hz=fallback_refresh_hz):
    hz = win.getActualFrameRate(
        nIdentical=20,
        nMaxFrames=200,
        nWarmUpFrames=20,
        threshold=1,
    )
    return fallback_hz if hz is None else hz


def make_overlay_text(state, refresh_hz, measured_refresh_hz):
    t_sec = state["frame_num"] / refresh_hz
    surround_label = "None" if state["surround_ori"] is None else str(state["surround_ori"])

    return (
        f"frame={state['frame_num']}   t={t_sec:.4f}s   "
        f"play={'ON' if state['playing'] else 'OFF'}\n"
        f"mode={state['modulation_mode'].value}   "
        f"phase_mode={state['upper_lower_phase_mode'].value}   "
        f"refresh_hz={refresh_hz:.3f}   measured_hz={measured_refresh_hz:.3f}\n"
        f"center_hz={center_flicker_hz:.2f}   surround_hz={surround_flicker_hz:.2f}\n"
        f"center_ori={state['center_ori']}   surround_ori={surround_label}\n"
        "RIGHT +1 frame | LEFT -1 frame | UP +10 | DOWN -10 | SPACE play/pause | "
        "C next center | S next surround | X toggle surround | T mode | P phase | R reset | H overlay | ESC quit"
    )


def main():
    win = make_window(
        size=window_size,
        fullscr=False,
        monitor_name=monitor_name,
        monitor_width_cm=monitor_width_cm,
        viewing_distance_cm=viewing_distance_cm,
    )
    stims = make_stimuli(win)

    measured_refresh_hz = get_refresh_hz(win)
    refresh_hz = forced_refresh_hz if use_forced_refresh else measured_refresh_hz

    surround_cycle = list(surround_oris)

    state = {
        "frame_num": 0,
        "playing": False,   # starts paused for true frame-by-frame demo
        "show_overlay": True,
        "center_ori": center_oris[0],
        "surround_ori": surround_cycle[0] if surround_cycle else None,
        "modulation_mode": modulation_modes[0],
        "upper_lower_phase_mode": upper_lower_phase_modes[0],
    }

    overlay = visual.TextStim(
        win=win,
        text="",
        pos=(0, -10),
        height=0.42,
        color="white",
        wrapWidth=18,
        alignText="center",
        anchorHoriz="center",
        autoLog=False,
    )

    event.clearEvents(eventType="keyboard")

    while True:
        keys = event.getKeys(
            keyList=["escape", "space", "right", "left", "up", "down", "c", "s", "x", "t", "p", "r", "h"]
        )

        if "escape" in keys:
            break
        if "space" in keys:
            state["playing"] = not state["playing"]
        if "right" in keys:
            state["frame_num"] += 1
        if "left" in keys:
            state["frame_num"] = max(0, state["frame_num"] - 1)
        if "up" in keys:
            state["frame_num"] += 10
        if "down" in keys:
            state["frame_num"] = max(0, state["frame_num"] - 10)
        if "c" in keys:
            state["center_ori"] = cycle_value(center_oris, state["center_ori"], 1)
        if "s" in keys and surround_cycle:
            state["surround_ori"] = cycle_value(surround_cycle, state["surround_ori"], 1)
        if "x" in keys:
            state["surround_ori"] = None if state["surround_ori"] is not None else surround_cycle[0]
        if "t" in keys:
            state["modulation_mode"] = cycle_value(modulation_modes, state["modulation_mode"])
        if "p" in keys:
            state["upper_lower_phase_mode"] = cycle_value(
                upper_lower_phase_modes,
                state["upper_lower_phase_mode"],
            )
        if "r" in keys:
            state["frame_num"] = 0
        if "h" in keys:
            state["show_overlay"] = not state["show_overlay"]

        if state["playing"]:
            state["frame_num"] += 1

        draw_flicker_frame(
            stims=stims,
            frame_num=state["frame_num"],
            refresh_hz=refresh_hz,
            center_ori=state["center_ori"],
            surround_ori=state["surround_ori"],
            center_contrast=center_contrast,
            surround_contrast=surround_contrast,
            center_flicker_hz=center_flicker_hz,
            surround_flicker_hz=surround_flicker_hz,
            modulation_mode=state["modulation_mode"],
            upper_lower_phase_mode=state["upper_lower_phase_mode"],
        )

        if state["show_overlay"]:
            overlay.text = make_overlay_text(state, refresh_hz, measured_refresh_hz)
            overlay.draw()

        win.flip()

    win.close()
    core.quit()


if __name__ == "__main__":
    main()
    
