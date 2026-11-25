"""Resolution-isolated banks and deterministic stationary warm-start policy."""
HQ=(1024,576)
PREVIEW=(512,288)


def plan(execution, phase):
    if execution!='adaptive':
        if phase not in {None,'continuous'}:raise ValueError('Phase is reserved for adaptive execution')
        return 'hq',HQ
    if phase=='preview':return 'preview-512',PREVIEW
    if phase=='refine':return 'hq',HQ
    raise ValueError('Adaptive phase must be preview or refine')


def bootstrap_slots(history_length, mode, phase):
    # A stationary V1 call is deterministic in the pinned, eval-mode model.
    # One generated RGB is reused in four slots, then one actual V5 forward runs.
    # These slots are not four distinct observations or four displayed frames.
    return 4 if phase=='refine' and mode=='temporal' and history_length<4 else 0


def validate_input_size(execution, phase, size):
    if execution=='adaptive' and phase=='refine' and tuple(size)!=HQ:
        raise ValueError('HQ refinement requires a fresh1024x576 render, not the512 preview')
