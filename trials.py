import random

from config import (
    center_orientations,
    surround_orientations,
    surround_conditions,
    center_contrast,
    surround_contrast,
    trials_per_condition,
)
from enums import ModulationMode, SurroundCondition, UpperLowerPhaseMode

def make_trial(
    stage,
    condition_id,
    center_orientation,
    surround_orientation,
    surround_condition,
    modulation_mode,
    upper_lower_phase_mode,
    center_contrast,
    surround_contrast,
):
    return {
        "stage": stage,
        "condition_id": condition_id,
        "center_orientation": center_orientation,
        "surround_orientation": surround_orientation,
        "surround_condition": surround_condition,
        "modulation_mode": modulation_mode.value,
        "upper_lower_phase_mode": upper_lower_phase_mode.value,
        "center_contrast": center_contrast,
        "surround_contrast": surround_contrast,
    }


def generate_trials(shuffle=True):
    trials = []
    condition_id = 0

    for center_orientation in center_orientations:
        for surround_condition_value in surround_conditions:
            surround_orientation_values = (
                [None]
                if surround_condition_value == SurroundCondition.absent
                else surround_orientations
            )

            for surround_orientation in surround_orientation_values:
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
                                    center_orientation=center_orientation,
                                    surround_orientation=surround_orientation,
                                    surround_condition=surround_condition_value,
                                    modulation_mode=modulation_mode,
                                    upper_lower_phase_mode=upper_lower_phase_mode,
                                    center_contrast=center_contrast,
                                    surround_contrast=surround_contrast,
                                )
                            )

    if shuffle:
        random.shuffle(trials)

    return trials
