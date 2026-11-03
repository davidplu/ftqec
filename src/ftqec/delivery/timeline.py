"""SVG timeline generated only from independently reconstructed schedule rows."""
import html,json
from pathlib import Path
from .verify import reconstruct


def render(schedule_path,output,start=0,stop=None,qubit_limit=32):
    payload=json.loads(Path(schedule_path).read_text(encoding='utf-8-sig'));c,metrics=reconstruct(payload)
    stop=metrics['D'] if stop is None else min(stop,metrics['D'])
    if type(start) is not int or start<0 or stop<=start or qubit_limit<1:raise ValueError('Invalid layer/qubit view')
    selected=[r for r in payload['operations'] if start<=r['start']<stop]
    qubits=sorted({q for r in selected for q in r['operation']['qubits']})[:qubit_limit]
    positions={q:60+25*i for i,q in enumerate(qubits)};width=max(800,100+65*(stop-start));height=110+25*len(qubits)
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">','<rect width="100%" height="100%" fill="white"/>',f'<text x="12" y="20" font-family="sans-serif" font-size="14">FTQEC schedule {payload["circuit"][:16]} | layers {start}:{stop}</text>']
    for t in range(start,stop):parts.append(f'<text x="{95+65*(t-start)}" y="42" font-family="sans-serif" font-size="11">{t}</text>')
    for q,y in positions.items():parts.extend([f'<text x="8" y="{y+4}" font-family="sans-serif" font-size="11">q{q}</text>',f'<line x1="55" y1="{y}" x2="{width-15}" y2="{y}" stroke="#b6c5ce"/>'])
    for row in selected:
        op=row['operation'];visible=[q for q in op['qubits'] if q in positions]
        if not visible:continue
        x=100+65*(row['start']-start);ys=[positions[q] for q in visible]
        label=html.escape(op['gate']);title=html.escape('operation '+str(row['id'])+' '+op['gate']+' '+str(op['qubits']))
        parts.append(f'<g><title>{title}</title><line x1="{x}" x2="{x}" y1="{min(ys)}" y2="{max(ys)}" stroke="#087f8c"/>')
        for y in ys:parts.append(f'<rect x="{x-20}" y="{y-9}" width="40" height="18" fill="#e5f5f2" stroke="#087f8c"/><text x="{x}" y="{y+4}" text-anchor="middle" font-family="sans-serif" font-size="10">{label}</text>')
        parts.append('</g>')
    parts.append(f'<text x="12" y="{height-15}" font-family="sans-serif" font-size="11">Q={metrics["Q"]}, D={metrics["D"]}, QD={metrics["QD"]}; showing {len(qubits)} of {c.num_qubits} qubits. Full operands are in hover titles and schedule JSON.</text></svg>')
    out=Path(output)
    if out.exists():raise FileExistsError('Timeline destination exists')
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(''.join(parts),encoding='utf-8')
    return dict(output=str(out),circuit=payload['circuit'],start=start,stop=stop,shown_qubits=qubits)
