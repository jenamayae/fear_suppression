import logging
from datetime import datetime
from pathlib import Path
from psychopy import core, data, event, gui, visual

from config import (
    monitor_name,
    monitor_pixels,
    monitor_width_cm,
    viewing_distance_cm,
    fullscreen,
    trial_duration,
    iti_duration,
    trials_per_condition,
    fallback_refresh_hz,
    use_labjack,
    require_triggers,
    simulate_labjack,
    center_flicker_hz,
    surround_flicker_hz,
    trigger_pulse_width_s,
    trigger_min_gap_s,
    stimulus_onset_code,
    stimulus_offset_code,
    frame_marker_code,
    frame_marker_interval,
    ecc,
    upper_deg,
    lower_deg,
    center_sf,
    surround_sf,
)
from stimuli import (
    make_window,
    make_stimuli,
    draw_flicker_frame,
    ModulationMode,
    UpperLowerPhaseMode,
)
from trials import generate_trials
from hardware import (
    LabjackFio8BitTrigger,
    SimulatedLabjackFio8BitTrigger,
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

def make_run_paths(sub_id, ses_id, run_id):
    run_root = Path("data") / f"sub-{sub_id}" / f"ses-{ses_id}"
    rawdata_dir = run_root / "rawdata"
    metadata_dir = run_root / "metadata"
    derivatives_dir = run_root / "derivatives"

    return {
        "run_root": run_root,
        "rawdata_dir": rawdata_dir,
        "metadata_dir": metadata_dir,
        "derivatives_dir": derivatives_dir,
        "session_info_path": metadata_dir / f"session_info_run-{run_id}.yaml",
        "trial_conditions_path": metadata_dir / f"trial_conditions_run-{run_id}",
    }

def get_next_run_id(sub_id, ses_id):
    metadata_dir = Path("data") / f"sub-{sub_id}" / f"ses-{ses_id}" / "metadata"
    if not metadata_dir.exists():
        return "001"

    run_ids = []

    for path in metadata_dir.glob("trial_conditions_run-*.csv"):
        name = path.stem
        run_str = name.removeprefix("trial_conditions_run-")
        if run_str.isdigit():
            run_ids.append(int(run_str))

    if not run_ids:
        return "001"

    return f"{max(run_ids) + 1:03d}"

def collect_exp_info():
    participant_info: dict[str, object] = {
        "subject": "",
        "session": "001",
    }

    if not gui.DlgFromDict(
        participant_info,
        title="Surround Suppression Stimuli",
        sortKeys=False,
    ).OK:
        return None

    sub_id = str(participant_info["subject"])
    ses_id = str(participant_info["session"])

    exp_info: dict[str, object] = {
        "subject": sub_id,
        "session": ses_id,
        "run": get_next_run_id(sub_id, ses_id),
    }

    if not gui.DlgFromDict(
        exp_info,
        title="Surround Suppression Stimuli",
        sortKeys=False,
    ).OK:
        return None

    return {
        "subject": str(exp_info["subject"]),
        "session": str(exp_info["session"]),
        "run": str(exp_info["run"]),
    }

def write_session_info_yaml(path, session_info):
    lines = []

    for section_name, section_values in session_info.items():
        lines.append(f"{section_name}:")
        for key, value in section_values.items():
            if isinstance(value, dict):
                lines.append(f"  {key}:")
                for nested_key, nested_value in value.items():
                    lines.append(f"    {nested_key}: {nested_value}")
            else:
                lines.append(f"  {key}: {value}")
        lines.append("")

    path.write_text("\n".join(lines) + "\n")

def main():
    stage_name = "calibration"
    datetime_start = datetime.now().isoformat(timespec="seconds")

    exp_info = collect_exp_info()
    if exp_info is None:
        core.quit()

    sub_id = exp_info["subject"]
    ses_id = exp_info["session"]
    run_id = exp_info["run"]
    run_paths = make_run_paths(sub_id, ses_id, run_id)

    run_paths["rawdata_dir"].mkdir(parents=True, exist_ok=True)
    run_paths["metadata_dir"].mkdir(parents=True, exist_ok=True)
    run_paths["derivatives_dir"].mkdir(parents=True, exist_ok=True)

    exp = data.ExperimentHandler(
        name="surround_suppression_stimuli",
        extraInfo=exp_info,
        dataFileName=str(run_paths["trial_conditions_path"]),
        saveWideText=True,
        savePickle=False,
    )

    for name in ("thisRow.t", "notes"): # remove unused psychopy colums
        if name in exp.dataNames:
            exp.dataNames.remove(name)

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

    session_info = { # yaml encoding
        "participant": {
            "sub_id": sub_id,
            "ses_id": ses_id,
            "run_id": run_id,
        },
        "session": {
            "datetime_start": datetime_start,
            "stage": stage_name,
        },
        "stim configs": {
            
            "center_hz": center_flicker_hz,
            "surround_hz": surround_flicker_hz,
            
            "ecc": ecc,
            "upper_deg": upper_deg,
            "lower_deg": lower_deg,
            
            "center_sf": center_sf,
            "surround_sf": surround_sf,
            
        },
        "trial configs": {
            "trial_duration": trial_duration,
            "iti_duration": iti_duration,
            "trials_per_condition": trials_per_condition,
        },
        "hardware": {
            "monitor_name": monitor_name,
            "monitor_pixels": monitor_pixels,
            "monitor_width_cm": monitor_width_cm,
            "viewing_distance_cm": viewing_distance_cm,
            "refresh_hz": refresh_hz,
        },
        "events": {
            "stimulus_onset_code": stimulus_onset_code,
            "stimulus_offset_code": stimulus_offset_code,
            "frame_marker_code": frame_marker_code,
            "frame_marker_interval": frame_marker_interval,
            "trigger_pulse_width_s": trigger_pulse_width_s,
            "trigger_min_gap_s": trigger_min_gap_s,
        },
    }
    write_session_info_yaml(run_paths["session_info_path"], session_info)

    trigger = None

    try:
        if use_labjack:
            try:
                trigger_class = SimulatedLabjackFio8BitTrigger if simulate_labjack else LabjackFio8BitTrigger
                trigger = trigger_class()
                trigger.open()
                log_trigger_settings()
            except Exception as exc:
                if require_triggers:
                    win.close()
                    raise RuntimeError(f"LabJack trigger startup failed: {exc}") from exc
                logging.warning("LabJack trigger unavailable; continuing without triggers: %s", exc)
                print(f"WARNING: LabJack trigger unavailable; continuing without triggers: {exc}")

        trials = generate_trials()

        show_message(win, "Press SPACE to begin calibration.\nPress ESC to quit.")

        global_frame_num = run_block(
            win=win,
            stims=stims,
            exp=exp,
            trials=trials,
            stage_name=stage_name,
            refresh_hz=refresh_hz,
            global_frame_num=global_frame_num,
            trigger=trigger,
        )

        show_message(win, "End of experiment. Thank you!\nPress SPACE to exit.")

    finally:
        if trigger is not None:
            trigger.close()

    exp.saveAsWideText(str(run_paths["trial_conditions_path"]) + ".csv")
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


def run_trial(win, stims, trial, trial_duration, refresh_hz, global_frame_num, trigger=None):
    trial_start_frame = global_frame_num
    n_frames = round(trial_duration * refresh_hz)
    modulation_mode = ModulationMode(trial["modulation_mode"])
    upper_lower_phase_mode = UpperLowerPhaseMode(trial["upper_lower_phase_mode"])

    if trigger is not None:
        send_stimulus_onset(trigger)

    for _ in range(n_frames):
        draw_flicker_frame(
            stims=stims,
            frame_num=global_frame_num,
            refresh_hz=refresh_hz,
            center_ori=trial["center_ori"],
            surround_ori=trial["surround_ori"],
            center_contrast=trial["center_contrast"],
            surround_contrast=trial["surround_contrast"],
            center_flicker_hz=center_flicker_hz,
            surround_flicker_hz=surround_flicker_hz,
            modulation_mode=modulation_mode,
            upper_lower_phase_mode=upper_lower_phase_mode,
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


def log_trial(exp, trial_num, trial, trial_start_frame, trial_end_frame, refresh_hz):
    exp.addData("trial_num", trial_num)
    exp.addData("upper_lower_phase_mode", trial["upper_lower_phase_mode"])
    exp.addData("modulation_mode", trial["modulation_mode"])
    exp.addData("center_flicker_hz", center_flicker_hz)
    exp.addData("surround_flicker_hz", surround_flicker_hz)
    exp.addData("center_ori", trial["center_ori"])
    exp.addData("surround_ori", trial["surround_ori"])
    exp.addData("center_contrast", trial["center_contrast"])
    exp.addData("surround_contrast", trial["surround_contrast"])
    exp.addData("refresh_hz", refresh_hz)
    exp.addData("trial_start_frame", trial_start_frame)
    exp.addData("trial_end_frame", trial_end_frame)
    exp.addData("condition_id", trial["condition_id"])
    exp.nextEntry()


def run_block(win, stims, exp, trials, stage_name, refresh_hz, global_frame_num, trigger=None):
    for trial_num, trial in enumerate(trials, start=1):
        global_frame_num, trial_start_frame, trial_end_frame = run_trial(
            win=win,
            stims=stims,
            trial=trial,
            trial_duration=trial_duration,
            refresh_hz=refresh_hz,
            global_frame_num=global_frame_num,
            trigger=trigger,
        )

        log_trial(
            exp=exp,
            trial_num=trial_num,
            trial=trial,
            trial_start_frame=trial_start_frame,
            trial_end_frame=trial_end_frame,
            refresh_hz=refresh_hz,
        )

        global_frame_num = run_iti(
            win=win,
            stims=stims,
            iti_duration=iti_duration,
            refresh_hz=refresh_hz,
            global_frame_num=global_frame_num,
        )

    return global_frame_num


if __name__ == "__main__":
    main()
