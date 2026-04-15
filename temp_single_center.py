import random
from datetime import datetime
from pathlib import Path
import csv

from psychopy import core, event, visual
from psychopy.visual.grating import GratingStim

from config import (
    monitor_name,
    monitor_pixels,
    monitor_width_cm,
    viewing_distance_cm,
    fullscreen,
    fallback_refresh_hz,
    trial_duration,
    iti_duration,
    center_radius,
    center_sf,
    center_mask,
    center_mask_params,
    center_contrast,
    use_labjack,
    require_triggers,
    simulate_labjack,
)
from stimuli import (
    make_window,
    ModulationMode,
    cycle_value,
    modulation_mode_dispatcher,
)
from hardware import (
    LabjackFio8BitTrigger,
    SimulatedLabjackFio8BitTrigger,
    log_trigger_settings,
    send_trial_start_codes,
    send_stimulus_offset,
    maybe_send_frame_marker,
    condition_code_for_mode,
)


FLICKER_HZ = 7.5
TRIALS_PER_CONDITION = 10


def get_refresh_hz(win, fallback_hz=fallback_refresh_hz):
    hz = win.getActualFrameRate(
        nIdentical=20,
        nMaxFrames=200,
        nWarmUpFrames=20,
        threshold=1,
    )
    return fallback_hz if hz is None else hz


def build_trials(n_per_condition=TRIALS_PER_CONDITION):
    trials = []
    for modulation_mode in (ModulationMode.phase_reversal, ModulationMode.on_off_flicker):
        for _ in range(n_per_condition):
            trials.append(modulation_mode)
    random.shuffle(trials)
    return trials


def show_message(win, text):
    event.clearEvents(eventType="keyboard")
    msg = visual.TextStim(win=win, text=text, color="white", autoLog=False)
    msg.draw()
    win.flip()

    while True:
        keys = event.waitKeys(keyList=["space", "escape"])
        if keys is None:
            continue
        if "escape" in keys:
            win.close()
            core.quit()
        if "space" in keys:
            return


def run_trial(
    win,
    center,
    fixation,
    modulation_mode,
    refresh_hz,
    global_frame_num,
    trigger=None,
):
    n_frames = round(trial_duration * refresh_hz)
    trial_start_frame = global_frame_num
    if trigger is not None:
        send_trial_start_codes(trigger, modulation_mode)

    for frame_num in range(n_frames):
        cyc_value = cycle_value(frame_num, refresh_hz, FLICKER_HZ)
        cyc = cyc_value % 1.0
        cycle_index = int(cyc_value)
        phase, gain = modulation_mode_dispatcher(cyc, cycle_index, modulation_mode)

        center.phase = phase
        center.contrast = center_contrast * gain

        center.draw()
        fixation.draw()
        win.flip()
        global_frame_num += 1

        if trigger is not None:
            maybe_send_frame_marker(trigger, global_frame_num)

        if "escape" in event.getKeys(keyList=["escape"]):
            win.close()
            core.quit()

    if trigger is not None:
        send_stimulus_offset(trigger)

    trial_end_frame = global_frame_num - 1
    return global_frame_num, trial_start_frame, trial_end_frame

def run_iti(win, fixation, refresh_hz, global_frame_num):
    n_frames = round(iti_duration * refresh_hz)
    for _ in range(n_frames):
        fixation.draw()
        win.flip()
        global_frame_num += 1
        if "escape" in event.getKeys(keyList=["escape"]):
            win.close()
            core.quit()
    return global_frame_num


def main():
    win = make_window(
        size=monitor_pixels,
        fullscr=fullscreen,
        monitor_name=monitor_name,
        monitor_width_cm=monitor_width_cm,
        viewing_distance_cm=viewing_distance_cm,
    )

    center = GratingStim(
        win=win,
        tex="sin",
        mask=center_mask,
        maskParams=center_mask_params,
        size=10,
        sf=center_sf,
        contrast=center_contrast,
        ori=45,
        phase=0.0,
        pos=(0, 0),
        autoLog=False,
    )
    fixation = visual.TextStim(
        win=win,
        text="+",
        pos=(0, 0),
        height=0.5,
        color="white",
        autoLog=False,
    )

    refresh_hz = get_refresh_hz(win)
    trials = build_trials(TRIALS_PER_CONDITION)
    global_frame_num = 0
    trigger = None
    out_dir = Path("data")
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = out_dir / f"temp_single_center_{timestamp}.csv"

    show_message(
        win,
        (
            f"Single-center temporary run\n"
            f"{TRIALS_PER_CONDITION} trials per condition (random interleaved)\n"
            f"Modes: phase_reversal, on_off_flicker\n"
            f"Flicker frequency: {FLICKER_HZ} Hz\n\n"
            "Press SPACE to begin, ESC to quit."
        ),
    )

    try:
        if use_labjack:
            try:
                trigger_class = (
                    SimulatedLabjackFio8BitTrigger if simulate_labjack else LabjackFio8BitTrigger
                )
                trigger = trigger_class()
                trigger.open()
                log_trigger_settings()
            except Exception as exc:
                if require_triggers:
                    win.close()
                    raise RuntimeError(f"LabJack trigger startup failed: {exc}") from exc
                print(f"WARNING: LabJack trigger unavailable; continuing without triggers: {exc}")

        with csv_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "trial_num",
                    "modulation_mode",
                    "condition_trigger_code",
                    "flicker_hz",
                    "refresh_hz",
                    "trial_start_frame",
                    "trial_end_frame",
                ],
            )
            writer.writeheader()

            for trial_idx, modulation_mode in enumerate(trials, start=1):
                condition_trigger_code = condition_code_for_mode(modulation_mode)
                print(
                    f"Trial {trial_idx:02d}/{len(trials)} | "
                    f"mode={modulation_mode.value} | "
                    f"flicker_hz={FLICKER_HZ} | "
                    f"condition_trigger_code={condition_trigger_code}"
                )
                global_frame_num, trial_start_frame, trial_end_frame = run_trial(
                    win=win,
                    center=center,
                    fixation=fixation,
                    modulation_mode=modulation_mode,
                    refresh_hz=refresh_hz,
                    global_frame_num=global_frame_num,
                    trigger=trigger,
                )
                writer.writerow(
                    {
                        "trial_num": trial_idx,
                        "modulation_mode": modulation_mode.value,
                        "condition_trigger_code": condition_trigger_code,
                        "flicker_hz": FLICKER_HZ,
                        "refresh_hz": refresh_hz,
                        "trial_start_frame": trial_start_frame,
                        "trial_end_frame": trial_end_frame,
                    }
                )
                f.flush()
                global_frame_num = run_iti(
                    win=win,
                    fixation=fixation,
                    refresh_hz=refresh_hz,
                    global_frame_num=global_frame_num,
                )
    finally:
        if trigger is not None:
            trigger.close()
    print(f"Saved CSV: {csv_path}")

    show_message(win, "Done.\nPress SPACE to exit.")
    win.close()
    core.quit()


if __name__ == "__main__":
    main()
