"""Materialize self-contained export indexes from shared-pool experiment records.

Policy databases deliberately do not duplicate the shared construction input.
This separate evidence catalog joins provenance without modifying raw runs or
charging copied task receipts as newly executed computation.
"""
import argparse,json
from pathlib import Path
from ftqec.codes.two_block import parse
from ftqec.optimization.store import PopulationStore
from ftqec.execution.tasks import Task
from ftqec.results.artifacts import save,digest,source_identity


def prepare(epoch,output):
    epoch=Path(epoch);output=Path(output)
    protocols=list(epoch.glob('protocol-A-v*.json'))
    if len(protocols)!=1:raise ValueError('One fixed-pool protocol required')
    spec=json.loads(protocols[0].read_text())
    if spec['source']!=source_identity():raise ValueError('Use the matching frozen package for delivery')
    if output.exists():raise FileExistsError('Delivery snapshots are immutable; choose a fresh output directory')
    output.mkdir(parents=True);origins={};copied=[]
    for path in sorted((epoch/'fixed-pool').glob('seed-*/*/comparison.json')):
        report=json.loads(path.read_text())
        if report['protocol']!=spec['identity']:raise ValueError('Mixed experimental source')
        for pair in report['state']['positive']:
            for cid in pair['sectors']:origins.setdefault(cid,[]).append(dict(run=str(path.parent.resolve()),pair=pair['id'],policy=report['policy'],seed=report['seed']))
    with PopulationStore(output/'population.sqlite',digest(dict(protocol=spec['identity'],origins=origins))) as dest:
        dest.set_meta('state',dict(source=spec['source'],code=parse(spec['code']).input.to_dict(),
            config=dict(spec['settings'],decoder='bposd',p=spec['settings']['noise']),
            status='EVIDENCE_CATALOG',protocol=spec['identity'],qualification='Task costs below are copied source receipts, not additional executions'))
        for cid,places in origins.items():
            run=Path(places[0]['run']);pool_path=run.parent/'pool'
            pool=json.loads((pool_path/'pool-accounted.json').read_text())
            with PopulationStore(run/'population.sqlite',readonly=True) as source:
                row=source.get(cid)
                if row['independent_verification']['status']!='CERTIFIED' or row['certify'].get('exact_distance')!=spec['settings']['target']:
                    raise ValueError('Unverified or inexact finalist')
                row['shared_pool_provenance']=dict(protocol=spec['identity'],pool=pool['hash'],genome=digest(row['genome']),origins=places)
                dest.put(row)
                for packet in source.packets(cid):
                    task=Task(**packet['task']);dest.queue(task,cid);dest.complete(task.identity,packet['answer'])
            with PopulationStore(pool_path/'population.sqlite',readonly=True) as source:
                for packet in source.packets(digest(row['genome'])):
                    task=Task(**packet['task']);dest.queue(task,digest(row['genome']));dest.complete(task.identity,packet['answer'])
            copied.append(dict(circuit=cid,pair=places[0]['pair'],basis=row['circuit']['experiment']['memory_basis'],resources=row['resources'],origins=places))
    save(output/'checkpoint.json',dict(schema='sqlite-population-1',population_db='population.sqlite',source=spec['source'],status='EVIDENCE_CATALOG'))
    save(output/'catalog.json',dict(protocol=spec['identity'],source=spec['source'],circuits=copied,
         qualification='Independent export verification is a subsequent measured audit, outside policy budgets'))
    return copied


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('epoch');p.add_argument('--output',required=True);a=p.parse_args()
    records=prepare(a.epoch,a.output);print(json.dumps(dict(circuits=len(records),output=a.output)))


if __name__=='__main__':main()
