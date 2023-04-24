# Not usable in practice, because the amount of data of all the prepared simulation
# is too large (>110GB limit allowed)

$(info Using configuration from config.py)

SIMULATIONS_DIR=$(shell python -c "from config import SIMULATIONS_DIR; print(SIMULATIONS_DIR)")
SIMULATION_SAMPLES=$(shell python -c "from config import N_SAMPLES; print(N_SAMPLES)")
REFERENCE_INFO_FILE=$(shell python -c "from config import REFERENCE_INFO_FILE; print(REFERENCE_INFO_FILE)")
DATASET_NAME=$(shell python -c "from config import DATASET_NAME; print(DATASET_NAME)")


$(info Assuming Python3.9.6 is loaded)
$(info Assuming Dispa-SET env is activated)

SENTINEL:=sentinel.txt

reference: reference.py config.py
	$(info +--------------------+)
	$(info | Building reference |)
	$(info +--------------------+)
	python reference.py

$(SIMULATIONS_DIR)/$(REFERENCE_INFO_FILE): reference

inputs: sampling.py config.py $(SIMULATIONS_DIR)/$(REFERENCE_INFO_FILE)
	$(info +----------------------+)
	$(info | Creating input files |)
	$(info +----------------------+)
	python sampling.py
	echo -e "Hi I'm the sentinel\n" > $(SIMULATIONS_DIR)/$(SENTINEL)

$(SIMULATIONS_DIR)/$(SENTINEL): inputs

simulations: $(SIMULATIONS_DIR)/$(SENTINEL)
	$(info +---------------------+)
	$(info | Running simulations |)
	$(info +---------------------+)
	@echo "CapacityRatio,ShareFlex,ShareStorage,ShareWind,SharePV,rNTC,Cost_[E/MWh],Congestion_[h],PeakLoad_[MW],MaxCurtailment_[MW],MaxLoadShedding_[MW],Demand_[TWh],NetImports_[TWh],Curtailment_[TWh],Shedding_[TWh],LostLoad_[TWh],CF_gas,CF_nuc,CF_wat,CF_win,CF_sun" > $(SIMULATIONS_DIR)/$(DATASET_NAME)
	sbatch launch-simulation-jobs.sh $(SIMULATIONS_DIR)

test:
	sbatch --version
