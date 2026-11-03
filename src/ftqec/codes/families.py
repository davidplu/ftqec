"""Code-only CSS construction inputs; no extraction schedules or architectures."""
from .input import load


def shor_product(rows,columns=None):
    columns=rows if columns is None else columns
    if min(rows,columns)<2:raise ValueError('Repetition lengths at least two')
    n=rows*columns;generators=[]
    for r in range(rows):
        for j in range(columns-1):
            text=['I']*n;text[r*columns+j]=text[r*columns+j+1]='Z';generators.append(''.join(text))
    for r in range(rows-1):
        text=['I']*n
        for q in range(r*columns,(r+2)*columns):text[q]='X'
        generators.append(''.join(text))
    return load(dict(n=n,name=f'shor_product_{rows}_{columns}',generators=generators,metadata=dict(family='shor_product',construction='concatenated bit and phase repetition',rows=rows,columns=columns,designed_distance_claim=min(rows,columns))))


def hamming_hypergraph_product():
    # H has each nonzero binary column of length three exactly once.
    h=[[int(j>>i&1) for j in range(1,8)] for i in range(3)]
    n=7*7+3*3;generators=[]
    # H_X = [H tensor I_7 | I_3 tensor H^T].
    for a in range(3):
        for j in range(7):
            text=['I']*n
            for i in range(7):
                if h[a][i]:text[i*7+j]='X'
            for b in range(3):
                if h[b][j]:text[49+a*3+b]='X'
            generators.append(''.join(text))
    # H_Z = [I_7 tensor H | H^T tensor I_3].
    for i in range(7):
        for b in range(3):
            text=['I']*n
            for j in range(7):
                if h[b][j]:text[i*7+j]='Z'
            for a in range(3):
                if h[a][i]:text[49+a*3+b]='Z'
            generators.append(''.join(text))
    return load(dict(n=n,name='hamming_7_4_3_hypergraph_product',generators=generators,metadata=dict(family='hypergraph_product',classical_checks=h,construction_reference='https://arxiv.org/abs/0903.0566',construction='Tillich-Zemor hypergraph product; H_X=[H x I | I x H^T], H_Z=[I x H | H^T x I]',designed_parameters_claim=[58,16,3],qualification='Parameters independently checked in experiment; no circuit or winning genome provided')))
