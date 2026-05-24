NUM_REALIZATIONS ${ensembles}
MIN_REALIZATIONS ${min_realizations_success}

QUEUE_SYSTEM LOCAL
QUEUE_OPTION LOCAL MAX_RUNNING ${cores}

${random_seed_block}

ENKF_ALPHA ${enkf_alpha}

RUNPATH output/simulations/realisation-<IENS>/iter-<ITER>
ENSPATH output/storage

GEN_KW PARA ./deck/prior.tmpl para.json ./deck/para.txt

OBS_CONFIG ./jobs/OBS

${jobs_block}
INSTALL_JOB data ./jobs/DATA
FORWARD_MODEL data
INSTALL_JOB metric ./jobs/METRIC
FORWARD_MODEL metric
${delete_block}

GEN_DATA SIMULATION_METRICS RESULT_FILE:sim_metrics_%d.txt REPORT_STEPS:0
