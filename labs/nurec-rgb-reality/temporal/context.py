"""Discontinuity guards for sparse interactive viewpoints, in relative units."""
import math

def reset_reasons(previous,current):
    if previous is None:return []
    reasons=[];a=previous['forward'];b=current['forward'];norm=lambda v:math.sqrt(sum(x*x for x in v))
    cosine=sum(x*y for x,y in zip(a,b))/(norm(a)*norm(b))
    if cosine<math.cos(math.radians(12)):reasons.append('camera_rotation')
    if norm([x-y for x,y in zip(previous['camera'],current['camera'])])>.75:reasons.append('camera_translation')
    if previous.get('projection')!=current.get('projection'):reasons.append('projection_changed')
    if previous.get('variant')!=current.get('variant'):reasons.append('reconstruction_changed')
    if current['frame']<previous['frame'] or abs(current['frame']-previous['frame'])>4:reasons.append('timeline_jump')
    return reasons
