controls:
  - name: para
    type: generic_control
    min: 0
    control_type: integer
    perturbation_magnitude: 0.01 # Not used for scipy/differential_evolution, but requiered by everest
    variables:
${variables_block}

objective_functions:
  - name: func

optimization:
  algorithm: scipy/differential_evolution
  max_function_evaluations: ${max_function_evaluations}
  min_realizations_success: ${min_realizations_success}${max_batch_block}
  options:
${options_block}
  parallel: True

install_jobs:
${install_jobs_block}

model:
  realizations: [0]

simulator:
  queue_system:
    max_running: ${cores}
    name: local

forward_model:
${forward_block}

environment:
  simulation_folder: sim_output
${rng_block}
