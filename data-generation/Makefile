$(info Using configuration from config.py)

SIMULATIONS_FOLDER=$(shell python -c "from config import SIMULATIONS_FOLDER; print(SIMULATIONS_FOLDER)")
SIMULATIONS_SUBFOLDER=$(shell python -c "from config import SIMULATIONS_SUBFOLDER; print(SIMULATIONS_SUBFOLDER)")
SIMULATION_SAMPLES=$(shell python -c "from config import N_SAMPLES; print(N_SAMPLES)")
DATASET_NAME=$(shell python -c "from config import DATASET_NAME; print(DATASET_NAME)")


$(info Assuming Python3.9.6 is loaded)
$(info Assuming Dispa-SET env is activated)

SENTINEL:=sentinel.txt

inputs: sampling.py config.py
	$(info +----------------------+)
	$(info | Creating input files |)
	$(info +----------------------+)
	python sampling.py
	echo -e "Hi I'm the sentinel\n" > $(SIMULATIONS_SUBFOLDER)/$(SENTINEL)

$(SIMULATIONS_SUBFOLDER)/$(SENTINEL): inputs

simulations: $(SIMULATIONS_SUBFOLDER)/$(SENTINEL)
	$(info +---------------------+)
	$(info | Running simulations |)
	$(info +---------------------+)
	@echo "CapacityRatio,ShareFlex,ShareStorage,ShareWind,SharePV,rNTC,Cost_[E/MWh],Congestion_[h],PeakLoad_[MW],MaxCurtailment_[MW],MaxLoadShedding_[MW],Demand_[TWh],NetImports_[TWh],Curtailment_[TWh],Shedding_[TWh],LostLoad_[TWh],CF_gas,CF_nuc,CF_wat,CF_win,CF_sun" > $(SIMULATIONS_SUBFOLDER)/$(DATASET_NAME)
	sbatch launch-simulation-jobs.sh $(SIMULATIONS_SUBFOLDER)

test:
	sbatch --version
