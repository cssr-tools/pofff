controls:
  - name: para
    type: generic_control
    min: 0
    control_type: integer
    variables:
% for para in dic["hm"]:
      - name: ${para}
        max: ${dic[para][3]}
        initial_guess: ${round((dic[f"{para}"][0]-dic[f"{para}"][1])/((dic[f"{para}"][2]-dic[f"{para}"][1])/(1.0*dic[f"{para}"][3])))}
% endfor

objective_functions:
  - name: func

optimization:
  backend: scipy
  algorithm: differential_evolution
  max_function_evaluations: ${dic["max_function_evaluations"]}
  min_realizations_success: ${dic["min_realizations_success"]}
% if dic["random_seed"] != 0:
  backend_options:
    seed: ${dic["random_seed"]}
    popsize: ${dic["popsize"]}
% endif
  parallel: True

install_jobs:
% if dic["monotonic"]:
  - name: scale
    source: jobs/SCALE
  - name: monotonic
    source: jobs/MONOTONIC
% endif
% for name in ["copyd", "equalreg", "satufunc", "bcprop", "flow", "data", "metric", "delete"]:
  - name: ${name}
    source: jobs/${name.upper()}
% endfor

model:
  realizations: [0]

simulator:
  cores: ${dic["cores"]}

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