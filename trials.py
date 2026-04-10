import random

from config import (
    center_oris,
    surround_oris,
    center_contrast,
    surround_contrast,
    trials_per_condition,
)
from stimuli import ModulationMode, UpperLowerPhaseMode

def make_trial(
    stage,
    condition_id,
    center_ori,
    surround_ori,
    modulation_mode,
    upper_lower_phase_mode,
    center_contrast,
    surround_contrast,
):
    return {
        "stage": stage,
        "condition_id": condition_id,
        "center_ori": center_ori,
        "surround_ori": surround_ori,
        "modulation_mode": modulation_mode.value,
        "upper_lower_phase_mode": upper_lower_phase_mode.value,
        "center_contrast": center_contrast,
        "surround_contrast": surround_contrast,
    }


def generate_trials(shuffle=True):
    trials = []
    condition_id = 0

    for center_ori in center_oris:
        for surround_ori in surround_oris:
            for modulation_mode in (
                ModulationMode.phase_reversal,
                ModulationMode.on_off_flicker,
            ):
                for upper_lower_phase_mode in (
                    UpperLowerPhaseMode.synchronized,
                    UpperLowerPhaseMode.offset,
                ):
                    condition_id += 1

                    for _ in range(trials_per_condition):
                        trials.append(
                            make_trial(
                                stage="calibration",
                                condition_id=condition_id,
                                center_ori=center_ori,
                                surround_ori=surround_ori,
                                modulation_mode=modulation_mode,
                                upper_lower_phase_mode=upper_lower_phase_mode,
                                center_contrast=center_contrast,
                                surround_contrast=surround_contrast,
                            )
                        )

    if shuffle:
        random.shuffle(trials)

    return trials
