controls:
  - name: para
    type: generic_control
    min: 0
    control_type: integer
    perturbation_magnitude: 0.01 # Not used for scipy/differential_evolution, but requiered by everest
    variables:
% for para in dic["hm"]:
      - name: ${para}
        max: ${dic[para][3]}
        initial_guess: ${round((dic[f"{para}"][0]-dic[f"{para}"][1])/((dic[f"{para}"][2]-dic[f"{para}"][1])/(1.0*dic[f"{para}"][3])))}
% endfor

objective_functions:
  - name: func

optimization:
  algorithm: scipy/differential_evolution
  max_function_evaluations: ${dic["max_function_evaluations"]}
  min_realizations_success: ${dic["min_realizations_success"]}
% if max_batch_num in dic:
  max_batch_num: ${dic["max_batch_num"]}
% endif
  options:
% for name in ["strategy", "maxiter", "popsize", "tol", "mutation", "recombination", "rng", "callback", "disp", "polish", "init", "atol", "updating", "workers", "constraints", "x0", "integratility", "vectorized"]:
% if name in dic:     
    ${name}: ${dic[name]}
% endif
% endfor
  parallel: True

install_jobs:
% if dic["monotonic"]:
  - name: scale
    executable: jobs/scale.py
  - name: monotonic
    executable: jobs/monotonic.py
% endif
% for name in ["copyd", "equalreg", "satufunc", "bcprop", "flow", "data", "metric", "delete"]:
  - name: ${name}
    executable: jobs/${name}.py
% endfor

model:
  realizations: [0]

simulator:
  queue_system:
    max_running: ${dic["cores"]}
    name: local

forward_model:
% if dic["monotonic"]:
  - scale
  - monotonic
% endif
  - copyd
  - equalreg
  - satufunc
  - bcprop
  - flow
  - data        -t ${dic["times"]}
                -m ${dic['deck']}/cellmap.npy
  - metric      -t ${dic["times"]}
                -e ${dic["experiment"]}
                -p ${dic["path"]}
                -s ${dic["msat"]}
                -c ${dic["mcon"]}
% if dic["delete"]:
  - delete
% endif

environment:
  simulation_folder: sim_output
% if dic["random_seed"] != 0:
  random_seed: ${dic["random_seed"]}
% endif