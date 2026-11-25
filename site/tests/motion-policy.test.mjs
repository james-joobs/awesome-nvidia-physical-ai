import test from 'node:test';import assert from 'node:assert/strict';
import {MotionPolicy} from '../../labs/rgb-reality-view/motion-policy.mjs';
const pose=x=>({camera:[x,-4,2],target:[x,0,0],frame:13,variant:'guided',projection:[64,16/9]});
test('preview changes to HQ only after the camera quiet period',()=>{const p=new MotionPolicy({idleMs:180});p.observe(pose(0),0);assert.equal(p.next('adaptive',100).width,512);assert.equal(p.next('adaptive',181).phase,'refine');});
test('stale HQ is rejected and a valid idle result stops redundant generation',()=>{const p=new MotionPolicy();p.observe(pose(0),0);const old=p.version;p.observe(pose(1),200);assert.equal(p.acceptRefinement(old),false);assert.equal(p.acceptRefinement(p.version),true);assert.equal(p.next('adaptive',500),null);});
test('native preview never schedules diffusion while moving',()=>{const p=new MotionPolicy();p.observe(pose(0),0);assert.equal(p.next('native',100),null);assert.equal(p.next('native',300).phase,'refine');});
test('subthreshold camera motion accumulates against the last significant pose',()=>{const p=new MotionPolicy();p.observe(pose(0),0);assert.equal(p.observe(pose(.0002),50),false);assert.equal(p.observe(pose(.0004),100),false);assert.equal(p.observe(pose(.0007),150),true);});
