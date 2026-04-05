from trials import generate_habituation_trials, generate_acquisition_trials

h = generate_habituation_trials()
a = generate_acquisition_trials()

print(len(h)) # should be 72 (4 center_oris x 3 surround_oris x 6 reps)
print(len(a)) # should be 60 

print(sum(t["reinforced"] for t in a if t["cs_type"] == "CS+"))