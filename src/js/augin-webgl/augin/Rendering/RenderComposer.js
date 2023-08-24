import { Vector2, WebGLRenderTarget } from "../../threejs/three.module.js";
import { EffectComposer } from '../../threejs/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from '../../threejs/jsm/postprocessing/RenderPass.js';
import { OutlinePass } from '../../threejs/jsm/postprocessing/OutlinePass.js';
import { ShaderPass } from '../../threejs/jsm/postprocessing/ShaderPass.js';
import { FXAAShader } from '../../threejs/jsm/shaders/FXAAShader.js';
import { Settings } from "../Settings.js";

export class RenderComposer {
    constructor(viewer, renderer, container) {
        const size = renderer.getMaxSupportedSize();
        var renderTarget = new WebGLRenderTarget(size.x, size.y);
        renderTarget.texture.name = 'EffectComposer.rt1';

        this.composer = new EffectComposer(renderer.renderer, renderTarget);

        const renderPass = new RenderPass(viewer.scene, viewer.getCamera());
        this.composer.addPass(renderPass);

        this.outlinePass = new OutlinePass(new Vector2(size.x, size.y), viewer.scene, viewer.getCamera());
        this.outlinePass.visibleEdgeColor = Settings.defaultSettings.materials.outline.color;
        this.outlinePass.hiddenEdgeColor = Settings.defaultSettings.materials.outline.color;
        this.outlinePass.edgeStrength = Settings.defaultSettings.materials.outline.intensity;
        this.outlinePass.edgeThickness = Settings.defaultSettings.materials.outline.blur;
        this.composer.addPass(this.outlinePass);

        this.effectFXAA = new ShaderPass(FXAAShader);
        this.effectFXAA.renderToScreen = true;
        this.composer.addPass(this.effectFXAA);

        this.renderer = renderer;
        this.container = container;

        this.setSize();
    }

    setSize() {
        const size = this.renderer.getMaxSupportedSize();
        this.composer.setSize(size.x, size.y);
        this.effectFXAA.uniforms['resolution'].value.set(1 / size.x, 1 / size.y);
    }

    render() {
        this.composer.render();
    }

    clearOutlinePass() {
        this.outlinePass.selectedObjects = [];
    }

    addOutlinePass(selectedObject) {
        if (!this.outlinePass.selectedObjects.includes(selectedObject)) {
            this.outlinePass.selectedObjects.push(selectedObject);
        }
    }

    removeOutlinePass(selectedObject) {
        this.outlinePass.selectedObjects = this.outlinePass.selectedObjects.filter(item => item !== selectedObject);
    }

}