// Pure scheduling policy. Native preview frames are never counted as AI outputs.
export class MotionPolicy {
  constructor({idleMs=180}={}){this.idleMs=idleMs;this.version=0;this.lastMotion=-Infinity;this.pose=null;this.refined=-1;}
  observe(pose,now){
    const previous=this.pose;
    let changed=!previous||pose.frame!==previous.frame||pose.variant!==previous.variant||JSON.stringify(pose.projection)!==JSON.stringify(previous.projection);
    if(previous&&!changed){
      const direction=p=>p.target.map((v,i)=>v-p.camera[i]),a=direction(previous),b=direction(pose),dot=a.reduce((s,v,i)=>s+v*b[i],0)/(Math.hypot(...a)*Math.hypot(...b));
      changed=Math.hypot(...pose.camera.map((v,i)=>v-previous.camera[i]))>.0005||dot<Math.cos(.03*Math.PI/180);
    }
    if(changed){this.pose=structuredClone(pose);this.lastMotion=now;this.version++;}
    return changed;
  }
  moving(now){return now-this.lastMotion<this.idleMs;}
  next(profile,now){
    if(!['adaptive','native'].includes(profile))return {phase:'continuous',width:1024,version:this.version};
    if(this.moving(now))return profile==='native'?null:{phase:'preview',width:512,version:this.version};
    return this.refined===this.version?null:{phase:'refine',width:1024,version:this.version};
  }
  acceptRefinement(version){if(version!==this.version)return false;this.refined=version;return true;}
}
