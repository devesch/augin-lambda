import { DoubleSide, MeshBasicMaterial, Mesh, SphereGeometry, Vector3 } from "../../threejs/three.module.js";
import { AugUtils } from "../Utils/AugUtils.js";
import { GizmoUtils } from "../Utils/GizmoUtils.js";

export class MeasurePoint {
    constructor(viewer) {
        this.viewer = viewer;
        this.mesh = void 0;
        this.position = new Vector3();
    }

    get isSet() {
        return this.mesh !== void 0;
    }

    get projectCenter() {
        return AugUtils.projectCenter(this.viewer.aug);
    }

    get pointDistance() {
        return this.viewer.camera.position.clone().distanceTo(this.position);
    }

    #getColor() { return this.viewer.settings.materials.measure.sphere.color; }
    #getSize() { return this.viewer.settings.materials.measure.sphere.size; }

    setPoint(point) {
        const geometry = new SphereGeometry(this.#getSize());

        const material = new MeshBasicMaterial({ color: this.#getColor(), side: DoubleSide });
        material.depthTest = false;
        this.mesh = new Mesh(geometry, material);
        this.mesh.renderOrder = 1;
        this.mesh.layers.set(this.viewer.measure.layer);

        const scaleVector = new Vector3();
        const scope = this;
        this.mesh.updateMatrixWorld = function (force) {
            scaleVector.set(scope.pointDistance / 100, scope.pointDistance / 100, scope.pointDistance / 100);
            scope.mesh.scale.copy(scaleVector);
            GizmoUtils.updateMatrixWorld(this, force);
        }

        this.viewer.scene.add(this.mesh);

        this.position = new Vector3().addVectors(new Vector3(point.x, point.y, point.z), this.projectCenter);
        this.mesh.position.copy(this.position);

        this.viewer.render();
    }

    remove() {
        if (this.mesh == null) return;

        this.viewer.scene.remove(this.mesh);

        if (this.mesh.material) {
            if (Array.isArray(this.mesh.material)) {
                for (const material of this.mesh.material) {
                    material.dispose();
                }
            } else {
                this.mesh.material.dispose();
            }
        }

        // Dispose the geometry
        if (this.mesh.geometry) {
            this.mesh.geometry.dispose();
        }

        this.mesh = void 0;
        this.position = new Vector3();

        this.viewer.render();
    }
}