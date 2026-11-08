import json
import pytest
import stim
from ftqec.results.artifacts import digest,save_checkpoint


def test_checkpoint_atomic_digest_and_failed_serialization(tmp_path,monkeypatch):
    path=tmp_path/'state.json';s={'nested':[{'unicode':'λ','x':False}], 'value':3}
    save_checkpoint(path,s);assert json.loads(path.read_text())==s
    assert s['checkpoint_digest']==digest({k:v for k,v in s.items() if k!='checkpoint_digest'})
    old=path.read_bytes();s['bad']=float('nan')
    with pytest.raises(ValueError):save_checkpoint(path,s)
    assert path.read_bytes()==old
    s.pop('bad');s['value']=4
    import ftqec.results.artifacts as module
    replace=module.os.replace;attempts=[]
    def transient(a,b):
        attempts.append(1)
        if len(attempts)==1:raise PermissionError('transient file reader')
        return replace(a,b)
    monkeypatch.setattr(module.os,'replace',transient);save_checkpoint(path,s)
    assert len(attempts)==2 and json.loads(path.read_text())==s


def test_bposd_complete_correlated_mechanisms_and_ordering():
    pytest.importorskip('ldpc')
    import numpy as np
    from ftqec.simulation.bposd import Decoder,matrices
    dem=stim.DetectorErrorModel('error(0.01) D0 D1 ^ D2 L1\nerror(0.02) D3 L0')
    h,l,p=matrices(dem)
    assert h.shape==(4,2) and np.array_equal(h.toarray(),[[1,0],[1,0],[1,0],[0,1]])
    assert np.array_equal(l.toarray(),[[0,1],[1,0]])
    d=Decoder(dem);samples=np.array([[0,0,0,0],[1,1,1,0],[0,0,0,1],[1,1,1,1]],dtype=np.uint8)
    predicted,bad=d.decode(samples)
    assert bad==0 and np.array_equal(predicted,[[0,0],[0,1],[1,0],[1,1]])
    assert np.array_equal(d.decode(samples)[0],predicted)
    with pytest.raises(ValueError):d.decode([[1,0]])
    with pytest.raises(MemoryError):matrices(dem,1)


def test_bposd_physical_boundaries_and_seed_replay():
    pytest.importorskip('ldpc')
    from ftqec.architectures.references import rotated_surface
    from ftqec.circuits.repeated import memory
    from ftqec.simulation.monte_carlo import evaluate
    _,single=rotated_surface(3,1)
    for basis in ('X','Z'):
        c=memory(single,3,basis)
        a=evaluate(c,.003,128,8,decoder='bposd');b=evaluate(c,.003,128,8,decoder='bposd')
        assert a['sample_hash']==b['sample_hash'] and a['failures']==b['failures']
        assert a['decoder_inconsistent_syndromes']==0
        assert evaluate(c,0,16,8,decoder='bposd')['failures']==0


def test_memory_proposals_budget_diversity_and_paired_promotion():
    from ftqec.codes.two_block import parse
    from ftqec.optimization.memory_proposals import propose,promote
    from pathlib import Path
    code=parse(json.loads(Path('examples/two_block_small.json').read_text()))
    a=propose(code,[],4,0,15,4,'hybrid');b=propose(code,[],4,0,15,4,'hybrid')
    assert a==b and all(x['parent'] is None for x in a)
    assert len({x['genome']['family'] for x in a})==5
    groups={str(i):[dict(id=str(i)+sector,genome=x['genome'],resources=dict(Q=10+i,D=30-i,QD=(10+i)*(30-i))) for sector in ('X','Z')] for i,x in enumerate(a)}
    chosen=promote(groups,7,'hybrid',4)
    assert len(chosen)==7 and all(len(x)==2 for x in chosen)
