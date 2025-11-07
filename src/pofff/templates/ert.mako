NUM_REALIZATIONS ${dic["ensembles"]}
MIN_REALIZATIONS ${dic["min_realizations_success"]}

QUEUE_SYSTEM LOCAL
QUEUE_OPTION LOCAL MAX_RUNNING ${dic["cores"]}

% if dic["random_seed"] > 0:
RANDOM_SEED ${dic["random_seed"]}
% endif

ENKF_ALPHA ${dic["enkf_alpha"]}

RUNPATH output/simulations/realisation-<IENS>/iter-<ITER>
ENSPATH output/storage

GEN_KW PARA ./deck/prior.tmpl para.json ./deck/para.txt

OBS_CONFIG ./jobs/OBS

% for name in ["copyd", "equalreg", "satufunc", "bcprop", "flow"]:
INSTALL_JOB ${name} ./jobs/${name.upper()}
FORWARD_MODEL ${name}
% endfor
INSTALL_JOB data ./jobs/DATA
FORWARD_MODEL data 
INSTALL_JOB metric ./jobs/METRIC
FORWARD_MODEL metric 
% if dic["delete"]:
INSTALL_JOB delete ./jobs/DELETE
FORWARD_MODEL delete
% endif

GEN_DATA SIMULATION_METRICS RESULT_FILE:sim_metrics_%d.txt REPORT_STEPS:0
