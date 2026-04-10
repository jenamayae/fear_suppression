# Preconditioning Calibration Stage

Questions:
1. Does upper/lower counterphase increase SSVEP response strength or SNR?
2. Do our stimuli produce reduced tagged responses in surround-present conditions consistent with surround suppression?
3. Is the effect of upper/lower counterphase different for phase-reversal versus on/off flicker? 

Conditions: 
* center orientations: [45]
* surround orientations: [None, 45-dynamic, 45-static]
* upper/lower phase mode: [synchronized, offset]
* modulation mode: [phase reversal, on/off flicker]
* 1 * 2 * 2 * 2 = 12 conditions

Trials:
* trial duration: 10.0 s
* inter trial interval: 3 s
* trials per condition: 10

Outputs:
* rms amplitude at input frequency as a function of condition comparing: 
* upper/lower counterphase vs none 
* orthogonal vs colinear
* phase reversal vs on/off 

---

TO DO:
- double the sf
- implement 45-static condition
- change outputs in readme^
- remove intial blank fixation
- double check stimuli location, visual angle, screen size, viewing distance
- look into mean luminance; cieling contrast
- analysis.py

consider also:
- doing double the on/off rate (center only, no surround)
- phase reversal rate at double that or half of that (center only, no surround)
- effect of upper/lower counterphase at different contrasts (one temporal frequ, center only)
- once we find maximal effect decide if center or surround is higher temporal frequ. 

