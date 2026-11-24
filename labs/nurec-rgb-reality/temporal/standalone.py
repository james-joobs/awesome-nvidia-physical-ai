"""Initialize exclusively from the publicly released Harmonizer checkpoint.

No base-model weights are fetched. The release includes the complete trained
live DiT and VAE parameters. Derived files stay in a private output directory;
the original checkpoint and upstream source are never modified. Inference is
refused if any learned parameter lacks an exact released tensor of its shape.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import torch
MODEL_SHA256='6e65e9ec33019a49f7f0d15f81f5e089c2527e131bd5339d6a14f9b3531db524'

def prepare(checkpoint,folder):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    digest=hashlib.file_digest(Path(checkpoint).open('rb'),'sha256').hexdigest()
    if digest!=MODEL_SHA256:raise ValueError('Use the pinned public Harmonizer checkpoint; preserve other model experiments separately')
    receipt=folder/'components.json';paths={'dit':folder/'harmonizer-live-dit.pt','vae':folder/'harmonizer-vae.pt'}
    if receipt.exists():
        old=json.loads(receipt.read_text())
        if old['checkpoint_sha256']!=digest:raise ValueError('Standalone component cache belongs to a different release')
        for k,path in paths.items():
            if hashlib.file_digest(path.open('rb'),'sha256').hexdigest()!=old['components'][k]['sha256']:raise ValueError('A standalone component cache changed')
        return paths,old
    if any(x.exists() for x in paths.values()):raise ValueError('Unknown partial component cache; preserve it and select a fresh directory')
    state=torch.load(checkpoint,map_location='cpu',weights_only=True,mmap=True);live={}
    for key,value in state['state_dict_unet'].items():
        if key.startswith('dit.'):live[key[4:]]=value
        elif key.startswith('net.'):live[key[4:]]=value
    if not live or not state['state_dict_vae']:raise ValueError('The public checkpoint does not contain complete model components')
    components={'dit':live,'vae':state['state_dict_vae']}
    for k,path in paths.items():torch.save(components[k],path)
    report={'schema':1,'checkpoint_sha256':digest,'weights_source':'Only nvidia/Harmonizer diffusion_harmonizer.pkl; no gated Cosmos checkpoint retrieved','components':{k:{'tensors':len(components[k]),'sha256':hashlib.file_digest(path.open('rb'),'sha256').hexdigest()} for k,path in paths.items()}}
    receipt.write_text(json.dumps(report,indent=2)+'\n');return paths,report

def patch_config(module,paths):
    original=module.get_pipeline_config
    def config(*args,**kwargs):
        value=original(*args,**kwargs);value.dit_path=str(paths['dit']);value.tokenizer['vae_pth']=str(paths['vae']);return value
    module.get_pipeline_config=config

def verify_parameters(model,checkpoint):
    released=torch.load(checkpoint,map_location='cpu',weights_only=True,mmap=True);unet={}
    for key,value in released['state_dict_unet'].items():
        if key.startswith('net.'):key='dit.'+key[4:]
        elif key.startswith('net_ema.'):key='dit_ema.'+key[8:]
        unet[key]=value
    groups={'dit':(model.unet,unet),'vae':(model._inner_vae(),released['state_dict_vae'])};counts={};mapping_counts={}
    canonical=lambda name:name.replace('_checkpoint_wrapped_module.','').replace('_orig_mod.','')
    for group,(target,source) in groups.items():
        # Activation-checkpoint/compile wrappers can expose different parameter
        # and state-dict names without changing the learned operation. Check
        # canonical names and actual values; strict=False alone is not proof.
        lookup={}
        for key,value in source.items():
            name=canonical(key)
            if name in lookup:raise ValueError(f'Ambiguous released parameter name: {name}')
            lookup[name]=value
        assignments={}
        for key,param in target.named_parameters():
            name=canonical(key)
            if name not in lookup or tuple(lookup[name].shape)!=tuple(param.shape):raise ValueError(f'Uncovered learned parameter: {group}.{key}')
        for key in target.state_dict():
            if canonical(key) in lookup:assignments[key]=lookup[canonical(key)]
        target.load_state_dict(assignments,strict=False)
        mapping_counts[group]=sum(canonical(key)!=key for key,_ in target.named_parameters())
        total=0
        for key,param in target.named_parameters():
            if param.is_meta:raise ValueError(f'Unmaterialized learned parameter: {group}.{key}')
            if not torch.equal(param.detach().cpu(),lookup[canonical(key)].to(dtype=param.dtype)):raise ValueError(f'Released parameter did not load exactly: {group}.{key}')
            total+=param.numel()
        counts[group]=total
    return {'all_learned_parameters_covered':True,'all_learned_parameters_equal_released_tensors':True,'parameter_counts':counts,'wrapper_names_remapped':mapping_counts,'scope':'All learned tensors loaded and exactly checked after dtype conversion, including activation-checkpoint wrapper names; architectural nonlearned buffers follow the pinned upstream implementation.'}
