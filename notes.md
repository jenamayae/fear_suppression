# preconditioning calibration phase 
optimize and validate stimuli configurations that yield stable, robust, and interpretable ssvep readouts of surround suppression

## considerations:
    summation strategy (upper/lower phase opposition; stimuli sizes and retinal location)
    modulation mode (binary_counterphase vs on_off_flicker; interaction with phase opposition, actual surround suppression, and SSVEP IM)
    orientations (tuning and difference-of-gaussians model)
    trial design (must also be compatible with fear conditioning outcome measures)
    contrasts (fixed or will we also use a psychophysical task)

## flicker frequencies:
    (of center and surround)
    must be integer divisors of refresh_rate_hz
    must be distinct enough to separate fundamentals and IM components.
    (nf1 ± mf2) must also fall within distinct, analyzable bins given epoch length

## other: 
    epoch length for resolution; bin alignment: cycles =  f * T should be an integer i.e. integer number of cycles in one epoch. 
    trial number, order, duration, iti, task and instructions (see (D.R. Bach et al. 2023))

## outcome
* validated stimulus set with high ssvep snr
* reliable extraction of linear (fundamental) and nonlinear (im) signals
* validated temporal design compatible with other outcome measures
* predefined analysis targets for the fear conditioning phase
* finalized subset of stimulus conditions to carry forward into conditioning
