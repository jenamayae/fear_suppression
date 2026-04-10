"""
structure:
  - load_cnt(path)
  - extract_events(raw)
  - make_epochs(stimulus_onset, stimulus_offset) 2s or 80 frames or 1 combined stimulus pattern cycle after stimulus_onset
  - compute_fft(frequency_resolution = 1/epoch) ie 0.167 Hz
  - plot_spectrum(amplitude, frequency)

  -pick oz for channel 


  -plot rms power at tagged frequency for topography: one for center one for surround. 


? baseline
? saving

basic validation checks:
  - verify requested event codes are present
  - verify epoch windows fit within the recording
  - verify tagged frequencies are resolvable given epoch length
  - warn if epoch length does not contain integer cycles of target frequencies
  
  """