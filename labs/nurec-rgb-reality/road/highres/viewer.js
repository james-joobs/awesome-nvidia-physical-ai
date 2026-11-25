import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { SparkRenderer } from '@sparkjsdev/spark';
import { loadRoadAtlas } from '../viewer.js';

const groundUp = new THREE.Vector3(0, 0, 1);
const axis = (pose, column) => new THREE.Vector3(...pose.map(row => row[column]));
const lerpAxis = (a, b, c, blend) => axis(a, c).lerp(axis(b, c), blend);
const dimensions = {
  car: [4.2, 1.75, 1.45, 0x536c7c], truck: [7.5, 2.15, 2.5, 0x8b939b],
  bus: [9, 2.3, 2.95, 0x377e8e], tram: [10, 2.25, 2.9, 0x43846d],
  person: [.42, .42, 1.65, 0xa67852], rider: [1.55, .55, 1.52, 0xa67852],
  motorcycle: [1.8, .6, 1.35, 0x596c77], bicycle: [1.6, .5, .97, 0x745d4f],
};

function addActors(scene, releases) {
  const box = new THREE.BoxGeometry();
  const rounded = new RoundedBoxGeometry(1, 1, 1, 2, .15);
  const wheel = new THREE.CylinderGeometry(1, 1, 1, 10);
  const rubber = new THREE.MeshStandardMaterial({ color: 0x14191d });
  const glass = new THREE.MeshStandardMaterial({ color: 0x2b3941, roughness: .3 });
  const pools = {};
  const paints = Object.fromEntries(Object.entries(dimensions).map(([name, [, , , color]]) =>
    [name, new THREE.MeshStandardMaterial({ color, roughness: .56 })]));
  releases.push(() => {
    box.dispose(); rounded.dispose(); wheel.dispose(); rubber.dispose(); glass.dispose();
    for (const paint of Object.values(paints)) paint.dispose();
  });
  const create = name => {
    const [length, width, height] = dimensions[name];
    const group = new THREE.Group();
    const part = (geometry, paint, size, position) => {
      const mesh = new THREE.Mesh(geometry, paint);
      mesh.scale.set(...size);
      mesh.position.set(...position);
      group.add(mesh);
    };
    if (name === 'person' || name === 'rider') {
      part(box, paints[name], [.36, .38, height*.43], [0, 0, height*.58]);
      part(box, paints[name], [.21, .23, .23], [0, 0, height*.91]);
      part(box, rubber, [.19, .27, height*.4], [0, 0, height*.2]);
    }
    if (['car', 'truck', 'bus', 'tram'].includes(name)) {
      const cabin = name === 'car' ? .55 : .86;
      part(rounded, paints[name], [length, width, height*.51], [0, 0, height*.36]);
      part(rounded, glass, [length*cabin, width*.91, height*.37], [0, 0, height*.73]);
      part(rounded, paints[name], [length*cabin*.91, width*.88, height*.11], [0, 0, height*.92]);
      for (const x of [-.32, .32]) for (const y of [-.45, .45]) {
        part(wheel, rubber, [.3, .18, .3], [length*x, width*y, .3]);
      }
    }
    if (['rider', 'motorcycle', 'bicycle'].includes(name)) {
      part(box, paints[name], [length*.8, width*.45, .15], [0, 0, .42]);
      for (const x of [-.32, .32]) part(wheel, rubber, [.30, .10, .30], [length*x, 0, .30]);
    }
    scene.add(group);
    return group;
  };
  return (from, to, fraction, yaw, ego, camera, enabled) => {
    for (const pool of Object.values(pools)) for (const model of pool) model.visible = false;
    if (!enabled) return 0;
    const next = new Map(to.map(actor => [actor[0], actor]));
    const used = {};
    let count = 0;
    for (const actor of from) {
      const [id, name, x, y, heading] = actor;
      const destination = next.get(id) ?? actor;
      const centerX = THREE.MathUtils.lerp(x, destination[2], fraction);
      const centerY = THREE.MathUtils.lerp(y, destination[3], fraction);
      if (Math.hypot(centerX-ego.x, centerY-ego.y) < 1.65) continue;
      const [length, width, height] = dimensions[name];
      const angle = heading ?? yaw;
      const dx = camera.x-centerX, dy = camera.y-centerY;
      const nearLong = Math.abs(dx*Math.cos(angle)+dy*Math.sin(angle)) < length*.52+.4;
      const nearLat = Math.abs(-dx*Math.sin(angle)+dy*Math.cos(angle)) < width*.54+.4;
      if (nearLong && nearLat && camera.z < height+.55) continue;
      const pool = pools[name] ??= [];
      const index = used[name] ?? 0;
      used[name] = index+1;
      const model = pool[index] ??= create(name);
      model.position.set(centerX, centerY, .02);
      const start = heading ?? yaw, end = destination[4] ?? start;
      model.rotation.z = start+Math.atan2(Math.sin(end-start), Math.cos(end-start))*fraction;
      model.visible = true;
      count++;
    }
    return count;
  };
}

export async function mountHighresViewer(root, signal, initial) {
  const releases = [];
  const q = name => root.querySelector(`[data-hq-${name}]`);
  const stage = q('stage');
  const base = root.dataset.hqBase;
  const ko = root.dataset.locale === 'ko';
  let closed = false;
  const release = () => {
    if (closed) return;
    closed = true;
    for (const dispose of releases.reverse()) dispose();
  };
  const on = (target, event, callback) => {
    target.addEventListener(event, callback);
    releases.push(() => target.removeEventListener(event, callback));
  };
  const get = async url => {
    const response = await fetch(url, { signal });
    if (!response.ok) throw new Error(`Cannot open scene asset (HTTP ${response.status})`);
    return response;
  };
  try {
    const road = await loadRoadAtlas(get, base);
    releases.push(() => road.dispose());
    const surround = await (await get(base+'road/surround.json')).json();
    const scenery = await road.loadSurroundings();
    releases.push(() => scenery.dispose());
    const background = await road.loadBackground();
    releases.push(() => background.dispose());
    const model = await new GLTFLoader().setMeshoptDecoder(MeshoptDecoder)
      .parseAsync(await (await get(root.dataset.hqCar)).arrayBuffer(), '');
    releases.push(() => {
      const geometry = new Set(), materials = new Set(), textures = new Set();
      model.scene.traverse(item => {
        if (item.geometry) geometry.add(item.geometry);
        if (item.material) for (const material of [item.material].flat()) materials.add(material);
      });
      for (const material of materials) {
        for (const value of Object.values(material)) if (value?.isTexture) textures.add(value);
        material.dispose();
      }
      for (const texture of textures) texture.dispose();
      for (const item of geometry) item.dispose();
    });
    signal.throwIfAborted();

    const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
    const canvas = renderer.domElement;
    canvas.tabIndex = 0;
    canvas.setAttribute('aria-label', root.dataset.hqCanvasLabel);
    stage.prepend(canvas);
    releases.push(() => {
      renderer.setAnimationLoop(null);
      renderer.dispose();
      renderer.forceContextLoss();
      canvas.remove();
    });

    const scene = new THREE.Scene();
    const spark = new SparkRenderer({ renderer });
    releases.push(() => spark.dispose());
    scene.add(spark, background, road.mesh, scenery.group);
    background.visible = road.mesh.visible = scenery.group.visible = true;
    scene.add(new THREE.HemisphereLight(0xf3f8ff, 0x766e64, 2.3));
    const sun = new THREE.DirectionalLight(0xffffff, 2);
    sun.position.set(-9, 5, 16);
    scene.add(sun);
    const car = new THREE.Group();
    model.scene.rotation.x = Math.PI/2;
    const bounds = new THREE.Box3().setFromObject(model.scene);
    const scale = 4.9/(bounds.max.x-bounds.min.x);
    model.scene.scale.multiplyScalar(scale);
    model.scene.position.copy(bounds.getCenter(new THREE.Vector3())).multiplyScalar(-scale);
    model.scene.position.z = -scale*bounds.min.z;
    car.add(model.scene);
    scene.add(car);
    const shadow = new THREE.Mesh(new THREE.PlaneGeometry(6.2, 3.15), new THREE.ShaderMaterial({
      transparent: true,
      depthWrite: false,
      vertexShader: `
        varying vec2 footprint;
        void main() {
          footprint = 2.0 * uv - 1.0;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        varying vec2 footprint;
        void main() {
          float opacity = .38 * (1.0 - smoothstep(.3, 1.0, length(footprint)));
          gl_FragColor = vec4(.06, .07, .08, opacity);
        }
      `,
    }));
    scene.add(shadow);
    releases.push(() => { shadow.geometry.dispose(); shadow.material.dispose(); });
    const showActors = addActors(scene, releases);

    const camera = new THREE.PerspectiveCamera(54, 1, .05, 250);
    camera.up.copy(groundUp);
    const controls = new OrbitControls(camera, canvas);
    controls.enableDamping = true;
    controls.dampingFactor = .14;
    controls.maxDistance = 24;
    controls.minDistance = .5;
    controls.maxPolarAngle = Math.PI*.53;
    releases.push(() => controls.dispose());

    const { frames } = surround;
    const path = road.manifest.scene_fit.front_path;
    if (frames.length !== path.length || path.length < 2) throw new Error('Invalid route length');
    const route = new THREE.Line(new THREE.BufferGeometry().setFromPoints(path.map(({pose}) =>
      new THREE.Vector3(pose[0][3], pose[1][3], .06))),
    new THREE.LineBasicMaterial({ color: 0xb5ed59, transparent: true, opacity: .9, depthWrite: false }));
    scene.add(route);
    releases.push(() => { route.geometry.dispose(); route.material.dispose(); });
    const duration = frames.at(-1).time;
    const time = q('time'), offset = q('offset'), lift = q('lift');
    const readout = q('readout'), play = q('play'), rgb = q('rgb'), note = q('note');
    const traffic = q('traffic'), routeLine = q('route-line');
    const modes = [...root.querySelectorAll('[data-hq-mode]')];
    const directions = [...root.querySelectorAll('[data-hq-camera]')];
    let mode = initial?.mode ?? 'chase', direction = initial?.direction ?? 'front';
    let playing = false, last = 0, actors = 0, image = '', sourceTime = 0;
    const lookahead = new Image();
    let unregistered, orbitAnchor;

    const updatePose = (restartOrbit = false) => {
      const t = Number(time.value);
      const upcoming = frames.findIndex(frame => frame.time > t);
      const hi = upcoming === -1 ? path.length-1 : upcoming;
      const lo = Math.max(0, hi-1);
      const a = path[lo].pose, b = path[hi].pose;
      const blend = (t-frames[lo].time)/(frames[hi].time-frames[lo].time || 1);
      const frame = blend < .5 ? frames[lo] : frames[hi];
      const position = lerpAxis(a, b, 3, blend);
      const forward = lerpAxis(a, b, 2, blend).normalize();
      const left = new THREE.Vector3().crossVectors(groundUp, forward).normalize();
      const floor = THREE.MathUtils.clamp(position.z-1.8, -.65, .65);
      const yaw = Math.atan2(forward.y, forward.x);
      car.position.copy(position).addScaledVector(forward, -1.35);
      car.position.z = floor;
      car.rotation.z = yaw;
      car.visible = mode === 'chase' || mode === 'orbit';
      shadow.position.set(car.position.x, car.position.y, .028);
      shadow.rotation.z = yaw;
      shadow.visible = car.visible;
      controls.enabled = mode === 'orbit' || mode === 'chase';
      const adjust = controls.enabled;

      const before = frames[lo].cameras[direction], after = frames[hi].cameras[direction];
      const calibrated = before ?? after;
      const fallbackRgb = mode === 'calibrated' && !calibrated;
      if (mode === 'calibrated' && !fallbackRgb) {
        const start = before ?? after, end = after ?? before;
        camera.fov = THREE.MathUtils.lerp(start.fov, end.fov, blend);
        camera.position.copy(lerpAxis(start.pose, end.pose, 3, blend));
        camera.up.copy(lerpAxis(start.pose, end.pose, 1, blend)).negate().normalize();
        camera.lookAt(camera.position.clone().add(lerpAxis(start.pose, end.pose, 2, blend).normalize()));
      } else if (adjust) {
        camera.fov = mode === 'chase' ? 58 : 54;
        camera.up.copy(groundUp);
        if (mode === 'chase') {
          camera.position.copy(position).addScaledVector(left, Number(offset.value)).addScaledVector(forward, -6.7);
          camera.position.z = floor+3.4+Number(lift.value);
          controls.target.copy(position).addScaledVector(forward, 5.5);
          controls.target.z = floor+1.25;
        } else {
          if (!orbitAnchor || restartOrbit) {
            camera.position.copy(position).addScaledVector(left, 2.4+Number(offset.value))
              .addScaledVector(forward, -3.6);
            camera.position.z = floor+3.0+Number(lift.value);
            controls.target.copy(position).addScaledVector(forward, 7);
          } else {
            const step = position.clone().sub(orbitAnchor);
            camera.position.add(step);
            controls.target.add(step);
          }
          orbitAnchor = position;
        }
        controls.update();
      }
      camera.updateProjectionMatrix();

      const showRgb = mode === 'rgb' || fallbackRgb;
      route.visible = routeLine.checked && !showRgb;
      actors = showActors(frame.actors, blend < .5 ? frames[hi].actors : frames[lo].actors,
        blend < .5 ? blend : 1-blend, yaw, car.position, camera.position, traffic.checked && !showRgb);
      canvas.hidden = showRgb;
      rgb.hidden = !showRgb;
      sourceTime = frame.time;
      if (showRgb) {
        const next = frame.rgb[direction];
        if (next && next !== image) {
          image = next;
          rgb.src = base+'road/'+next;
          const future = frames[blend < .5 ? hi : hi+1]?.rgb[direction];
          if (future) lookahead.src = base+'road/'+future;
        }
      }
      if (unregistered !== fallbackRgb) {
        unregistered = fallbackRgb;
        updateNote();
      }
      readout.textContent = ko ? `${t.toFixed(1)}초` : `${t.toFixed(1)} s`;
    };

    const updateNote = () => {
      note.textContent = unregistered ? (ko ? '이 시점의 3D 카메라 자세를 복원하지 못해 실제 RGB를 표시합니다.' : 'Camera pose unavailable here. Showing the original RGB frame.')
        : mode === 'rgb' ? (ko ? 'KITScenes에서 촬영한 카메라 RGB입니다. 주행 시간에 맞춰 샘플을 표시합니다.' : 'Original KITScenes camera RGB, sampled along the timeline.')
        : (ko ? 'Volvo는 추가한 기준 차량입니다. 주변 차량과 보행자는 RGB에서 추정한 위치를 3D 모형으로 표시합니다.' : 'The Volvo is a reference vehicle. Other vehicles and people are 3D proxies positioned from RGB observations.');
    };
    const updateButtons = () => {
      for (const button of modes) button.setAttribute('aria-pressed', String(button.dataset.hqMode === mode));
      for (const button of directions) button.setAttribute('aria-pressed', String(button.dataset.hqCamera === direction));
      q('directions').hidden = mode !== 'calibrated' && mode !== 'rgb';
      q('overlays').hidden = mode === 'rgb';
      for (const label of root.querySelectorAll('[data-hq-adjust]')) label.hidden = !controls.enabled;
      updateNote();
    };
    const setPlaying = state => {
      playing = state;
      last = 0;
      play.setAttribute('aria-pressed', String(state));
      play.textContent = state ? (ko ? '일시 정지' : 'Pause') : (ko ? '재생' : 'Play');
    };
    time.max = String(duration);
    time.value = '0';
    offset.value = '0';
    lift.value = '.35';
    on(time, 'input', () => updatePose());
    on(traffic, 'change', () => updatePose());
    on(routeLine, 'change', () => updatePose());
    for (const input of [offset, lift]) on(input, 'input', () => updatePose(true));
    for (const button of modes) on(button, 'click', () => {
      mode = button.dataset.hqMode;
      updatePose(true);
      updateButtons();
    });
    for (const button of directions) on(button, 'click', () => {
      direction = button.dataset.hqCamera;
      updatePose();
      updateButtons();
    });
    on(play, 'click', () => {
      if (!playing && Number(time.value) >= duration-.01) {
        time.value = '0';
        updatePose();
      }
      setPlaying(!playing);
    });
    setPlaying(false);
    updatePose();
    updateButtons();
    releases.push(() => { rgb.hidden = true; rgb.removeAttribute('src'); lookahead.removeAttribute('src'); });

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
    let clock = 0;
    renderer.setAnimationLoop(now => {
      if (!visible || document.hidden) { last = 0; return; }
      if (playing) {
        // Accumulate wall time even when the slider rounds smaller steps.
        if (last) clock += Math.min((now-last)/1000, .15);
        else clock = Number(time.value);
        last = now;
        time.value = String(Math.min(clock, duration));
        updatePose();
        if (clock >= duration) setPlaying(false);
      }
      if (!canvas.hidden) {
        if (controls.enabled) controls.update();
        renderer.render(scene, camera);
      }
    });
    on(time, 'input', () => { clock = Number(time.value); });
    root.highresViewState = () => ({
      position: camera.position.toArray(), frame: Number(time.value), duration, mode, direction,
      sourceTime, actors, vehicle: car.visible, routeVisible: route.visible,
      gaussians: road.manifest.scene_fit.gaussians,
    });
    releases.push(() => delete root.highresViewState);
    return release;
  } catch (error) {
    release();
    throw error;
  }
}
