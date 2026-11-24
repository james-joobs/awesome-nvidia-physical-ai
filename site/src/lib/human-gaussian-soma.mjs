import * as THREE from 'three';
import {dyno} from '@sparkjsdev/spark';

// A known-rig renderer control. This is not an RGB-trained 4D reconstruction.
// Gaussian footprints are isotropic; only centers are LBS-deformed.
export class SomaSkinnedGaussians {
  constructor(meta, indices, weights, matrices) {
    const width=1024,height=Math.ceil(meta.gaussians/width),size=width*height;
    const influences=meta.influences??8,layers=Math.ceil(influences/4);
    const ids=new Float32Array(size*4*layers),ws=new Float32Array(size*4*layers);
    for(let i=0;i<meta.gaussians;i++)for(let j=0;j<influences;j++){
      const to=(Math.floor(j/4)*size+i)*4+j%4;ids[to]=indices[i*influences+j];ws[to]=weights[i*influences+j];
    }
    const arrayTexture=data=>{const t=new THREE.DataArrayTexture(data,width,height,layers);t.type=THREE.FloatType;t.format=THREE.RGBAFormat;t.internalFormat='RGBA32F';t.minFilter=t.magFilter=THREE.NearestFilter;t.needsUpdate=true;return t;};
    const poseTexture=new THREE.DataTexture(matrices,meta.bones*4,meta.frames,THREE.RGBAFormat,THREE.FloatType);poseTexture.internalFormat='RGBA32F';poseTexture.minFilter=poseTexture.magFilter=THREE.NearestFilter;poseTexture.needsUpdate=true;
    this.textures=[arrayTexture(ids),arrayTexture(ws),poseTexture];
    this.uniform=new dyno.DynoUniform({key:'somaGaussian',type:{type:'SomaGaussian'},globals:()=>[`struct SomaGaussian { sampler2DArray indices; sampler2DArray weights; sampler2D poses; float time; float fps; int frames; int influences; int width; };`],value:{indices:this.textures[0],weights:this.textures[1],poses:poseTexture,time:0,fps:meta.fps,frames:meta.frames,influences,width}});
    this.modifier=dyno.dynoBlock({gsplat:dyno.Gsplat},{gsplat:dyno.Gsplat},({gsplat})=>new dyno.Dyno({inTypes:{gsplat:dyno.Gsplat,rig:{type:'SomaGaussian'}},outTypes:{gsplat:dyno.Gsplat},inputs:{gsplat,rig:this.uniform},statements:({inputs,outputs})=>{
      const g=outputs.gsplat,r=inputs.rig;
      return [`${g}=${inputs.gsplat};
      if(isGsplatActive(${g}.flags)){
        ivec2 uv=ivec2(${g}.index % ${r}.width,${g}.index / ${r}.width);
        float frame=clamp(${r}.time*${r}.fps,0.0,float(${r}.frames-1));int f0=int(floor(frame));int f1=min(f0+1,${r}.frames-1);float blend=fract(frame);
        vec4 rest=vec4(${g}.center,1.0);vec3 position=vec3(0.0);
        for(int j=0;j<8;j++){if(j>=${r}.influences)break;int layer=j/4;int component=j%4;int bone=int(texelFetch(${r}.indices,ivec3(uv,layer),0)[component]);float weight=texelFetch(${r}.weights,ivec3(uv,layer),0)[component];
          if(weight>0.0){
            mat4 a=transpose(mat4(texelFetch(${r}.poses,ivec2(bone*4,f0),0),texelFetch(${r}.poses,ivec2(bone*4+1,f0),0),texelFetch(${r}.poses,ivec2(bone*4+2,f0),0),texelFetch(${r}.poses,ivec2(bone*4+3,f0),0)));
            mat4 b=transpose(mat4(texelFetch(${r}.poses,ivec2(bone*4,f1),0),texelFetch(${r}.poses,ivec2(bone*4+1,f1),0),texelFetch(${r}.poses,ivec2(bone*4+2,f1),0),texelFetch(${r}.poses,ivec2(bone*4+3,f1),0)));
            position+=weight*mix((a*rest).xyz,(b*rest).xyz,blend);
          }
        }
        ${g}.center=position;
      }`];
    }}).outputs);
  }
  update(seconds){this.uniform.value.time=seconds;}
  dispose(){for(const texture of this.textures)texture.dispose();}
}
