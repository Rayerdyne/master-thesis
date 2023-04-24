"""
Temporary file to contain my new version of the adjust utility function in
Dispa-SET preprocessing.

Function that are copied then updated.
"""

import logging
import shutil
import os, sys

import numpy as np
import pandas as pd

from ..misc.gdx_handler import write_variables

def adjust_unit_capacity(SimData, u_idx, scaling=1, value=None, singleunit=False):
    """
    Function used to modify the installed capacities in the Dispa-SET generated input data
    The function update the Inputs.p file in the simulation directory at each call

    :param SimData:            Input data dictionary
    :param u_idx:              names of the units to be scaled
    :param scaling:            Scaling factor to be applied to the installed capacity
    :param value:              Absolute value of the desired capacity (! Applied only if scaling != 1 !)
    :param singleunit:         Set to true if the technology should remain lumped in a single unit
    :return:                   New SimData dictionary
    """
    # a few checks:
    if len(u_idx) ==0:
        logging.warning('adjust_unit_capacity : list of units to be scaled is empty')
        return SimData
    if scaling > 1E10:
        logging.warning('adjust_unit_capacity: scaling factor is too high (' + str(scaling) + ')')
        return SimData
        
    # find the units to be scaled:
    units = SimData['units'].loc[u_idx,:]
    cond = SimData['units'].index.isin(u_idx)
    idx = pd.Series(np.where(cond)[0], index=units.index)
    TotalCapacity = (units.PowerCapacity * units.Nunits).sum()
    if scaling != 1:
        RequiredCapacity = TotalCapacity * scaling
    elif value is not None:
        RequiredCapacity = value
    else:
        RequiredCapacity = TotalCapacity
    if singleunit:
        Nunits_new = pd.Series(1, index=units.index)
    else:
        Nunits_new = (units.Nunits * RequiredCapacity / TotalCapacity).astype('float').round()
    Nunits_new[Nunits_new < 1] = 1
    Cap_new = units.PowerCapacity * RequiredCapacity / (units.PowerCapacity * Nunits_new).sum()
    for u in units.index:
        logging.info('Unit ' + u + ':')
        logging.info('    PowerCapacity: ' + str(SimData['units'].PowerCapacity[u]) + ' --> ' + str(Cap_new[u]))
        logging.info('    Nunits: ' + str(SimData['units'].Nunits[u]) + ' --> ' + str(Nunits_new[u]))
        factor = Cap_new[u] / SimData['units'].PowerCapacity[u]
        SimData['parameters']['PowerCapacity']['val'][idx[u]] = Cap_new[u]
        SimData['parameters']['Nunits']['val'][idx[u]] = Nunits_new[u]
        SimData['units'].loc[u, 'PowerCapacity'] = Cap_new[u]
        SimData['units'].loc[u, 'Nunits'] = Nunits_new[u]
        for col in ['CostStartUp', 'NoLoadCost', 'StorageCapacity', 'StorageChargingCapacity']:
            SimData['units'].loc[u, col] = SimData['units'].loc[u, col] * factor
        for param in ['CostShutDown', 'CostStartUp', 'PowerInitial', 'RampDownMaximum', 'RampShutDownMaximum',
                      'RampStartUpMaximum', 'RampUpMaximum', 'StorageCapacity']:
            SimData['parameters'][param]['val'][idx[u]] = SimData['parameters'][param]['val'][idx[u]] * factor

        for param in ['StorageChargingCapacity', 'StorageInitial']:
            # find index, if any:
            idx_s = np.where(np.array(SimData['sets']['s']) == u)[0]
            if len(idx_s) == 1:
                idx_s = idx_s[0]
                SimData['parameters'][param]['val'][idx_s] = SimData['parameters'][param]['val'][idx_s] * factor
    return SimData


def adjust_capacity(inputs, tech_fuel, scaling=1, value=None, singleunit=False, sto_fp_time_range=None, write_gdx=False, dest_path=''):
    """
    Function used to modify the installed capacities in the Dispa-SET generated input data
    The function update the Inputs.p file in the simulation directory at each call

    :param inputs:            Input data dictionary OR path to the simulation directory containing Inputs.p
    :param tech_fuel:         tuple with the technology and fuel type for which the capacity should be modified
    :param scaling:           Scaling factor to be applied to the installed capacity
    :param value:             Absolute value of the desired capacity (! Applied only if scaling != 1 !)
    :param singleunit:        Set to true if the technology should remain lumped in a single unit
    :param sto_fp_time_range: Ignored for non storage units. Specifies the range of full power time contained in the storage
                              the units have to fit in. If none, infinite range is considered
    :param write_gdx:         boolean defining if Inputs.gdx should be also overwritten with the new data
    :param dest_path:         Simulation environment path to write the new input data. If unspecified, no data is written!
    :return:                  New SimData dictionary
    """
    import pickle

    if isinstance(inputs, str):
        path = inputs
        inputfile = path + '/Inputs.p'
        if not os.path.exists(path):
            sys.exit('Path + "' + path + '" not found')
        with open(inputfile, 'rb') as f:
            SimData = pickle.load(f)
    elif isinstance(inputs, dict):
        SimData = inputs
        path = SimData['config']['SimulationDirectory']
    else:
        logging.error('The input data must be either a dictionary or string containing a valid directory')
        sys.exit(1)

    if not isinstance(tech_fuel, tuple):
        sys.exit('tech_fuel must be a tuple')
    

    # find the units to be scaled:
    cond = (SimData['units']['Technology'] == tech_fuel[0]) & (SimData['units']['Fuel'] == tech_fuel[1])

    # add condition to filter storage units outside the range of full power time
    if tech_fuel[0] in ["BATS", "BEVS", "CAES", "P2GS", "THMS"]:
        if sto_fp_time_range is None:
            sto_fp_time_range = (-np.infty, np.infty)
        elif not isinstance(sto_fp_time_range, tuple):
            logging.error("The range of full power time is invalid (not a tuple)")
            sys.exit(1)

        fp_time = 3600 * SimData["units"]["PowerCapacity"] / SimData["units"]["STOCapacity"]
        cond &= (sto_fp_time_range[0] <= fp_time) & (fp_time < sto_fp_time_range[1])

    u_idx = SimData['units'][cond].index.tolist()

    SimData = adjust_unit_capacity(SimData, u_idx, scaling=scaling, value=value, singleunit=singleunit)
    if dest_path == '':
        logging.info('Not writing any input data to the disk')
    else:
        if not os.path.isdir(dest_path):
            shutil.copytree(path, dest_path)
            logging.info('Created simulation environment directory ' + dest_path)
        logging.info('Writing input files to ' + dest_path)
        with open(os.path.join(dest_path, 'Inputs.p'), 'wb') as pfile:
            pickle.dump(SimData, pfile, protocol=pickle.HIGHEST_PROTOCOL)
        if write_gdx:
            write_variables(SimData['config'], 'Inputs.gdx', [SimData['sets'], SimData['parameters']])
            shutil.copy('Inputs.gdx', dest_path + '/')
            os.remove('Inputs.gdx')
    return SimData

def ranges_from_tresholds(thresholds, only_thresholds=False):
    """
    Outputs a list of ranges as a list of tuples.

    :param tresholds:        A list of tresholds to separate ranges at
    :param only_thresholds:  If false, add a bottom 0 threshold and ceil +np.infty bound, else restrict to given values
    """
    all = []
    if not only_thresholds:
        if thresholds[0] != 0:
            all.append(0)
        
        all += thresholds

        if all[-1] != np.inf:
            all.append(np.inf)
    else:
        all = thresholds
    
    res = []
    for i in range(len(all)-1):
        res.append((all[i], all[i+1]))

    # for x, y in zip(all[:-1], all[1:]):
    #     res.append((x, y))
    
    return res