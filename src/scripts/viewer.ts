// A KILN .glb in the browser, the way a game shows it: the real file, its rig and its animations, lit by the
// style's look kit (sky and ground light, sun, tonemapper, toon bands and outlines). Drag to turn it.
// One viewer per section: models and styles switch in place (browsers cap WebGL contexts).

import {
  ACESFilmicToneMapping,
  AgXToneMapping,
  AnimationMixer,
  Box3,
  Color,
  DataTexture,
  DirectionalLight,
  HemisphereLight,
  LoopRepeat,
  Mesh,
  MeshStandardMaterial,
  MeshToonMaterial,
  NearestFilter,
  NoToneMapping,
  PCFSoftShadowMap,
  PerspectiveCamera,
  PlaneGeometry,
  RedFormat,
  Scene,
  ShadowMaterial,
  Timer,
  Vector3,
  WebGLRenderer,
  type AnimationAction,
  type AnimationClip,
  type Object3D,
  type ToneMapping,
} from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { OutlineEffect } from "three/examples/jsm/effects/OutlineEffect.js";
import { clone } from "three/examples/jsm/utils/SkeletonUtils.js";

export interface Look {
  shader: string;
  toon_bands: number;
  outline: number;
  outline_color: string;
  tonemapper: string;
  exposure: number;
  saturation: number;
  contrast: number;
  ambient: number;
  sky_top: string;
  sky_horizon: string;
  ground: string;
  sun_pitch: number;
  sun_yaw: number;
  sun_energy: number;
  sun_color: string;
  shadows: boolean;
}

const TONEMAPPERS: Record<string, ToneMapping> = {
  linear: NoToneMapping,
  filmic: ACESFilmicToneMapping,
  aces: ACESFilmicToneMapping,
  agx: AgXToneMapping,
};

const loader = new GLTFLoader();
const cache = new Map<string, Promise<{ scene: Object3D; animations: AnimationClip[] }>>();

export const base = () => document.documentElement.dataset.base ?? "/";
export const reducedMotion = () => matchMedia("(prefers-reduced-motion: reduce)").matches;

function load(url: string) {
  if (!cache.has(url)) cache.set(url, loader.loadAsync(url));
  return cache.get(url)!;
}

function bands(n: number): DataTexture {
  const data = new Uint8Array(n);
  for (let i = 0; i < n; i++) data[i] = Math.round(60 + (195 * i) / Math.max(1, n - 1));
  const tex = new DataTexture(data, n, 1, RedFormat);
  tex.minFilter = tex.magFilter = NearestFilter;
  tex.needsUpdate = true;
  return tex;
}

export class Viewer {
  readonly renderer: WebGLRenderer;
  readonly scene = new Scene();
  readonly camera = new PerspectiveCamera(28, 1, 0.05, 100);
  readonly controls: OrbitControls;
  private outline: OutlineEffect;
  private hemi = new HemisphereLight();
  private sun = new DirectionalLight();
  private floor = new Mesh(new PlaneGeometry(40, 40), new ShadowMaterial({ opacity: 0.22 }));
  private timer = new Timer();
  private mixer: AnimationMixer | null = null;
  private clips: AnimationClip[] = [];
  private action: AnimationAction | null = null;
  private model: Object3D | null = null;
  private look: Look | null = null;
  private visible = false;
  private request = 0;
  playing = !reducedMotion();
  onClips: (names: string[]) => void = () => {};

  constructor(private host: HTMLElement) {
    this.renderer = new WebGLRenderer({ antialias: true, alpha: true });
    this.renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = PCFSoftShadowMap;
    host.prepend(this.renderer.domElement);
    this.outline = new OutlineEffect(this.renderer);
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.renderer.domElement.style.touchAction = "pan-y"; // vertical swipes still scroll the page
    this.controls.enableZoom = false;
    this.controls.enablePan = false;
    this.controls.enableDamping = true;
    this.controls.autoRotate = this.playing;
    this.controls.autoRotateSpeed = 1.6;
    this.controls.minPolarAngle = 0.35;
    this.controls.maxPolarAngle = 1.62;
    this.controls.addEventListener("start", () => (this.controls.autoRotate = false));
    this.floor.rotation.x = -Math.PI / 2;
    this.floor.receiveShadow = true;
    this.sun.castShadow = true;
    this.sun.shadow.mapSize.set(1024, 1024);
    this.sun.shadow.radius = 4;
    this.scene.add(this.hemi, this.sun, this.sun.target, this.floor);
    new ResizeObserver(() => this.resize()).observe(host);
    new IntersectionObserver(([e]) => {
      this.visible = e.isIntersecting;
      if (this.visible) this.loop();
    }).observe(host);
    this.resize();
  }

  private resize() {
    const w = this.host.clientWidth;
    const h = this.host.clientHeight;
    if (!w || !h) return;
    this.renderer.setSize(w, h, false);
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
    this.draw();
  }

  /** Show `url` with `look`; `anim` (a KILN animation name) plays if present, else the first loop. */
  async show(url: string, look: Look, anim?: string) {
    const ticket = ++this.request;
    const gltf = await load(url);
    if (ticket !== this.request) return;
    if (this.model) this.scene.remove(this.model);
    this.mixer?.stopAllAction();
    const model = clone(gltf.scene);
    this.model = model;
    this.scene.add(model);
    this.applyLook(look);
    this.frame(model);
    this.mixer = new AnimationMixer(model);
    this.clips = gltf.animations;
    const names = this.clips.map((c) => c.name.replace(/-loop$/, ""));
    this.onClips(names);
    this.play(anim && names.includes(anim) ? anim : names[0]);
    this.draw();
  }

  play(name?: string) {
    this.action?.stop();
    this.action = null;
    const clip = this.clips.find((c) => c.name.replace(/-loop$/, "") === name);
    if (!clip || !this.mixer) return;
    this.action = this.mixer.clipAction(clip).setLoop(LoopRepeat, Infinity).play();
    this.loop();
  }

  setPlaying(on: boolean) {
    this.playing = on;
    this.controls.autoRotate = on;
    this.loop();
  }

  applyLook(look: Look) {
    this.look = look;
    const r = this.renderer;
    r.toneMapping = TONEMAPPERS[look.tonemapper] ?? ACESFilmicToneMapping;
    r.toneMappingExposure = look.exposure;
    r.domElement.style.filter = `saturate(${look.saturation}) contrast(${look.contrast})`;
    this.host.style.background = `linear-gradient(${look.sky_top}, ${look.sky_horizon} 62%, ${look.ground} 62.2%, ${look.ground})`;
    const toon = look.shader === "toon";
    this.hemi.color.set(look.sky_horizon);
    this.hemi.groundColor.set(look.ground);
    this.hemi.intensity = look.ambient * (toon ? 1.2 : 1.5);
    this.sun.color.set(look.sun_color);
    this.sun.intensity = look.sun_energy * (toon ? 2.2 : 2.6);
    this.sun.castShadow = look.shadows;
    const p = (look.sun_pitch * Math.PI) / 180;
    const y = (look.sun_yaw * Math.PI) / 180;
    this.sun.position.set(Math.cos(p) * Math.sin(y), -Math.sin(p), Math.cos(p) * Math.cos(y)).multiplyScalar(8);
    const gradient = toon ? bands(look.toon_bands) : null;
    this.model?.traverse((o: any) => {
      if (!o.isMesh) return;
      o.castShadow = true;
      const src: MeshStandardMaterial = o.userData.original ?? o.material;
      o.userData.original = src;
      if (toon) {
        const m = new MeshToonMaterial({ color: src.color, map: src.map, emissive: src.emissive, gradientMap: gradient });
        m.userData.outlineParameters = { thickness: 0.0045, color: new Color(look.outline_color).toArray(), visible: look.outline > 0 };
        o.material = m;
      } else {
        o.material = src;
      }
    });
    this.draw();
  }

  private frame(model: Object3D) {
    const box = new Box3().setFromObject(model);
    const size = box.getSize(new Vector3());
    const centre = box.getCenter(new Vector3());
    const radius = size.length() * 0.48; // the bounding sphere, a little tight: corners rarely all face the camera
    const dist = radius / Math.sin(((this.camera.fov / 2) * Math.PI) / 180);
    this.controls.target.copy(centre);
    this.camera.position.copy(centre).add(new Vector3(0.45, 0.32, 1).normalize().multiplyScalar(dist));
    this.camera.near = dist / 20;
    this.camera.far = dist * 6;
    this.camera.updateProjectionMatrix();
    const s = this.sun.shadow.camera;
    const r = Math.max(size.x, size.y, size.z) * 1.2;
    s.left = s.bottom = -r;
    s.right = s.top = r;
    s.near = 0.1;
    s.far = 30;
    s.updateProjectionMatrix();
    this.sun.target.position.copy(centre);
    this.controls.update();
  }

  private draw() {
    if (!this.look) return;
    if (this.look.shader === "toon" && this.look.outline > 0) this.outline.render(this.scene, this.camera);
    else this.renderer.render(this.scene, this.camera);
  }

  private running = false;
  private loop() {
    if (this.running) return;
    this.running = true;
    this.timer.update();
    const tick = (t: number) => {
      if (!this.visible) {
        this.running = false;
        return;
      }
      this.timer.update(t);
      if (this.playing) this.mixer?.update(Math.min(this.timer.getDelta(), 0.1));
      this.controls.update();
      this.draw();
      requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }
}
