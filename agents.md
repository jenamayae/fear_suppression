
## Scope
Local rules for the suppression_stimuli PsychoPy experiment.

## Data organization
```
data/                       
  sub-<id>/
    ses-<id>/ 
      rawdata/
        sub-<id>_ses-<id>_run-<id>_eeg.cnt
      metadata/
        session_info_run-<id>.yaml          # session metadata
        trial_conditions_run-<id>.csv               # trial structure  
      derivatives/              # analysis outputs (fft, snr, plots)
```


## Experiment rules
- keep condition variables in tables, metadata, or logged trial fields, not ad hoc filenames
- preserve frame-based timing logic unless there is a clear reason to change it and the change is approved
- do not modify existing data files

## Validation
- suggest basic validation checks but do not implement without approval
- do not introduce new durable test contracts, figures of merit, exclusion rules, or pass/fail criteria without human review
- when proposing analysis changes, state whether the change affects preprocessing, measurement, statistics, or visualization
