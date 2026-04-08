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
* beginning fixation: 3.0 s (remove this)
* trial duration: 10.0 s
* inter trial interval: 3 s
* trials per condition: 10

Outputs:
* rms amplitude at input frequency as a function of condition comparing: 
* upper/lower counterphase vs none 
* orthogonal vs colinear
* phase reversal vs on/off 
    
to do:
double sf
implement 45-static condition
change outputs^

consider:
also do the double on/off rate
sin reversal rate at double that or half of that. 
center only stim no surround

consider:
for no surround condition: temporal frequency, contrasts.
pick one temporal frequency for contrast
how does upper/lower affect contrasts. 
once we find maximal effect decide if center or surround is higher. 
