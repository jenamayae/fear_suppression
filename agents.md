# Fear suppression experiment

## Experiment Development Stages:
1. Preconditioning Calibration 
2. Conditioning Calibration 
2. Full Experiment

## Scope
Local rules for the fear suppression PsychoPy experiment, LabJack trigger code, trial generation, data logging, and EEG analysis helpers.

## Data organization
```
rawdata/                        # immutable acquisition output
  sub-<id>/
    ses-<id>/
      eeg/
        *.cnt

workdata/                       # all derived / working files
  sub-<id>/
    ses-<id>/
      trialconditions/          # design matrix (planned trials)
      sourcedata/               # exported / converted data (optional)
      derivatives/              # analysis outputs (fft, snr, plots)
```


## Experiment rules
- keep condition variables in tables, metadata, or logged trial fields, not ad hoc filenames
- preserve frame-based timing logic unless there is a clear reason to change it and the change is approved
- do not modify existing data files unless explicitly asked
may depend on them
- do not modify existing data files 

## Validation
- suggest basic validation checks but do not implement without approval
- do not introduce new durable test contracts, figures of merit, exclusion rules, or pass/fail criteria without human review
- when proposing analysis changes, state whether the change affects preprocessing, measurement, statistics, or visualization
