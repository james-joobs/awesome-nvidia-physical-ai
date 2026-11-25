import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { SparkRenderer } from '@sparkjsdev/spark';
import { loadRoadAtlas } from '../viewer.js';

export async function mountHighresViewer(root, signal) {
  const releases = [];
  const q = (name) => root.querySelector(`[data-hq-${name}]`);
  const stage = q('stage');
  const base = root.dataset.hqBase;
  let closed = false;
  const release = () => {
    if (closed) return;
    closed = true;
    for (const dispose of releases.reverse()) dispose();
  };
  const get = async (url) => {
    const response = await fetch(url, { signal });
    if (!response.ok) throw new Error(`Cannot open scene asset (HTTP ${response.status})`);
    return response;
  };
  try {
    const road = await loadRoadAtlas(get, base);
    releases.push(() => road.dispose());
    const scenery = await road.loadSurroundings();
    releases.push(() => scenery.dispose());
    const background = await road.loadBackground();
    releases.push(() => background.dispose());
    signal.throwIfAborted();

    const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
    const canvas = renderer.domElement;
    canvas.tabIndex = 0;
    canvas.setAttribute('aria-label', root.dataset.hqCanvasLabel);
    stage.append(canvas);
    releases.push(() => {
      renderer.setAnimationLoop(null);
      renderer.dispose();
      renderer.forceContextLoss();
      canvas.remove();
    });
    const scene = new THREE.Scene();
    scene.add(new SparkRenderer({ renderer }));
    const spark = scene.children[0];
    releases.push(() => spark.dispose());
    scene.add(background, road.mesh, scenery.group);
    background.visible = road.mesh.visible = scenery.group.visible = true;

    const camera = new THREE.PerspectiveCamera(54, 1, .05, 250);
    camera.up.set(0, 0, 1);
    const controls = new OrbitControls(camera, canvas);
    controls.enableDamping = true;
    controls.dampingFactor = .14;
    controls.maxDistance = 24;
    controls.minDistance = .5;
    controls.maxPolarAngle = Math.PI * .59;
    releases.push(() => controls.dispose());

    const path = road.manifest.scene_fit.front_path;
    const axisUp = new THREE.Vector3(0, 0, 1);
    const time = q('time');
    const offset = q('offset');
    const lift = q('lift');
    const updatePose = () => {
      const t = Number(time.value), lo = Math.floor(t);
      const a = path[lo].pose, b = path[Math.min(lo+1, path.length-1)].pose;
      const position = new THREE.Vector3(a[0][3], a[1][3], a[2][3])
        .lerp(new THREE.Vector3(b[0][3], b[1][3], b[2][3]), t-lo);
      const look = new THREE.Vector3(a[0][2], a[1][2], a[2][2])
        .lerp(new THREE.Vector3(b[0][2], b[1][2], b[2][2]), t-lo).normalize();
      const left = new THREE.Vector3().crossVectors(axisUp, look).normalize();
      position.addScaledVector(left, Number(offset.value));
      position.z += Number(lift.value);
      camera.position.copy(position);
      controls.target.copy(position).addScaledVector(look, 12);
      controls.target.z -= Number(lift.value) * .5;
      controls.update();
      q('readout').textContent = `${((path[lo].frame-path[0].frame)/10).toFixed(1)} s`;
    };
    time.max = String(path.length-1);
    time.value = String(Math.floor(path.length*.57));
    offset.value = '-0.8';
    lift.value = '0.3';
    for (const input of [time, offset, lift]) {
      input.addEventListener('input', updatePose);
      releases.push(() => input.removeEventListener('input', updatePose));
    }
    updatePose();

    const resize = () => {
      if (!stage.clientWidth || !stage.clientHeight) return;
      camera.aspect = stage.clientWidth/stage.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(stage.clientWidth, stage.clientHeight);
    };
    resize();
    const size = new ResizeObserver(resize);
    size.observe(stage);
    releases.push(() => size.disconnect());
    let visible = true;
    const intersection = new IntersectionObserver(([entry]) => visible = entry.isIntersecting);
    intersection.observe(stage);
    releases.push(() => intersection.disconnect());
    renderer.setAnimationLoop(() => {
      if (visible && !document.hidden) {
        controls.update();
        renderer.render(scene, camera);
      }
    });
    root.highresViewState = () => ({ position: camera.position.toArray(), frame: Number(time.value),
      gaussians: road.manifest.scene_fit.gaussians });
    releases.push(() => delete root.highresViewState);
    return release;
  } catch (error) {
    release();
    throw error;
  }
}
