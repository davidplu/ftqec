"""Optional BP-OSD over complete Stim detector-error mechanisms.

One column retains the entire correlated detector/logical effect of an error
instruction, including separator components. The physical sampler is unchanged.
This is a heuristic independent-DEM-mechanism decoder, not a distance proof or
a location-exclusive maximum-likelihood physical decoder.
"""
import time
from importlib.metadata import version
from ..results.artifacts import digest


def matrices(dem, max_errors=100000):
    import numpy as np
    from scipy.sparse import csc_matrix
    ds=[];ls=[];probabilities=[]
    for instruction in dem.flattened():
        if instruction.type!='error':continue
        if len(probabilities)>=max_errors:raise MemoryError('BP-OSD mechanism limit')
        d=set();l=set()
        for t in instruction.targets_copy():
            if t.is_relative_detector_id():d.symmetric_difference_update((t.val,))
            elif t.is_logical_observable_id():l.symmetric_difference_update((t.val,))
            elif not t.is_separator():raise ValueError('Unsupported DEM target')
        probability=instruction.args_copy()[0]
        if not 0<=probability<=1:raise ValueError('Invalid DEM probability')
        ds.append(sorted(d));ls.append(sorted(l));probabilities.append(probability)
    def matrix(columns,rows):
        rr=[r for column in columns for r in column]
        cc=[c for c,column in enumerate(columns) for _ in column]
        return csc_matrix((np.ones(len(rr),dtype=np.uint8),(rr,cc)),shape=(rows,len(columns)),dtype=np.uint8)
    return matrix(ds,dem.num_detectors),matrix(ls,dem.num_observables),probabilities


class Decoder:
    def __init__(self,dem,max_errors=100000,max_iter=50,osd_order=2):
        from ldpc import BpOsdDecoder
        self.h,self.l,probabilities=matrices(dem,max_errors)
        # OSD searches free variables. Some native library builds do not guard
        # an order larger than that dimension, so validate it before entering C++.
        pivots={}
        for column in range(self.h.shape[1]):
            value=sum(1<<int(row) for row in self.h.indices[self.h.indptr[column]:self.h.indptr[column+1]])
            while value:
                pivot=value.bit_length()-1
                if pivot not in pivots:pivots[pivot]=value;break
                value^=pivots[pivot]
        if type(osd_order) is not int or osd_order<0 or type(max_iter) is not int or max_iter<1:raise ValueError('BP-OSD parameters')
        effective_order=min(osd_order,self.h.shape[1]-len(pivots))
        self.parameters=dict(max_iter=max_iter,bp_method='minimum_sum',ms_scaling_factor=.625,
                             schedule='serial',omp_thread_count=1,osd_method='OSD_CS' if effective_order else 'OSD_0',osd_order=effective_order)
        self.backend=BpOsdDecoder(self.h,error_channel=probabilities,**self.parameters) if self.h.shape[1] and self.h.shape[0] else None
        self.receipt=dict(decoder='bposd',decoder_version=version('ldpc'),parameters=self.parameters,
                          detectors=self.h.shape[0],mechanisms=self.h.shape[1],observables=self.l.shape[0],
                          dem_hash=digest(str(dem)),approximation='BP/OSD heuristic on complete independent DEM mechanisms; not physical-location-exclusive ML',
                          correlated_effects='Every DEM instruction is one column; separator components are not split')
    def decode(self,detectors):
        import numpy as np
        detectors=np.asarray(detectors,dtype=np.uint8)
        if detectors.ndim!=2 or detectors.shape[1]!=self.h.shape[0] or np.any(detectors>1):raise ValueError('Detector sample shape or values')
        predictions=np.zeros((len(detectors),self.l.shape[0]),dtype=np.uint8);inconsistent=0
        for i,syndrome in enumerate(detectors):
            correction=np.asarray(self.backend.decode(syndrome),dtype=np.uint8) if self.backend is not None else np.zeros(self.h.shape[1],dtype=np.uint8)
            if np.any((self.h@correction)%2!=syndrome):inconsistent+=1
            predictions[i]=(self.l@correction)%2
        return predictions,inconsistent


def evaluate_bposd(c,p,shots,seed,max_decoder_faults=100000):
    import numpy as np
    from .monte_carlo import model,interval
    start=time.perf_counter();cpu=time.process_time()
    try:
        import ldpc  # noqa: F401
    except ImportError:
        return dict(status='UNSUPPORTED_DECODER',decoder='bposd',reason='Install ftqec[bposd]')
    sc=model(c,p);dem=sc.detector_error_model(decompose_errors=False,approximate_disjoint_errors=False).flattened()
    build_cpu=time.process_time();build_wall=time.perf_counter();decoder=Decoder(dem,max_decoder_faults)
    build=dict(cpu=time.process_time()-build_cpu,wall=time.perf_counter()-build_wall)
    det,obs=sc.compile_detector_sampler(seed=seed).sample(shots,separate_observables=True)
    dc=time.process_time();dw=time.perf_counter();predicted,inconsistent=decoder.decode(det)
    failures=int(np.count_nonzero(np.any(predicted!=obs,axis=1)))
    return dict(**decoder.receipt,p=p,shots=shots,seed=seed,failures=failures,rate=failures/shots,
                confidence=interval(failures,shots),decoder_inconsistent_syndromes=inconsistent,
                failure_metric='any logical observable prediction mismatch',
                decoder_build_cost=build,decoder_inference_cost=dict(cpu=time.process_time()-dc,wall=time.perf_counter()-dw),
                noise='physical_memory_operation_local' if c.boundary_model=='repeated_noisy_memory' else 'operation_depolarizing_reset_X_measurement_flip_perfect_boundaries',
                stim_hash=digest(str(sc)),sample_hash=digest(dict(detectors=np.packbits(det,axis=1).tolist(),observables=np.packbits(obs,axis=1).tolist())),
                cpu=time.process_time()-cpu,wall=time.perf_counter()-start)
