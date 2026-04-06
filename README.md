# Preconditioning Calibration Phase
## Purpose: 
Systematically evaluate stimulus parameters to identify configurations that produce stable, robust, and interpretable ssvep readouts of surround suppression

## Parameter Space:
the following dimensions to be explicitly varied and evaluated:
* summation strategy: upper/lower phase opposition; spatial arrangement; retinal location
* modulation mode: binary_counterphase vs on_off_flicker; interaction with summation strategy and im components
* orientation: surround suppression tuning properties; alignment with fear conditioning paradigm and difference-of-gaussians model 
* contrast: fixed vs task-based; interaction with suppression strength and response amplitude
* trial structure: timing, iti, and compatibility with downstream fear conditioning measures)
* flicker frequency: 

### frequency constraints: 
* center and surround frequencies must be integer divisors of refresh_rate_hz
* frequencies must be separable at the level of fundamentals and im components
* im terms (nf1 ± mf2) must fall into resolvable frequency bins given epoch duration
* discrete bins: epoch length selected such that f × T yields integer cycle counts 

## Outputs:
* validated stimulus set with high ssvep snr
* reliable extraction of linear (fundamental) and nonlinear (im) signals
* validated temporal design compatible with other outcome measures
* predefined analysis targets for the fear conditioning phase
* finalized subset of stimulus conditions to carry forward into conditioning

## Task List:
- [x] repo set up and sharing
(upload to github; share with ryan and martin)
- [] code refactor pass
(improve structure, modularity, and parameter control for onsite iteration)
- [] stimulus verification
(frame-by-frame validation of rendering, phase relationships, and timing)
- [] temporal and trial design
(finalize epoch length, trial duration, iti, and event triggers)
- [] analysis specification
(define analysis targets; create local agents.md for pipeline behavior)
- [] analysis pipeline implementation
(fft extraction, snr calculation, im identification)
- [] pipeline validation
(synthetic/known-answer datasets; confirm recovery of injected signals)
- [] empirical validation
(test pipeline and stimuli with pilot eeg recordings)

