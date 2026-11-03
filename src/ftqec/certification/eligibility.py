"""Explicit eligibility of the existing finite graph-projection portfolio."""
from ..results.artifacts import digest,source_identity
from .structural import projections
from .inventory import backward,forward


def assess(c):
    inv=backward(c)
    try:
        channels=[]
        for bit,choices in projections(c).items():
            rows=[]
            for masks in choices:
                obstruction=None
                for op,label,d,l,_ in inv.rows():
                    support=[i for i,m in enumerate(masks) if (d&m).bit_count()%2]
                    if len(support)>2:
                        obstruction=dict(operation=op,label=label,detectors=d,logical=l,projected_support=support);break
                rows.append(dict(masks=masks,eligible=obstruction is None,obstruction=obstruction))
            channels.append(dict(bit=bit,eligible=any(r['eligible'] for r in rows),choices=rows))
        return dict(circuit=digest(c.to_dict()),source=source_identity(),inventory_hash=inv.hash,inventory_count=inv.count,
                    channels=channels,eligible=bool(channels) and all(r['eligible'] for r in channels),
                    scope='Existing logical-channel projection portfolio only; not impossibility of every conceivable graph representation')
    finally:inv.close()


def verify(c,receipt):
    if receipt.get('circuit')!=digest(c.to_dict()) or receipt.get('source')!=source_identity():return dict(verified=False,reason='identity')
    inv=forward(c)
    try:
        if receipt.get('inventory_hash')!=inv.hash or receipt.get('inventory_count')!=inv.count:return dict(verified=False,reason='inventory')
        choices=projections(c);channels=receipt.get('channels',[])
        if [r['bit'] for r in channels]!=list(choices):return dict(verified=False,reason='logical coverage')
        for channel in channels:
            if [r['masks'] for r in channel['choices']]!=choices[channel['bit']]:return dict(verified=False,reason='projection coverage')
            eligible=[]
            for row in channel['choices']:
                found=None
                for op,label,d,l,_ in inv.rows():
                    support=[]
                    for i,mask in enumerate(row['masks']):
                        parity=0
                        while mask:
                            b=mask&-mask;parity^=bool(d&b);mask^=b
                        if parity:support.append(i)
                    if len(support)>2:
                        found=dict(operation=op,label=label,detectors=d,logical=l,projected_support=support);break
                if row['obstruction']!=found or row['eligible']!=(found is None):return dict(verified=False,reason='projection obstruction')
                eligible.append(found is None)
            if channel['eligible']!=any(eligible):return dict(verified=False,reason='channel eligibility')
        actual=bool(channels) and all(r['eligible'] for r in channels)
        return dict(verified=receipt.get('eligible')==actual,eligible=actual,method='forward physical effects and explicit projected-support obstructions')
    finally:inv.close()
