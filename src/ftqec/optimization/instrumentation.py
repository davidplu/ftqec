import time,psutil

def timed(function,*args):
    cpu=time.process_time();wall=time.perf_counter();result=function(*args)
    return result,dict(cpu=time.process_time()-cpu,wall=time.perf_counter()-wall,rss=psutil.Process().memory_info().rss,memory_scope="end-of-phase resident set, not a phase peak")
