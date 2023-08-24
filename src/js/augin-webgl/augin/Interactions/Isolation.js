import { Mesh } from "../../threejs/three.module.js";

export class Isolation {
    constructor(viewer) {
        this.viewer = viewer;
        this._active = false;
    }

    isActive() { return this._active; }
    #getColor() { return this.viewer.settings.materials.isolation.color; }
    #getOpacity() { return this.viewer.settings.materials.isolation.opacity; }

    apply() {
        if (this._active) return;
        if (!this.viewer.selection.hasSelectedObjects()) return;

        const material = this.viewer.renderer.materials.createIsolationMaterial(this.#getColor(), this.#getOpacity());
        this.viewer.clippingPlanes.applyClipPlanes(material);
        this.viewer.scene.traverse((node) => {
            if (node instanceof Mesh) {
                if (node.isInstancedMesh || node.name === "MergedMesh") {
                    node.material = material;
                }
            }
        });

        this._active = true;

        this.viewer.selection.showOutline(false);
        this.viewer.selection.showRender(true);
        this.viewer.camera.focusOnObject(this.viewer.selection.getFirstSelectedObject());
        this.viewer.render();
    }

    remove() {
        if (!this._active) return;

        this.viewer.scene.traverse((node) => {
            if (node instanceof Mesh) {
                if (node.isInstancedMesh || node.name === "MergedMesh") {
                    // const useAlpha = node.geometry.attributes['color'].itemSize === 4;
                    const useAlpha = false;
                    node.material = this.viewer.renderer.materials.getMaterial(useAlpha);
                }
            }
        });

        this._active = false;

        this.viewer.selection.showOutline(true);
        this.viewer.selection.showRender(false);
        this.viewer.render();
    }

    update(currentMeshes) {
        this.viewer.camera.focusOnObject(currentMeshes);
        this.viewer.render();
    }
}