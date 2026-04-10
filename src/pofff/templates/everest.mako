controls:
  - name: para
    type: generic_control
    min: 0
    control_type: integer
    perturbation_magnitude: 0.01 # Not used for scipy/differential_evolution, but requiered by everest
    variables:
% for para in dic["hm"]:
<% ini_val, min_val, max_val, no_vals = dic["hm"][para][0], dic["hm"][para][1], dic["hm"][para][2], dic["hm"][para][3] %>\
      - name: ${para}
        max: ${no_vals}
        initial_guess: ${round((ini_val-min_val)/((max_val-min_val)/(1.0*no_vals)))}
% endfor

objective_functions:
  - name: func

optimization:
  algorithm: scipy/differential_evolution
  max_function_evaluations: ${dic["max_function_evaluations"]}
  min_realizations_success: ${dic["min_realizations_success"]}
% if dic["max_batch_num"]:
  max_batch_num: ${dic["max_batch_num"]}
% endif
  options:
% for name in ["strategy", "maxiter", "popsize", "tol", "mutation", "recombination", "rng", "callback", "disp", "polish", "init", "atol", "updating", "workers", "constraints", "x0", "integrality", "vectorized"]:
% if dic[name]:     
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
% if dic["rng"]:
  random_seed: ${dic["rng"]}
% endif