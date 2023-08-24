import { Scene, EventDispatcher } from "../threejs/three.module.js";
import { AugLoader } from './Aug/Aug.js';
import { Settings } from './Settings.js';
import { Raycast } from './Interactions/Raycast.js';
import { Selection } from "./Interactions/Selection.js";
import { ClippingPlanes } from "./Interactions/ClippingPlanes.js";
import { Isolation } from "./Interactions/Isolation.js";
import { Renderer } from "./Rendering/Renderer.js";
import { Background } from "./Rendering/Background.js";
import { Environment } from './Rendering/Enviroment.js';
import { Camera } from "./Camera.js";
import { Input } from "./Inputs/Input.js";
import { Measure } from "./Interactions/Measure.js";
import { Stats } from "./Helpers/Stats.js";

export class Viewer {
    constructor() {
        this.settings = new Settings();
        this.scene = new Scene();
        this.renderer = new Renderer(this);
        this.camera = new Camera(this);
        this.raycast = new Raycast(this);

        this.renderer.createTextRenderer();

        this.clippingPlanes = new ClippingPlanes(this);
        this.selection = new Selection(this);
        this.isolation = new Isolation(this);
        this.measure = new Measure(this);
        this.input = new Input(this);
        this.stats = new Stats();
        this.aug = null;
        this.eventDispatcher = new EventDispatcher();
    }

    addFpsLowEvent(onLowFpsEvent = void 0) {
        if (onLowFpsEvent !== void 0)
            this.eventDispatcher.addEventListener("low_fps", onLowFpsEvent);
        this.onLowFpsEvent = onLowFpsEvent;
    }

    async init(url, id = void 0, onLoadedEvent = void 0, onProgressEvent = void 0) {
        if (onLoadedEvent !== void 0)
            this.eventDispatcher.addEventListener("load_aug", onLoadedEvent);
        if (onProgressEvent !== void 0)
            this.eventDispatcher.addEventListener("progress_aug", onProgressEvent);

        document.body.appendChild(this.stats.dom);

        const background = await new Background(this.getRenderer(), this.settings);
        this.scene.background = background;
        this.renderer.initRender();
        this.render();

        let startTime = performance.now();

        let augLoader = new AugLoader();
        augLoader.setRenderer(this.renderer);
        augLoader.load(url, id, (augScene) => {

            this.aug = augLoader;

            this.scene = augScene;
            this.scene.background = background;
            this.scene.environment = background;

            const centerPivot = this.aug.applyCenter();
            this.scene.position.set(-centerPivot.x, -centerPivot.y, -centerPivot.z);

            const environment = new Environment(Settings.defaultSettings);
            environment.getObjects().forEach((o) => this.scene.add(o));
            environment.applySkylightPosition(centerPivot);
            environment.adaptGroundToContent(augLoader.getOriginalBoundingBox());
            this.scene.environment = environment;

            this.camera.initialize(augLoader.getBoundingBox());

            this.clippingPlanes.init(augLoader);

            this.renderer.initRender();

            this.input.register();

            update();

            let endTime = performance.now();

            if (onLoadedEvent !== void 0)
                this.eventDispatcher.dispatchEvent({ type: "load_aug", loadedTimeMs: endTime - startTime });
        }, (downloadProgress) => {
            if (onProgressEvent !== void 0)
                this.eventDispatcher.dispatchEvent({ type: "progress_aug", progressType: 'download', progress: downloadProgress });
        }, (loadProgress) => {
            if (onProgressEvent !== void 0)
                this.eventDispatcher.dispatchEvent({ type: "progress_aug", progressType: 'load', progress: loadProgress });
        }, null);

        const scope = this;

        let frameCount = 0;
        let lastTime = Date.now();
        let fps = 0;
        let lowFps = this.settings.quality.maximumLowFps;
        let currentSecondsInLowFps = 0;
        let secondsInLowFps = this.settings.quality.secondsInLowFps;
        let warningLowFps = false;
        let holdCountFps = false;

        function update() {
            if (scope.onLowFpsEvent !== void 0)
            {
                if (holdCountFps) return;

                frameCount++;

                let currentTime = Date.now();

                if (currentTime - lastTime >= 1000) {
                    fps = frameCount;
                    frameCount = 0;
                    lastTime = currentTime;

                    if (fps < lowFps) {
                        currentSecondsInLowFps++;
                        if (currentSecondsInLowFps > secondsInLowFps) {
                            if (!warningLowFps) {
                                scope.eventDispatcher.dispatchEvent({ type: "low_fps" });
                                warningLowFps = true;
                            }
                        }
                    }
                    else {
                        currentSecondsInLowFps = 0;
                    }
                }
            }

            requestAnimationFrame(update);

            const needsUpdate = scope.renderer.update() || scope.renderer.needsUpdate;

            if (needsUpdate)
                scope.render();
            if (scope.settings.showStats)
                scope.stats.update();
        }

        document.addEventListener("visibilitychange", () => {
            if (document.visibilityState === "visible") {
                lastTime = Date.now();
                holdCountFps = false;
            } else {
                frameCount = 0;
                currentSecondsInLowFps = 0;
                holdCountFps = true;
            }
        });
    }

    render() {
        this.renderer.render();
    }

    getRenderer() {
        return this.renderer.renderer;
    }

    getCamera() {
        return this.camera.camera;
    }

    getContainer() {
        return this.renderer.container;
    }
}