import * as THREE from 'three';
import { dyno, SplatMesh } from '@sparkjsdev/spark';

async function readTexture(get, url) {
  let response;
  try {
    response = await get(url);
  } catch (error) {
    // Retry a transient connection reset without masking HTTP or abort errors.
    if (!(error instanceof TypeError)) throw error;
    await new Promise(resolve => setTimeout(resolve, 140));
    response = await get(url);
  }
  const image = await createImageBitmap(await response.blob(), {
    imageOrientation: 'flipY',
    premultiplyAlpha: 'none',
    colorSpaceConversion: 'none',
  });
  const texture = new THREE.Texture(image);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.flipY = false;
  texture.anisotropy = 8;
  texture.needsUpdate = true;
  return texture;
}

function disposeTexture(texture) {
  texture.dispose();
  texture.image.close();
}

function facadeMesh(corners, texture) {
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(corners.flat(), 3));
  geometry.setAttribute('uv', new THREE.Float32BufferAttribute([0,0, 1,0, 1,1, 0,1], 2));
  geometry.setIndex([0,1,2, 0,2,3]);
  return new THREE.Mesh(geometry, new THREE.MeshBasicMaterial({
    map: texture, side: THREE.DoubleSide, alphaTest: 0.53,
  }));
}

function skyMesh(texture) {
  const geometry = new THREE.SphereGeometry(1, 32, 20);
  const material = new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, depthTest: false,
    uniforms: { image: { value: texture } },
    vertexShader: `
      varying vec3 direction;
      void main() {
        direction = position;
        vec4 clip = projectionMatrix * vec4(mat3(viewMatrix) * position, 1.0);
        gl_Position = clip.xyww;
      }
    `,
    fragmentShader: `
      varying vec3 direction;
      uniform sampler2D image;
      void main() {
        vec3 ray = normalize(direction);
        vec2 uv = vec2(atan(ray.y, ray.x) / 6.283185307 + 0.5,
                      asin(clamp(ray.z, -1.0, 1.0)) / 3.141592654 + 0.5);
        gl_FragColor = texture2D(image, uv);
        #include <colorspace_fragment>
      }
    `,
  });
  const mesh = new THREE.Mesh(geometry, material);
  mesh.frustumCulled = false;
  mesh.renderOrder = -100;
  return mesh;
}

async function loadSurroundings(get, base, record) {
  const group = new THREE.Group();
  const jobs = [
    () => readTexture(get, base+record.sky.file).then(skyMesh),
    ...record.facades.map(wall => () => readTexture(get, base+wall.file)
      .then(texture => facadeMesh(wall.corners, texture))),
  ];
  const results = [];
  for (let offset = 0; offset < jobs.length; offset += 3) {
    results.push(...await Promise.allSettled(jobs.slice(offset, offset+3).map(load => load())));
    if (results.some(result => result.status === 'rejected')) break;
  }
  const failure = results.find(result => result.status === 'rejected');
  const meshes = results.filter(result => result.status === 'fulfilled').map(result => result.value);
  const dispose = () => {
    group.removeFromParent();
    for (const mesh of meshes) {
      disposeTexture(mesh.material.map ?? mesh.material.uniforms.image.value);
      mesh.geometry.dispose();
      mesh.material.dispose();
    }
  };
  if (failure) {
    dispose();
    throw failure.reason;
  }
  group.add(...meshes);
  group.visible = false;
  return { group, dispose };
}

function roadOpacityModifier(texture, manifest) {
  const type = { gsplat: dyno.Gsplat };
  const bounds = dyno.dynoVec4(new THREE.Vector4(...manifest.bounds_xy));
  const height = dyno.dynoVec4(new THREE.Vector4(...manifest.height_coefficients));
  const clearance = dyno.dynoVec2(new THREE.Vector2(...(manifest.road_clearance ?? [.16, .46])));
  const coverage = dyno.dynoSampler2D(texture);
  return dyno.dynoBlock(type, type, ({ gsplat }) => new dyno.Dyno({
    inTypes: { ...type, bounds: 'vec4', height: 'vec4', clearance: 'vec2', coverage: 'sampler2D' },
    outTypes: type,
    inputs: { gsplat, bounds, height, clearance, coverage },
    statements: ({ inputs, outputs }) => {
      const { gsplat, bounds, height, clearance, coverage } = inputs;
      const output = outputs.gsplat;
      return [
        `${output} = ${gsplat};`,
        `vec3 center = ${output}.center;`,
        `vec2 uv = (center.xy - ${bounds}.xy) / (${bounds}.zw - ${bounds}.xy);`,
        'if (all(greaterThan(uv, vec2(0.0))) && all(lessThan(uv, vec2(1.0)))) {',
        '  vec2 xy = center.xy / vec2(25.0, 10.0);',
        `  float roadZ = dot(${height}, vec4(1.0, xy, xy.x*xy.x));`,
        `  float covered = textureLod(${coverage}, uv, 0.0).a;`,
        `  float footprint = min(0.55, 1.5 * max(${output}.scales.x, max(${output}.scales.y, ${output}.scales.z)));`,
        `  float nearRoad = 1.0 - smoothstep(${clearance}.x + footprint, ${clearance}.y + footprint, abs(center.z - roadZ));`,
        `  ${output}.rgba.a *= 1.0 - nearRoad * smoothstep(0.58, 0.82, covered);`,
        '}',
      ];
    },
  }).outputs);
}

export async function loadRoadAtlas(get, base) {
  const manifest = await (await get(base + 'road/road.json')).json();
  if (manifest.schema !== 1) throw new Error('Unsupported road atlas');
  const texture = await readTexture(get, base + 'road/' + manifest.texture);

  const [left, bottom, right, top] = manifest.bounds_xy;
  const [offset, slopeX, slopeY, curveX] = manifest.height_coefficients;
  const height = (x, y) => offset + slopeX*x/25 + slopeY*y/10 + curveX*(x/25)**2;
  const columns = 96;
  const surfaceOffset = .015;
  const geometry = new THREE.PlaneGeometry(right-left, top-bottom, columns, 16);
  geometry.translate((left+right)/2, (bottom+top)/2, 0);
  const positions = geometry.getAttribute('position');
  for (let i = 0; i < positions.count; i++) {
    positions.setZ(i, height(positions.getX(i), positions.getY(i)) + surfaceOffset);
  }
  geometry.computeBoundingSphere();

  const material = new THREE.MeshBasicMaterial({
    map: texture, side: THREE.DoubleSide, alphaTest: 0.55,
    polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1,
  });
  const mesh = new THREE.Mesh(geometry, material);
  mesh.visible = false;
  return {
    mesh,
    manifest,
    heightAt(x, y) {
      // The mesh linearly interpolates curvature between its X grid columns.
      const column = THREE.MathUtils.clamp((x-left)/(right-left)*columns, 0, columns);
      const first = Math.floor(column);
      const spacing = (right-left)/columns;
      return surfaceOffset + THREE.MathUtils.lerp(
        height(left+first*spacing, y), height(left+Math.min(first+1, columns)*spacing, y),
        column-first,
      );
    },
    backgroundModifier: roadOpacityModifier(texture, manifest),
    async loadSurroundings() {
      return manifest.surroundings
        ? loadSurroundings(get, base+'road/', manifest.surroundings)
        : null;
    },
    async loadBackground() {
      const record = manifest.sky_filtered;
      const bytes = await (await get(base + 'road/' + record.file)).arrayBuffer();
      const digest = new Uint8Array(await crypto.subtle.digest('SHA-256', bytes));
      const hash = [...digest].map(x => x.toString(16).padStart(2, '0')).join('');
      if (bytes.byteLength !== record.bytes || hash !== record.sha256) {
        throw new Error('Background checksum mismatch');
      }
      const background = new SplatMesh({
        fileBytes: bytes, fileName: record.file, objectModifier: this.backgroundModifier,
      });
      try {
        await background.initialized;
        background.visible = false;
        return background;
      } catch (error) {
        background.dispose();
        throw error;
      }
    },
    dispose() {
      mesh.removeFromParent();
      geometry.dispose();
      material.dispose();
      disposeTexture(texture);
    },
  };
}
