import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { SparkRenderer } from '@sparkjsdev/spark';
import { loadRoadAtlas } from '../viewer.js';

const groundUp = new THREE.Vector3(0, 0, 1);
const axis = (pose, column) => new THREE.Vector3(...pose.map(row => row[column]));
const lerpAxis = (a, b, c, blend) => axis(a, c).lerp(axis(b, c), blend);
const groundClearance = .002;
const rgbRatio = 768/498;
const captions = {
  car: ['차량', 'Car'], truck: ['트럭', 'Truck'], transit: ['대중교통', 'Transit'],
  person: ['보행자', 'Person'],
  bicycle: ['자전거', 'Bicycle'], motorcycle: ['오토바이', 'Motorcycle'],
};
const colors = ['#b6ed65', '#78dbff', '#ffc967', '#ebadf6'];

function findTireContacts(model) {
  const contacts = Array(4).fill(null);
  const position = new THREE.Vector3();
  model.updateMatrixWorld(true);
  model.traverse(mesh => {
    const vertices = mesh.geometry?.getAttribute('position');
    if (!vertices) return;
    for (let i = 0; i < vertices.count; i++) {
      position.fromBufferAttribute(vertices, i).applyMatrix4(mesh.matrixWorld);
      if (position.z > .12 || Math.abs(position.x) < .7 || Math.abs(position.y) < .4) continue;
      const corner = (position.x > 0 ? 2 : 0)+(position.y > 0 ? 1 : 0);
      if (!contacts[corner] || position.z < contacts[corner].z) contacts[corner] = position.clone();
    }
  });
  if (contacts.some(contact => contact === null)) throw new Error('Missing Volvo tire contact vertices');
  return contacts;
}

function placeOnRoad(car, shadow, road, contacts, position, forward) {
  const yaw = Math.atan2(forward.y, forward.x);
  const heading = new THREE.Vector3(Math.cos(yaw), Math.sin(yaw), 0);
  const x = position.x-1.35*heading.x, y = position.y-1.35*heading.y;
  const slopeX = road.heightAt(x+.5, y)-road.heightAt(x-.5, y);
  const slopeY = road.heightAt(x, y+.5)-road.heightAt(x, y-.5);
  const normal = new THREE.Vector3(-slopeX, -slopeY, 1).normalize();
  heading.z = slopeX*heading.x+slopeY*heading.y;
  heading.normalize();
  const lateral = new THREE.Vector3().crossVectors(normal, heading).normalize();
  car.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(heading, lateral, normal));
  const rotated = contacts.map(contact => contact.clone().applyQuaternion(car.quaternion));
  const heights = rotated.map(tire => road.heightAt(x+tire.x, y+tire.y)-tire.z);
  const z = Math.max(...heights)+groundClearance;
  car.position.set(x, y, z);
  shadow.position.set(x, y, road.heightAt(x, y)+.006);
  shadow.quaternion.copy(car.quaternion);
  return heights.map(height => z-height);
}

function drawTracks(layer, observations, ko) {
  const width = layer.clientWidth;
  layer.replaceChildren(...observations.map(([id, category, box]) => {
    const [x1, y1, x2, y2] = box;
    const marker = document.createElement('div');
    marker.className = 'observed-track';
    marker.dataset.trackId = id;
    marker.style.setProperty('--track-color', colors[id % colors.length]);
    marker.style.left = `${100*x1}%`;
    marker.style.top = `${100*y1}%`;
    marker.style.width = `${100*(x2-x1)}%`;
    marker.style.height = `${100*(y2-y1)}%`;
    const title = document.createElement('span');
    title.textContent = `${captions[category][ko ? 0 : 1]} #${id}`;
    title.hidden = width*(x2-x1) < 33;
    marker.append(title);
    return marker;
  }));
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
    const bounds = new THREE.Box3().setFromObject(model.scene, true);
    const scale = 4.9/(bounds.max.x-bounds.min.x);
    model.scene.scale.multiplyScalar(scale);
    model.scene.position.copy(bounds.getCenter(new THREE.Vector3())).multiplyScalar(-scale);
    model.scene.position.z = -scale*bounds.min.z;
    const tireContacts = findTireContacts(model.scene);
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
      new THREE.Vector3(pose[0][3], pose[1][3], road.heightAt(pose[0][3], pose[1][3])+.045))),
    new THREE.LineBasicMaterial({ color: 0xb5ed59, transparent: true, opacity: .9, depthWrite: false }));
    scene.add(route);
    releases.push(() => { route.geometry.dispose(); route.material.dispose(); });
    const duration = frames.at(-1).time;
    const time = q('time'), offset = q('offset'), lift = q('lift');
    const readout = q('readout'), play = q('play'), rgb = q('rgb'), note = q('note');
    const inset = q('inset'), track = q('track'), routeLine = q('route-line');
    const source = q('source'), sourceFrame = q('source-frame'), boxes = q('boxes');
    const sourceTag = q('source-tag');
    const modes = [...root.querySelectorAll('[data-hq-mode]')];
    const directions = [...root.querySelectorAll('[data-hq-camera]')];
    let mode = initial?.mode ?? 'chase', direction = initial?.direction ?? 'front';
    let playing = false, last = 0, sourceTime = 0, tireGaps = [];
    let requested, shown, trackData, trackRequest;
    let trackError = false, visibleTracks = 0;
    const lookahead = new Image();
    let unregistered, orbitAnchor;

    const fitSource = () => {
      if (source.hidden) return false;
      const width = `${Math.min(source.clientWidth, source.clientHeight*rgbRatio)}px`;
      if (sourceFrame.style.width === width) return false;
      sourceFrame.style.width = width;
      return true;
    };
    const renderObservations = () => {
      const records = shown && track.checked && !source.hidden
        ? trackData?.cameras[shown.direction]?.[shown.index] ?? [] : [];
      drawTracks(boxes, records, ko);
      visibleTracks = records.length;
      const caption = directions.find(button => button.dataset.hqCamera === shown?.direction)?.textContent;
      sourceTag.textContent = trackError && track.checked
        ? (ko ? '추적 결과 로딩 실패' : 'Tracks unavailable')
        : caption ? `${ko ? '실사 RGB' : 'Camera RGB'} · ${caption}` : '';
    };
    const ensureTracks = () => {
      if (!track.checked || trackRequest) return;
      trackError = false;
      trackRequest = get(base+'road/tracks.json').then(response => response.json()).then(data => {
        if (data.schema !== 1 || data.times.length !== frames.length ||
            data.times.some((time, index) => time !== frames[index].time)) {
          throw new Error('Tracking data does not match the route timeline');
        }
        trackData = data;
        renderObservations();
      }).catch(error => {
        if (signal.aborted) return;
        trackError = true;
        renderObservations();
        console.error(error);
      });
    };
    on(rgb, 'load', () => {
      if (!requested || rgb.currentSrc !== requested.url) return;
      shown = requested;
      renderObservations();
    });
    const showSource = (show, pictureInPicture, index) => {
      source.hidden = !show;
      source.toggleAttribute('data-inset', pictureInPicture);
      if (!show) return;
      const resized = fitSource();
      ensureTracks();
      const file = frames[index].rgb[direction];
      if (!file) return;
      const url = new URL(base+'road/'+file, location.href).href;
      if (url === requested?.url) {
        if (resized) renderObservations();
        return;
      }
      requested = { index, direction, url };
      shown = undefined;
      renderObservations();
      rgb.src = url;
      const future = frames[index+1]?.rgb[direction];
      if (future) lookahead.src = base+'road/'+future;
    };

    const updatePose = (restartOrbit = false) => {
      const t = Number(time.value);
      const upcoming = frames.findIndex(frame => frame.time > t);
      const hi = upcoming === -1 ? path.length-1 : upcoming;
      const lo = Math.max(0, hi-1);
      const a = path[lo].pose, b = path[hi].pose;
      const blend = (t-frames[lo].time)/(frames[hi].time-frames[lo].time || 1);
      const sourceIndex = blend < .5 ? lo : hi;
      const position = lerpAxis(a, b, 3, blend);
      const forward = lerpAxis(a, b, 2, blend).normalize();
      const left = new THREE.Vector3().crossVectors(groundUp, forward).normalize();
      tireGaps = placeOnRoad(car, shadow, road, tireContacts, position, forward);
      const floor = road.heightAt(car.position.x, car.position.y);
      car.visible = mode === 'chase' || mode === 'orbit';
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
          camera.position.copy(position).addScaledVector(left, Number(offset.value)).addScaledVector(forward, -8.5);
          camera.position.z = floor+3.45+Number(lift.value);
          controls.target.copy(position).addScaledVector(forward, 1.8);
          controls.target.z = floor+.95;
        } else {
          if (!orbitAnchor || restartOrbit) {
            camera.position.copy(position).addScaledVector(left, 3.8+Number(offset.value))
              .addScaledVector(forward, -6.0);
            camera.position.z = floor+3.0+Number(lift.value);
            controls.target.copy(position).addScaledVector(forward, 2.7);
            controls.target.z = floor+.9;
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
      canvas.hidden = showRgb;
      sourceTime = frames[sourceIndex].time;
      showSource(showRgb || inset.checked, !showRgb && inset.checked, sourceIndex);
      if (unregistered !== fallbackRgb) {
        unregistered = fallbackRgb;
        updateNote();
      }
      readout.textContent = ko ? `${t.toFixed(1)}초` : `${t.toFixed(1)} s`;
    };

    const updateNote = () => {
      note.textContent = unregistered ? (ko ? '이 시점의 3D 카메라 자세를 복원하지 못해 실제 RGB를 표시합니다.' : 'Camera pose unavailable here. Showing the original RGB frame.')
        : mode === 'rgb' ? (ko ? 'KITScenes 실사 RGB입니다. 추적 ID는 선택한 카메라의 프레임 사이에서 이어집니다.' : 'Tracking IDs follow detections within the selected KITScenes camera.')
        : (ko ? 'Volvo 바퀴를 복원한 노면에 맞췄습니다. 실사 추적 창에서 주변 차량을 확인할 수 있습니다.' : 'The Volvo tires follow the reconstructed road. Open the RGB tracking inset to see surrounding traffic.');
    };
    const updateButtons = () => {
      for (const button of modes) button.setAttribute('aria-pressed', String(button.dataset.hqMode === mode));
      for (const button of directions) button.setAttribute('aria-pressed', String(button.dataset.hqCamera === direction));
      q('directions').hidden = mode !== 'calibrated' && mode !== 'rgb' && !inset.checked;
      q('inset-option').hidden = mode === 'rgb';
      q('track-option').hidden = !inset.checked && mode !== 'rgb' && !unregistered;
      q('route-option').hidden = mode === 'rgb';
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
    on(inset, 'change', () => { updatePose(); updateButtons(); });
    on(track, 'change', () => {
      if (trackError) trackRequest = undefined;
      ensureTracks();
      renderObservations();
    });
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
    releases.push(() => {
      source.hidden = true;
      boxes.replaceChildren();
      rgb.removeAttribute('src');
      lookahead.removeAttribute('src');
    });

    const resize = () => {
      if (!stage.clientWidth || !stage.clientHeight) return;
      camera.aspect = stage.clientWidth/stage.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(stage.clientWidth, stage.clientHeight);
      fitSource();
      if (!source.hidden) renderObservations();
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
      sourceTime, visibleTracks: source.hidden ? 0 : visibleTracks, tireGaps,
      vehicle: car.visible, routeVisible: route.visible,
      gaussians: road.manifest.scene_fit.gaussians,
    });
    releases.push(() => delete root.highresViewState);
    return release;
  } catch (error) {
    release();
    throw error;
  }
}
