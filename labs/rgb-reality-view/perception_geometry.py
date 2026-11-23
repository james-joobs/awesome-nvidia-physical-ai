"""RGB road-plane projection and short-clip association, in relative viewer units.

This is an explicit ground-contact assumption, not a learned 3D detector.
"""
import math

VEHICLES = {'car', 'truck', 'bus'}
def family(label):
    return 'vehicle' if label in VEHICLES else label

def ground_contact(pixel, K, rotation, position, max_range=45):
    """Intersect a pinhole RGB ray with z=0. Reject horizon/behind/far rays."""
    u, v = pixel
    ray = [(u-K[0][2])/K[0][0], (v-K[1][2])/K[1][1], 1]
    direction = [sum(rotation[i][j]*ray[j] for j in range(3)) for i in range(3)]
    if not all(math.isfinite(x) for x in direction+list(position)) or direction[2] >= -1e-4:
        return None
    t = -position[2]/direction[2]
    if t <= 0:
        return None
    point = [position[i]+t*direction[i] for i in range(3)]
    if math.dist(point[:2], position[:2]) > max_range:
        return None
    return [round(point[0], 5), round(point[1], 5), 0.0]

def rle_encode(values):
    counts=[]; previous=0; length=0
    for bit in values:
        bit=int(bool(bit))
        if bit==previous:length+=1
        else:counts.append(length);length=1;previous=bit
    counts.append(length)
    return counts

def associate(frames):
    """Merge nearby cross-camera estimates, then associate by class/position.

No source annotations or identity labels. IDs may switch; missing objects are
not extrapolated. A merge is deliberately forbidden within the same camera.
"""
    active={}; next_id=1
    for fi, frame in enumerate(frames):
        detections=[d for v in frame['views'].values() for d in v['detections'] if d['ground_position'] is not None]
        clusters=[]
        for d in sorted(detections, key=lambda d:-d['score']):
            radius=.65 if family(d['class'])=='vehicle' else .25
            candidates=[c for c in clusters if family(c['class'])==family(d['class']) and d['camera'] not in c['cameras'] and math.dist(c['position'][:2],d['ground_position'][:2])<radius]
            if candidates:
                c=min(candidates,key=lambda c:math.dist(c['position'][:2],d['ground_position'][:2]))
                c['members'].append(d);c['cameras'].append(d['camera'])
            else:
                clusters.append({'class':d['class'],'score':d['score'],'position':d['ground_position'],'cameras':[d['camera']],'members':[d]})
        used=set(); objects=[]
        for c in clusters:
            gate=2.0 if family(c['class'])=='vehicle' else .6
            candidates=[(math.dist(t['position'][:2],c['position'][:2]),tid) for tid,t in active.items() if tid not in used and fi-t['frame']<=2 and family(t['class'])==family(c['class'])]
            distance,tid=min(candidates,default=(float('inf'),None))
            if distance>gate:tid=next_id;next_id+=1
            used.add(tid);active[tid]={'position':c['position'],'class':c['class'],'frame':fi}
            for d in c['members']:d['track_id']=tid
            objects.append({'id':tid,'class':c['class'],'score':c['score'],'ground_position':c['position'],'cameras':c['cameras']})
        frame['objects']=objects
        active={tid:t for tid,t in active.items() if fi-t['frame']<=2}
    return next_id-1
