import matlab.engine
import os
import itertools
import numpy as np
import pytest
import time

from py3gpp.nrPDSCHPTRSIndices import nrPDSCHPTRSIndices
from py3gpp.configs.nrPDSCHConfig import nrPDSCHConfig
from py3gpp.configs.nrCarrierConfig import nrCarrierConfig

def run_nr_pdschptrs_indices(cfg, eng):
    carrier = nrCarrierConfig();
    carrier.SubcarrierSpacing = 120;
    carrier.CyclicPrefix = 'normal';
    carrier.NSizeGrid = 132;
    carrier.NStartGrid = 0;

    pdsch_cfg = nrPDSCHConfig();
    pdsch_cfg.NSizeBWP = cfg['n_size_bwp']
    pdsch_cfg.NStartBWP = cfg['n_start_bwp']
    pdsch_cfg.MappingType = cfg['MappingType']
    pdsch_cfg.DMRS.DMRSTypeAPosition = cfg['DMRSTypeAPosition']
    pdsch_cfg.DMRS.DMRSLength = cfg['DMRSLength']
    pdsch_cfg.DMRS.DMRSAdditionalPosition = cfg['DMRSAdditionalPosition']
    pdsch_cfg.DMRS.DMRSConfigurationType = cfg['DMRSConfigurationType']
    pdsch_cfg.DMRS.NIDNSCID = cfg['NIDNSCID']
    pdsch_cfg.DMRS.NSCID = cfg['NSCID']
    pdsch_cfg.RNTI = cfg['RNTI']
    pdsch_cfg.PRBSet = cfg['PRBSet']
    pdsch_cfg.SymbolAllocation = cfg['SymbolAllocation']

    pdsch_cfg.EnablePTRS = cfg['EnablePTRS']
    pdsch_cfg.PTRS.TimeDensity = cfg['PTRSTimeDensity']
    pdsch_cfg.PTRS.FrequencyDensity = cfg['PTRSFrequencyDensity']
    pdsch_cfg.PTRS.REOffset = cfg['PTRSREOffset']

    pdschptrs_indices = nrPDSCHPTRSIndices(carrier, pdsch_cfg)

    [_,_,_, indices_ref] = eng.gen_pdschdmrs(cfg, nargout=4)
    indices_ref = np.array(list(itertools.chain(*indices_ref)))
    indices_ref = indices_ref - 1

    assert np.array_equal(pdschptrs_indices, indices_ref)


@pytest.fixture(scope='session')
def eng():
    eng = matlab.engine.connect_matlab()
    yield eng
    eng.quit()

@pytest.mark.parametrize('typeA_pos', [2, 3])
@pytest.mark.parametrize('symb_alloc', [[2, 12]])
@pytest.mark.parametrize('dmrs_add_pos', [0, 1, 2, 3])
@pytest.mark.parametrize('PRBSet', [list(range(0, 132)), list(range(60, 132)), list(range(30, 60))])
@pytest.mark.parametrize('dmrs_cfg_type', [1, 2])
@pytest.mark.parametrize('PTRSREOffset', ['00', '01', '10', '11'])
@pytest.mark.parametrize('PTRSFrequencyDensity', [2, 4])
@pytest.mark.parametrize('PTRSTimeDensity', [1, 2, 4])
def test_nr_pdschptrs_indices(typeA_pos, symb_alloc, dmrs_add_pos, PRBSet, dmrs_cfg_type, PTRSREOffset, PTRSFrequencyDensity, PTRSTimeDensity, eng):
    eng.cd(os.path.dirname(__file__))

    cfg = {}
    cfg['n_size_bwp'] = 132
    cfg['n_start_bwp'] = 0
    cfg['MappingType'] = "A"
    cfg['DMRSTypeAPosition'] = typeA_pos
    cfg['DMRSLength'] = 1
    cfg['DMRSAdditionalPosition'] = dmrs_add_pos
    cfg['PRBSet'] = PRBSet
    cfg['SymbolAllocation'] = symb_alloc
    cfg['DMRSConfigurationType'] = dmrs_cfg_type
    cfg['NIDNSCID'] = 1
    cfg['NSCID'] = 0
    cfg['RNTI'] = 1
    cfg['EnablePTRS'] = 1
    cfg['PTRSTimeDensity'] = PTRSTimeDensity
    cfg['PTRSFrequencyDensity'] = PTRSFrequencyDensity
    cfg['PTRSREOffset'] = PTRSREOffset

    run_nr_pdschptrs_indices(cfg, eng)

if __name__ == '__main__':
    _eng = matlab.engine.connect_matlab()
    test_nr_pdschptrs_indices(2, [2, 12], 3, list(range(0, 132)), 1, '00', 2, 4, _eng)
    _eng.quit()