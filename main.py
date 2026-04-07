import logging
from pathlib import Path
from psychopy import core, data, event, gui, visual

from config import (
    monitor_name,
    monitor_pixels,
    default_refresh_hz,
    monitor_width_cm,
    viewing_distance_cm,
    fullscreen,
    trial_duration,
    iti_duration,
    fallback_refresh_hz,
    use_labjack,
    require_triggers,
    center_flicker_hz,
    surround_flicker_hz,
    trigger_pulse_width_s,
    trigger_min_gap_s,
    stimulus_onset_code,
    stimulus_offset_code,
    frame_marker_code,
    frame_marker_interval,
)

from stimuli import (
    make_window,
    make_stimuli,
    draw_flicker_frame,
    modulation_mode
)
from trials import generate_habituation_trials, generate_acquisition_trials

from hardware import (
    LabjackFio8BitTrigger,
    log_trigger_settings,
    send_stimulus_onset,
    send_stimulus_offset,
    maybe_send_frame_marker,
)

# ----------------------------
# main experiment configuration
# ----------------------------

def get_refresh_hz(win, fallback_hz=fallback_refresh_hz):
    hz = win.getActualFrameRate(
        nIdentical=20,
        nMaxFrames=200,
        nWarmUpFrames=20,
        threshold=1,
    )
    return fallback_hz if hz is None else hz


def main():
   
    exp_info: dict[str, object] = {"subject": "", "session": "001"}

    if not gui.DlgFromDict(exp_info, title="Fear Surround Suppression").OK:
        core.quit()

    exp_info.update(
        {
            "trigger_pulse_width_s": trigger_pulse_width_s,
            "trigger_min_gap_s": trigger_min_gap_s,
            "stimulus_onset_code": stimulus_onset_code,
            "stimulus_offset_code": stimulus_offset_code,
            "frame_marker_code": frame_marker_code,
            "frame_marker_interval": frame_marker_interval,
        }
    )

    Path("data").mkdir(exist_ok=True)
    filename = Path("data") / f"{exp_info['subject']}_{exp_info['session']}"

    exp = data.ExperimentHandler(
        name="fear_surround_suppression",
        extraInfo=exp_info,
        dataFileName=str(filename),
        saveWideText=True,
        savePickle=False,
    )

    win = make_window(
        size=monitor_pixels,
        fullscr=fullscreen,
        monitor_name=monitor_name,
        monitor_width_cm=monitor_width_cm,
        viewing_distance_cm=viewing_distance_cm,
    )
    stims = make_stimuli(win)
    refresh_hz = get_refresh_hz(win)
    global_frame_num = 0

    trigger = None

    try:
        if use_labjack:
            try:
                trigger = LabjackFio8BitTrigger()
                trigger.open()
                log_trigger_settings()
            except Exception as exc:
                if require_triggers:
                    win.close()
                    raise RuntimeError(f"LabJack trigger startup failed: {exc}") from exc
                logging.warning("LabJack trigger unavailable; continuing without triggers: %s", exc)
                print(f"WARNING: LabJack trigger unavailable; continuing without triggers: {exc}")

        habituation_trials = generate_habituation_trials()
        acquisition_trials = generate_acquisition_trials()

        show_message(win, "Press SPACE to begin Phase I.\nPress ESC to quit.")
        global_frame_num = run_block(
            win=win,
            stims=stims,
            exp=exp,
            trials=habituation_trials,
            phase_name="habituation",
            refresh_hz=refresh_hz,
            global_frame_num=global_frame_num,
            modulation_mode=modulation_mode,
            trigger=trigger,
        )

        show_message(win, "Press SPACE to begin Phase II.\nPress ESC to quit.")
        global_frame_num = run_block(
            win=win,
            stims=stims,
            exp=exp,
            trials=acquisition_trials,
            phase_name="acquisition",
            refresh_hz=refresh_hz,
            global_frame_num=global_frame_num,
            modulation_mode=modulation_mode,
            trigger=trigger,
        )

        show_message(win, "End of experiment. Thank you!\nPress SPACE to exit.")

    finally:
        if trigger is not None:
            trigger.close()

    exp.saveAsWideText(str(filename) + ".csv")
    win.close()
    core.quit()


def show_message(win, text):
    event.clearEvents(eventType="keyboard")
    msg = visual.TextStim(win=win, text=text)
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


def run_trial(win, stims, trial, trial_duration, refresh_hz, global_frame_num, modulation_mode, trigger=None):
    trial_start_frame = global_frame_num
    n_frames = round(trial_duration * refresh_hz)

    if trigger is not None:
        send_stimulus_onset(trigger)

    for _ in range(n_frames):
        draw_flicker_frame(
            stims=stims,
            frame_num=global_frame_num,
            refresh_hz=refresh_hz,
            center_ori=trial["center_ori"],
            surround_ori=trial["surround_ori"],
            left_center_contrast=trial["left_center_contrast"],
            right_center_contrast=trial["right_center_contrast"],
            left_surround_contrast=trial["left_surround_contrast"],
            right_surround_contrast=trial["right_surround_contrast"],
            center_flicker_hz=center_flicker_hz,
            surround_flicker_hz=surround_flicker_hz,
            modulation_mode=modulation_mode,
        )

        win.flip()
        global_frame_num += 1

        if trigger is not None:
            maybe_send_frame_marker(trigger, global_frame_num) 

        if "escape" in event.getKeys():
            win.close()
            core.quit()

    trial_end_frame = global_frame_num - 1
    if trigger is not None:
        send_stimulus_offset(trigger)

    return global_frame_num, trial_start_frame, trial_end_frame


def run_iti(win, stims, iti_duration, refresh_hz, global_frame_num):
    n_frames = round(iti_duration * refresh_hz)

    for _ in range(n_frames):
        stims["fixation"].draw()
        win.flip()
        global_frame_num += 1

        if "escape" in event.getKeys():
            win.close()
            core.quit()

    return global_frame_num


def log_trial(exp, phase_name, trial_num, trial, trial_start_frame, trial_end_frame, refresh_hz):
    exp.addData("phase", phase_name)
    exp.addData("trial_num", trial_num)
    exp.addData("center_ori", trial["center_ori"])
    exp.addData("surround_ori", trial["surround_ori"])
    exp.addData("surround_present", trial["surround_present"])
    exp.addData("cs_type", trial["cs_type"])
    exp.addData("reinforced", trial["reinforced"])
    exp.addData("left_center_contrast", trial["left_center_contrast"])
    exp.addData("right_center_contrast", trial["right_center_contrast"])
    exp.addData("left_surround_contrast", trial["left_surround_contrast"])
    exp.addData("right_surround_contrast", trial["right_surround_contrast"])
    exp.addData("trial_start_frame", trial_start_frame)
    exp.addData("trial_end_frame", trial_end_frame)
    exp.addData("refresh_hz", refresh_hz if trial_num == 1 else "")
    exp.nextEntry()


def run_block(win, stims, exp, trials, phase_name, refresh_hz, global_frame_num, modulation_mode, trigger=None):
    for trial_num, trial in enumerate(trials, start=1):
        global_frame_num, trial_start_frame, trial_end_frame = run_trial(
            win=win,
            stims=stims,
            trial=trial,
            trial_duration=trial_duration,
            refresh_hz=refresh_hz,
            global_frame_num=global_frame_num,
            modulation_mode=modulation_mode,
            trigger=trigger,
        )

        log_trial(
            exp=exp,
            phase_name=phase_name,
            trial_num=trial_num,
            trial=trial,
            trial_start_frame=trial_start_frame,
            trial_end_frame=trial_end_frame,
            refresh_hz=refresh_hz,
        )

    return global_frame_num


if __name__ == "__main__":
    main()
