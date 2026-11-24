import * as THREE from 'three';
import {dyno} from '@sparkjsdev/spark';

// Exact conditional 4D position, temporal opacity and real SH appearance.
// Conditional covariance is independent of query time, and is in ExtSplats.
export class TemporalGaussians {
 constructor(meta,motion,variance,sh){
  this.meta=meta;const width=1024,height=Math.ceil(meta.gaussians/width),size=width*height;
  const texture=data=>{const t=new THREE.DataTexture(data,width,height,THREE.RGBAFormat,THREE.FloatType);t.internalFormat='RGBA32F';t.minFilter=t.magFilter=THREE.NearestFilter;t.needsUpdate=true;return t;};
  const mv=new Float32Array(size*4);mv.set(motion);const vr=new Float32Array(size*4);vr.set(variance);
  const coefficients=new Uint16Array(size*4*16);
  for(let i=0;i<meta.gaussians;i++)for(let k=0;k<16;k++){const from=(i*16+k)*3,to=(k*size+i)*4;coefficients[to]=sh[from];coefficients[to+1]=sh[from+1];coefficients[to+2]=sh[from+2];}
  const shTex=new THREE.DataArrayTexture(coefficients,width,height,16);shTex.type=THREE.HalfFloatType;shTex.format=THREE.RGBAFormat;shTex.internalFormat='RGBA16F';shTex.minFilter=shTex.magFilter=THREE.NearestFilter;shTex.needsUpdate=true;
  this.uniform=new dyno.DynoUniform({key:'native4d',type:{type:'Native4D'},globals:()=>[`struct Native4D { sampler2D motion; sampler2D variance; sampler2DArray sh; vec3 camera; float time; float threshold; int width; int degree; };`],value:{motion:texture(mv),variance:texture(vr),sh:shTex,camera:new THREE.Vector3(),time:0,threshold:meta.marginal_threshold,width,degree:meta.degree}});
  this.modifier=dyno.dynoBlock({gsplat:dyno.Gsplat},{gsplat:dyno.Gsplat},({gsplat})=>new dyno.Dyno({inTypes:{gsplat:dyno.Gsplat,model:{type:'Native4D'}},outTypes:{gsplat:dyno.Gsplat},inputs:{gsplat,model:this.uniform},statements:({inputs,outputs})=>{const g=outputs.gsplat,m=inputs.model;return [`
   ${g}=${inputs.gsplat};
   if(isGsplatActive(${g}.flags)){
    ivec2 uv=ivec2(${g}.index % ${m}.width,${g}.index / ${m}.width);
    vec4 vt=texelFetch(${m}.motion,uv,0); float dt=${m}.time-vt.w;
    float marginal=exp(-0.5*dt*dt*texelFetch(${m}.variance,uv,0).x);
    ${g}.center+=vt.xyz*dt;
    ${g}.rgba.a*=marginal>=${m}.threshold?marginal:0.0;
    vec3 dir=normalize(${g}.center-${m}.camera);float x=dir.x,y=dir.y,z=dir.z;
    float b[16];b[0]=0.28209479177387814;b[1]=-0.4886025119029199*y;b[2]=0.4886025119029199*z;b[3]=-0.4886025119029199*x;
    b[4]=1.0925484305920792*x*y;b[5]=-1.0925484305920792*y*z;b[6]=0.31539156525252005*(2.0*z*z-x*x-y*y);b[7]=-1.0925484305920792*x*z;b[8]=0.5462742152960396*(x*x-y*y);
    b[9]=-0.5900435899266435*y*(3.0*x*x-y*y);b[10]=2.890611442640554*x*y*z;b[11]=-0.4570457994644658*y*(4.0*z*z-x*x-y*y);b[12]=0.3731763325901154*z*(2.0*z*z-3.0*x*x-3.0*y*y);b[13]=-0.4570457994644658*x*(4.0*z*z-x*x-y*y);b[14]=1.445305721320277*z*(x*x-y*y);b[15]=-0.5900435899266435*x*(x*x-3.0*y*y);
    vec3 rgb=vec3(0.5);int count=(${m}.degree+1)*(${m}.degree+1);
    for(int k=0;k<16;k++){if(k>=count)break;rgb+=b[k]*texelFetch(${m}.sh,ivec3(uv,k),0).xyz;}
    ${g}.rgba.rgb=clamp(rgb,vec3(0.0),vec3(1.0));
   }
  `];}}).outputs);
 }
 update(seconds,camera){this.uniform.value.time=seconds;this.uniform.value.camera.copy(camera);}
}
