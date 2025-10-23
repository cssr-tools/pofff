NUM_REALIZATIONS ${dic["ensembles"]}
MIN_REALIZATIONS ${dic["min_realizations_success"]}

QUEUE_SYSTEM LOCAL
QUEUE_OPTION LOCAL MAX_RUNNING ${dic["cores"]}

% if dic["random_seed"] > 0:
RANDOM_SEED ${dic["random_seed"]}
% endif

RUNPATH output/simulations/realisation-<IENS>/iter-<ITER>
ENSPATH output/storage

ECLBASE ${dic["data"]}
RUN_TEMPLATE deck/${dic["data"]}.DATA <ECLBASE>.DATA

GEN_KW PARA ./deck/prior.tmpl para.json ./deck/para.txt

OBS_CONFIG ./jobs/OBS
TIME_MAP ./jobs/TIME

% for name in ["copyd", "equalreg", "satufunc", "bcprop", "flow"]:
INSTALL_JOB ${name} ./jobs/${name.upper()}
SIMULATION_JOB ${name}
% endfor
INSTALL_JOB data ./jobs/DATA
SIMULATION_JOB data -t ${dic["times"]} -m ${dic['deck']}/cellmap.npy
INSTALL_JOB metric ./jobs/METRIC
SIMULATION_JOB metric -t ${dic["times"]} -e ${dic["experiment"]} -s ${dic["msat"]} -c ${dic["mcon"]} -p ${dic["path"]}
% if dic["delete"]:
INSTALL_JOB delete ./jobs/DELETE
SIMULATION_JOB delete
% endif

GEN_DATA SIMULATION_METRICS RESULT_FILE:sim_metrics_%d.txt REPORT_STEPS:0 INPUT_FORMAT:ASCII
