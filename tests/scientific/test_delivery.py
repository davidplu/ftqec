import json
from copy import deepcopy
from pathlib import Path
import pytest
from ftqec.codes.input import load
from ftqec.architectures.population import Genome,compile
from ftqec.screening.structural import check
from ftqec.certification.exact import certify
from ftqec.results.artifacts import digest,source_identity,save
from ftqec.delivery.export import export_result,schedule_payload,stim_text
from ftqec.delivery.verify import reconstruct,verify_bundle,verify_stim


def example(tmp_path, noncss=False):
    inp=load(dict(generators=['XYZ'] if noncss else ['ZZ']))
    g=Genome('bare',(tuple(range(inp.code.n)),),(0,),shared=False)
    c=compile(inp,g);check(c)
    cert=certify(c,1)
    row=dict(id=digest(c.to_dict()),circuit=c.to_dict(),certify=cert,genome=g.to_dict())
    save(tmp_path/'checkpoint.json',dict(code=inp.to_dict(),source=source_identity(),config=dict(p=.01,seed=4,decoder='one_mechanism_lookup'),rows=[row],tasks={}))
    return c,row


def test_complete_export_reconstruction_proof_and_stim(tmp_path):
    c,row=example(tmp_path)
    for format in ('bundle','schedule-json','circuit-json','stim'):
        out=tmp_path/format
        export_result(tmp_path,row['id'],out,format)
        if format=='bundle':
            result=verify_bundle(out)
            assert result['positive_certificate_verified'] and result['certificate_binding_verified']
        if format=='schedule-json':assert verify_bundle(out)['reconstruction_verified']
        if format=='circuit-json':assert json.loads(out.read_text())==c.to_dict()
        if format=='stim':assert verify_stim(c,out.read_text(),.01)
    with pytest.raises(FileExistsError):export_result(tmp_path,row['id'],tmp_path/'bundle')


@pytest.mark.parametrize('kind',['gate','start','dependency','records','reset','logical','detector','resource','certificate','source','stim','missing'])
def test_bundle_tamper_rejected_even_with_refreshed_member_hash(tmp_path,kind):
    import hashlib
    c,row=example(tmp_path);root=tmp_path/'bundle';export_result(tmp_path,row['id'],root)
    file='schedule.json';data=json.loads((root/file).read_text())
    if kind=='gate':data['operations'][0]['operation']['gate']='X'
    elif kind=='start':data['operations'][1]['start']=0
    elif kind=='dependency':data['operations'][1]['dependencies']=[]
    elif kind=='records':data['measurements']={}
    elif kind=='reset':data['ancilla_lifetimes'][0]['reset']=1
    elif kind=='logical':data['metadata']['observables']=[['absent']]
    elif kind=='detector':data['metadata']['detectors']=[]
    elif kind=='resource':file='resources.json';data=json.loads((root/file).read_text());data['D']+=1
    elif kind=='certificate':file='certificate.json';data=json.loads((root/file).read_text());data['circuit']='bad'
    elif kind=='source':file='evidence.json';data=json.loads((root/file).read_text());data['exporter_source']='bad'
    elif kind=='stim':file='circuit.stim';(root/file).write_text('R 0\n')
    elif kind=='missing':(root/'tasks.json').unlink()
    if kind not in ('stim','missing'):
        if file=='schedule.json':data['schedule_identity']=digest({k:v for k,v in data.items() if k!='schedule_identity'})
        save(root/file,data)
    manifest=json.loads((root/'manifest.json').read_text())
    if (root/file).exists():manifest['members'][file]=hashlib.sha256((root/file).read_bytes()).hexdigest()
    save(root/'manifest.json',manifest)
    with pytest.raises((ValueError,KeyError)):verify_bundle(root)


def test_noncss_observables_and_unrecorded_measurements(tmp_path):
    c,row=example(tmp_path,True)
    c.add('M',[c.syndrome_qubits[0]])
    c.observables=[c.detectors[0]]
    p=schedule_payload(c);rebuilt,metrics=reconstruct(p)
    assert rebuilt.to_dict()==c.to_dict()
    assert verify_stim(c,stim_text(c,0),0)


def test_source_mismatch_never_promoted_to_positive(tmp_path):
    c,row=example(tmp_path)
    state=json.loads((tmp_path/'checkpoint.json').read_text());state['source']='old';state['rows'][0]['certify']['source']='old';save(tmp_path/'checkpoint.json',state)
    export_result(tmp_path,row['id'],tmp_path/'bundle')
    result=verify_bundle(tmp_path/'bundle')
    assert result['reconstruction_verified'] and not result['positive_certificate_verified']
    assert 'SOURCE_MISMATCH' in result['proof_replay']['reason']


def test_selected_layer_timeline_and_bounded_verifier_task(tmp_path):
    from ftqec.delivery.timeline import render
    from ftqec.execution.tasks import Task,execute
    import xml.etree.ElementTree as ET
    c,row=example(tmp_path);path=tmp_path/'schedule.json';save(path,schedule_payload(c))
    out=tmp_path/'timeline.svg';result=render(path,out,0,3,2)
    assert result['stop']==3 and len(result['shown_qubits'])<=2
    ET.fromstring(out.read_text())
    task=Task(dict(circuit=c.to_dict(),certificate=row['certify']),'verify',c.code.input_hash,{'p':0},'auto',0,source_identity(),{'work':200000})
    assert execute(task)['result']['verified']


def test_public_result_listing(tmp_path):
    from ftqec.delivery.export import list_results
    c,row=example(tmp_path)
    state=json.loads((tmp_path/'checkpoint.json').read_text())
    from ftqec.evaluation.resources import resources
    state['rows'][0]['resources']=resources(c);save(tmp_path/'checkpoint.json',state)
    listed=list_results(tmp_path)
    assert listed['results'][0]['circuit_id']==row['id']


def test_real_optimizer_physical_id_is_distinct_from_exact_certificate_id(tmp_path):
    from ftqec.circuits.identity import physical_identity
    from ftqec.delivery.export import list_results
    c,row=example(tmp_path)
    row['id']=physical_identity(c)
    from ftqec.evaluation.resources import resources
    row['resources']=resources(c)
    assert row['id']!=digest(c.to_dict())
    state=json.loads((tmp_path/'checkpoint.json').read_text());state['rows']=[row]
    save(tmp_path/'checkpoint.json',state)
    listed=list_results(tmp_path,True)['results'][0]
    assert listed['circuit_id']==row['id'] and listed['exact_circuit_identity']==digest(c.to_dict())
    export_result(tmp_path,row['id'],tmp_path/'bundle')
    v=verify_bundle(tmp_path/'bundle');assert v['positive_certificate_verified']
    manifest=json.loads((tmp_path/'bundle/manifest.json').read_text())
    assert manifest['circuit']==digest(c.to_dict()) and manifest['candidate_id']==row['id']
