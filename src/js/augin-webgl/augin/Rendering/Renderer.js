import { Clock, Vector2, WebGLRenderer, PCFSoftShadowMap, ACESFilmicToneMapping } from "../../threejs/three.module.js";
// import WebGPU from '../../threejs/jsm/capabilities/WebGPU.js';
// import WebGPURenderer from '../../threejs/jsm/renderers/webgpu/WebGPURenderer.js';
import { AugMaterials } from "./AugMaterials.js";
import { RenderComposer } from "./RenderComposer.js";
import { Text2DRenderer } from "./Text2DRenderer.js";

export class Renderer {
    constructor(viewer) {
        // if ( WebGPU.isAvailable() ) {
        //     this.renderer = new WebGPURenderer();
        // }
        // else
        // {
        //     this.renderer = new WebGLRenderer( {
        //         powerPreference: "high-performance",
        //         precision: "highp",
        //         antialias: true,
        //         stencil: false,
        //         logarithmicDepthBuffer: true
        //     });
        // }

        this.renderer = new WebGLRenderer({
            powerPreference: "high-performance",
            precision: "highp",
            antialias: true,
            stencil: false,
            logarithmicDepthBuffer: true
        });

        this.materials = new AugMaterials(viewer);

        this.container = document.createElement('div');
        document.body.appendChild(this.container);

        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.toneMappingExposure = 1;

        const rendererCanvas = this.renderer.domElement;
        this.container.appendChild(rendererCanvas);
        this.container.addEventListener('resize', () => this.onWindowResize());

        this.clock = new Clock();

        this.viewer = viewer;

        this.text2DRenderer = void 0;

        this.needsUpdate = false;
        this.getMaxResolution();

        this._currentSize = this.getMaxSupportedSize();
    }

    get camera () {
        return this.viewer.camera;
    }

    get textEnabled() {
        return this._renderText;
    }

    set textEnabled(value) {
        if (value === this._renderText)
            return;

        this.needsUpdate = true;
        this._renderText = value;
        this.text2DRenderer.text.style.display = value ? "block" : "none";
    }

    createTextRenderer() {
        this.text2DRenderer = new Text2DRenderer(this.viewer, this.container);
        this._renderText = void 0;
        this.textEnabled = false;
    }

    initRender() {
        this.renderComposer = new RenderComposer(this.viewer, this, this.container);
    }

    addEventListener(type, listener) {
        this.container.addEventListener(type, listener);
    }

    onWindowResize() {
        this.setSize();

        this.needsUpdate = true;
    }

    getSize() {
        return new Vector2(this.container.clientWidth, this.container.clientHeight);
    }

    getMaxSupportedSize() {
        const clampedWidth = Math.min(this.container.clientWidth, this.maxResolution);
        const clampedHeight = Math.min(this.container.clientHeight, this.maxResolution);
        return new Vector2(clampedWidth, clampedHeight);
    }

    getMaxResolution() {
        const canvas = document.createElement('canvas');
        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
        if (!gl) {
            canvas.remove();
            // WebGL is not supported, return a fallback value
            return 2048; // Choose a suitable fallback resolution
        }
        const maxTextureSize = gl.getParameter(gl.MAX_TEXTURE_SIZE);
        const maxViewportDims = gl.getParameter(gl.MAX_VIEWPORT_DIMS);
        const maxWidth = Math.min(maxTextureSize, maxViewportDims[0]);
        const maxHeight = Math.min(maxTextureSize, maxViewportDims[1]);
        this.maxResolution = Math.min(maxWidth, maxHeight);
        canvas.remove();
    }

    setSize() {
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderComposer.setSize();
        this.camera.updateAspect();
    }

    getBoundingClientRect() {
        return this.renderer.domElement.getBoundingClientRect()
    }

    getParentSize() {
        const parentElement = this.container.parentElement;
        const parentWidth = parentElement ? parentElement.clientWidth : void 0;
        const parentHeight = parentElement ? parentElement.clientHeight : void 0;

        return new Vector2(
            parentWidth !== null ? parentWidth : this.container.clientWidth,
            parentHeight !== null ? parentHeight : this.container.clientHeight
        );
    }

    getAspectRatio() {
        const size = this.getParentSize();
        return size.x / size.y;
    }

    update() {
        const parentSize = this.getParentSize();
        const changeSize = this._currentSize.x !== parentSize.x || this._currentSize.y !== parentSize.y;
        if (changeSize) {
            this.onWindowResize();
            this._currentSize = parentSize;
        }

        return this.camera.update(this.clock.getDelta()) || changeSize;
    }

    render() {
        if (this.renderComposer === void 0) return;

        // this.renderer.render(this.viewer.scene, this.viewer.camera.camera);
        this.renderComposer.render();
        if (this.textEnabled) {
            this.text2DRenderer.render();
        }
        this.needsUpdate = false;
    }
}