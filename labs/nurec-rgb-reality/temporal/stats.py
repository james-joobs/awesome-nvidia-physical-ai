"""Separate delivered AI updates, browser frames and model-forward latency."""
import math
import statistics


def percentile(values, q):
    if not values:
        raise ValueError('No measurements')
    values = sorted(values)
    i = (len(values) - 1) * q
    lo, hi = math.floor(i), math.ceil(i)
    return values[lo] + (values[hi] - values[lo]) * (i - lo)


def interaction_summary(recording):
    start, end = recording['before']['now'], recording['after']['now']
    if end <= start:
        raise ValueError('Recording clock must advance')
    rows = [r for r in recording['rows'] if not r.get('discarded_stale') and start <= r.get('completed_at_ms', -1) <= end]
    times = [r['completed_at_ms'] for r in rows]
    if len(rows) < 2 or any(b <= a for a, b in zip(times, times[1:])):
        raise ValueError('Need distinct monotonically painted GPU outputs')
    contextual = [r for r in rows if r['history_frames'] == 4]
    if not contextual:
        raise ValueError('No actual temporal-context outputs')
    frames = [t for t in recording['frame_timestamps_ms'] if start <= t <= end]
    gaps = [b - a for a, b in zip(frames, frames[1:])]
    if not gaps or min(gaps) <= 0:
        raise ValueError('Invalid browser frame timestamps')
    return {
        'seconds': (end - start) / 1000,
        'painted_ai_updates': len(rows),
        'delivered_ai_fps': len(rows) * 1000 / (end - start),
        'temporal_model_median_ms': statistics.median(r['model_ms'] for r in contextual),
        'temporal_capture_to_paint_median_ms': statistics.median(r['round_trip_ms'] for r in contextual),
        'capture_to_paint_p95_ms': percentile([r['round_trip_ms'] for r in rows], .95),
        'native_presented_fps': len(frames) * 1000 / (end - start),
        'native_frame_p95_ms': percentile(gaps, .95),
        'native_frames_over_50ms': sum(g > 50 for g in gaps),
        'discarded_stale': recording.get('discarded_stale', 0),
        'scope': 'Observed GPU outputs actually painted during this recording. Native render FPS is a separate client measure, not diffusion throughput. Model median uses history=4 only.',
    }
