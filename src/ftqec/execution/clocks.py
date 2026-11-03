"""Active elapsed time for safeguards, alongside ordinary elapsed-time reports."""
import os,time


def active_time():
    if os.name=="nt":
        import ctypes
        value=ctypes.c_ulonglong()
        if ctypes.windll.kernel32.QueryUnbiasedInterruptTime(ctypes.byref(value)):
            return value.value*1e-7
    return time.perf_counter()


ACTIVE_CLOCK_SCOPE="Windows unbiased interrupt time excludes sleep/hibernation" if os.name=="nt" else "platform performance counter; sleep semantics platform-dependent"
