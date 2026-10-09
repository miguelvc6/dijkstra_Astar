"""One isolated experiment: uninstrumented timing, then memory, then observation."""
import gc
import json
import math
import signal
import statistics
import sys
import time
import tracemalloc
from contextlib import contextmanager

from experiments.observe import observe
from experiments.registry import arguments, function
from experiments.validation import validate


class SearchTimeout(Exception):
    pass


@contextmanager
def deadline(seconds):
    """Interrupt a search in its own process; parent also enforces a hard timeout."""
    previous = signal.getsignal(signal.SIGALRM)
    def expired(*_):
        raise SearchTimeout(f'Search exceeded {seconds:g} seconds')
    signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def run(job):
    case, key = job['case'], job['algorithm']
    expected = math.inf if job['expected'] is None else job['expected']
    timeout = job.get('timeout', 10)
    fn, args = function(key), arguments(key, case)
    output = dict(status='ok', validated=False, timing_samples_ns=[], iterations_per_sample=0)
    phase = 'correctness'
    try:
        with deadline(timeout):
            result = fn(*args)
        validate(result, case, expected)
        output['validated'] = True
        output['cost'] = None if math.isinf(result[0]) else result[0]
        output['path_length'] = len(result[1])
        phase = 'timing'
        for _ in range(job.get('warmups', 2)):
            with deadline(timeout):
                fn(*args)
        gc.collect()
        with deadline(timeout):
            started = time.perf_counter_ns()
            fn(*args)
            calibration = max(time.perf_counter_ns() - started, 1)
        # Short searches are batched to reduce timer overhead; keep results alive
        # only for one invocation, and include normal path-return/allocation work.
        batch = min(1000, max(1, math.ceil(job.get('sample_ms', 10) * 1_000_000 / calibration)))
        output['iterations_per_sample'] = batch
        for _ in range(job.get('repeats', 9)):
            gc.collect()
            with deadline(max(timeout, timeout * batch)):
                started = time.perf_counter_ns()
                for _ in range(batch):
                    result = fn(*args)
                elapsed = time.perf_counter_ns() - started
            validate(result, case, expected)
            output['timing_samples_ns'].append(elapsed / batch)
        samples = output['timing_samples_ns']
        q1, _, q3 = statistics.quantiles(samples, n=4, method='inclusive')
        output.update(median_ns=statistics.median(samples), q1_ns=q1, q3_ns=q3)
        phase = 'memory'
        result = None
        gc.collect()
        with deadline(timeout):
            tracemalloc.start(1)
            try:
                result = fn(*args)
                current, peak = tracemalloc.get_traced_memory()
            finally:
                tracemalloc.stop()
        validate(result, case, expected)
        output.update(peak_python_bytes=peak, returned_live_python_bytes=current)
        phase = 'observation'
        with deadline(timeout):
            observed_result, stats, _ = observe(key, case)
        validate(observed_result, case, expected)
        output['operations'] = stats
    except SearchTimeout as error:
        output.update(status='timeout', phase=phase, error=str(error))
    except RecursionError as error:
        output.update(status='recursion_limit', phase=phase, error=str(error))
    except Exception as error:
        output.update(status='error', phase=phase, error=f'{type(error).__name__}: {error}')
    return output


if __name__ == '__main__':
    job = json.load(sys.stdin)
    print(json.dumps(run(job), allow_nan=False))
