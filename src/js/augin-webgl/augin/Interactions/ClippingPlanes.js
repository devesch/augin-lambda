import { EventDispatcher, Plane, Group, PlaneGeometry, MeshBasicMaterial, DoubleSide, Mesh, Vector3, Box3 } from "../../threejs/three.module.js";
import { EventHelper } from "../Helpers/EventHelper.js";

export class ClippingPlanes {
    constructor(viewer) {
        this.params = {
            clipIntersection: true,
            planeConstant: 1,
            showClipping: false
        };
        this.clipPlanes = [];
        this.visualizePlanes = [];
        this.viewer = viewer;
        this.center = new Vector3();
        this.size = new Vector3();
        this.bbMin = new Vector3();
        this.bbMax = new Vector3();
        this.layer = 31;
        this.clippingPlaneBoundBox = new Box3();
        this.onChangeValue = new EventDispatcher();
    }

    init(aug) {
        this.aug = aug;
        // Get the center of the bounding box
        this.aug.getOriginalBoundingBox().getCenter(this.center);
        this.aug.getOriginalBoundingBox().getSize(this.size);
        this.bbMin = this.aug.getOriginalBoundingBox().min;
        this.bbMax = this.aug.getOriginalBoundingBox().max;

        this.viewer.camera.enableLayer(this.layer);

        this.clipPlanes = this.#createClippingPlanesFromBoundingBox();

        const visualizePlanes = this.#createVisualizePlanes();
        this.viewer.scene.add(visualizePlanes);
        visualizePlanes.visible = this.params.showClipping;

        this.viewer.renderer.materials.setClipPlanes(this.clipPlanes);
        this.viewer.getRenderer().localClippingEnabled = true;
    }

    applyClipPlanes(material) {
        material.clippingPlanes = this.clipPlanes;
    }

    reset() {
        if (this.clipPlanes === undefined) return;

        this.changeClipPlane(0, 1);
        this.changeClipPlane(1, 1);
        this.changeClipPlane(2, 1);
        this.changeClipPlane(3, 1);
        this.changeClipPlane(4, 1);
        this.changeClipPlane(5, 1);
    }

    #createClippingPlanesFromBoundingBox() {
        const planes = [];
        const normals = [
            new Vector3(-1, 0, 0),
            new Vector3(1, 0, 0),
            new Vector3(0, -1, 0),
            new Vector3(0, 1, 0),
            new Vector3(0, 0, -1),
            new Vector3(0, 0, 1)
        ];

        for (let i = 0; i < 6; i++) {
            const plane = new Plane(normals[i], this.params.planeConstant);
            planes.push(plane);
        }

        return planes;
    }

    changeClipPlane(index, value) {
        const bbMin = this.bbMin;
        const bbMax = this.bbMax;
        const center = this.center;
        const clipPlane = this.clipPlanes[index];
        clipPlane.constant = value;
        if (index == 0) {
            this.clippingPlaneBoundBox.max.x = (bbMax.x - center.x) * value;
            clipPlane.translate(new Vector3((bbMax.x - center.x) * value, 0, 0));
        }
        if (index == 1) {
            this.clippingPlaneBoundBox.min.x = (bbMin.x - center.x) * value;
            clipPlane.translate(new Vector3((bbMin.x - center.x) * value, 0, 0));
        }
        if (index == 2) {
            this.clippingPlaneBoundBox.max.y = (bbMax.y - center.y) * value;
            clipPlane.translate(new Vector3(0, (bbMax.y - center.y) * value, 0));
        }
        if (index == 3) {
            this.clippingPlaneBoundBox.min.y = (bbMin.y - center.y) * value;
            clipPlane.translate(new Vector3(0, (bbMin.y - center.y) * value, 0));
        }
        if (index == 4) {
            this.clippingPlaneBoundBox.max.z = (bbMax.z - center.z) * value;
            clipPlane.translate(new Vector3(0, 0, (bbMax.z - center.z) * value));
        }
        if (index == 5) {
            this.clippingPlaneBoundBox.min.z = (bbMin.z - center.z) * value;
            clipPlane.translate(new Vector3(0, 0, (bbMin.z - center.z) * value));
        }

        if (this.onChangeValue != null)
            this.onChangeValue.dispatchEvent({ type: EventHelper.CHANGED_VALUE_NAME, viewer: this.viewer, clippingPlaneBoundBox: this.clippingPlaneBoundBox });

        this.#updateVisualizePlane(index);
        this.viewer.render();
    }

    #createVisualizePlanes() {
        // Now calculate the size of the bounding box
        const size = new Vector3();
        this.aug.getOriginalBoundingBox().getSize(size);

        const material = new MeshBasicMaterial({ color: 0xffff00, side: DoubleSide, opacity: 0.25, transparent: true });

        const margin = 2;

        const group = new Group();
        // Create six planes for each side of the bounding box
        for (let i = 0; i < 6; i++) {
            let planeGeometry;
            if (i < 2) {
                // The two planes in X direction
                planeGeometry = new PlaneGeometry(size.z + margin, size.y + margin);
            } else if (i < 4) {
                // The two planes in Y direction
                planeGeometry = new PlaneGeometry(size.x + margin, size.z + margin);
            } else {
                // The two planes in Z direction
                planeGeometry = new PlaneGeometry(size.y + margin, size.x + margin);
            }

            // Create the mesh
            const visualizePlane = new Mesh(planeGeometry, material);

            visualizePlane.rotation[(i < 2 ? 'y' : i < 4 ? 'x' : 'z')] = i % 2 === 0 ? Math.PI / 2 : -Math.PI / 2;

            visualizePlane.layers.set(this.layer);
            this.visualizePlanes.push(visualizePlane);
            group.add(visualizePlane);

            this.changeClipPlane(i, this.params.planeConstant);
        }

        group.layers.set(this.layer);

        return group;
    }

    #updateVisualizePlane(index) {
        const visualizePlane = this.visualizePlanes[index];
        visualizePlane.position.copy(this.clipPlanes[index].normal).multiplyScalar(-this.clipPlanes[index].constant).add(this.center);
    }

    showPlanes(value) {
        visualizePlanes.visible = value;
        this.viewer.render();

    }

    insideClippingPlane(point) {
        if (point.x < this.clippingPlaneBoundBox.min.x || point.x > this.clippingPlaneBoundBox.max.x) return false;
        if (point.y < this.clippingPlaneBoundBox.min.y || point.y > this.clippingPlaneBoundBox.max.y) return false;
        if (point.z < this.clippingPlaneBoundBox.min.z || point.z > this.clippingPlaneBoundBox.max.z) return false;

        return true;
    }
}