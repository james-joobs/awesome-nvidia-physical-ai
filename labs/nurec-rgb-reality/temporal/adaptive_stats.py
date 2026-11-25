"""Count only painted outputs inside recorded move/rest intervals."""
import statistics
from stats import percentile


def interaction_summary(recording):
    moving = [e for e in recording['events'] if e['kind'] == 'moving']
    resting = [e for e in recording['events'] if e['kind'] == 'rest']
    if not moving or len(moving) != len(resting):
        raise ValueError('Record matching move/rest intervals')
    if any(e['end_ms'] <= e['start_ms'] for e in moving + resting):
        raise ValueError('Intervals must advance')
    duration = sum(e['end_ms'] - e['start_ms'] for e in moving) / 1000
    inside = lambda t: any(e['start_ms'] <= t < e['end_ms'] for e in moving)
    rows = [r for r in recording['rows'] if not r.get('discarded_stale')]
    times = [r['completed_at_ms'] for r in rows]
    if any(b <= a for a, b in zip(times, times[1:])):
        raise ValueError('Paint timestamps must strictly increase')
    ai = [r for r in rows if inside(r['completed_at_ms'])]
    temporal = [r for r in ai if r['history_frames'] == 4]
    browser = [r for r in recording['presentation'] if r['kind'] == 'native-preview' and inside(r['at_ms'])]
    median = lambda values: statistics.median(values) if values else None
    stops = []
    for event in resting:
        start, end = event['start_ms'], event['end_ms']
        last_motion = max([m['at_ms'] for m in recording['motion'] if start <= m['at_ms'] < end] + [start])
        candidates = [r for r in rows if r['resolution'] == [1024, 576]
                      and last_motion <= r['input_view']['captured_at_ms']
                      and r['completed_at_ms'] < end]
        if not candidates:
            raise ValueError('No current-view HQ paint after camera settles')
        first = candidates[0]
        # Ignore pre-stop in-flight outputs. Count redundant *new* HQ captures
        # after the first current-view HQ result, within the same rest interval.
        redundant = [r for r in rows if first['completed_at_ms'] < r['input_view']['captured_at_ms'] < end]
        stops.append({'cycle': event['cycle'], 'sequence': first['sequence'],
                      'camera_inertia_ms': last_motion - start,
                      'pointer_stop_to_hq_ms': first['completed_at_ms'] - start,
                      'camera_stop_to_hq_ms': first['completed_at_ms'] - last_motion,
                      'model_calls': first['model_calls'],
                      'reused_reference_slots': first['reused_reference_slots'],
                      'redundant_idle_requests': len(redundant)})
    return {'moving_seconds': duration, 'painted_ai_updates_while_moving': len(ai),
            'delivered_ai_fps_while_moving': len(ai) / duration,
            'moving_model_median_ms': median([r['model_ms'] for r in temporal]),
            'moving_capture_to_paint_median_ms': median([r['round_trip_ms'] for r in ai]),
            'moving_capture_to_paint_p95_ms': percentile([r['round_trip_ms'] for r in ai], .95) if ai else None,
            'browser_preview_fps_while_moving': len(browser) / duration,
            'camera_stop_to_hq_median_ms': median([r['camera_stop_to_hq_ms'] for r in stops]),
            'pointer_stop_to_hq_median_ms': median([r['pointer_stop_to_hq_ms'] for r in stops]),
            'stops': stops,
            'scope': 'Only actual paints in three recorded mouse-drag intervals count as moving FPS. Browser previews are not AI frames. Camera stop uses the last significant pose change; pointer stop includes orbit damping. All passes are sequential on one GPU.'}
