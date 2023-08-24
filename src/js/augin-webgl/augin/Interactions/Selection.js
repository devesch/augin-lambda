import { Box3, Color, EventDispatcher, Group, Matrix4, Mesh, Object3D } from "../../threejs/three.module.js";
import { Data } from "../MeshBuilder/Data.js";
import { EventHelper } from "../Helpers/EventHelper.js";
import { ObjectUtils } from "../Utils/ObjectUtils.js";

export class Selection {
    constructor(viewer) {
        this._viewer = viewer;

        this.selectObjects = [];
        this.layer = 2;
        this._groupObject;
        this._currentGuid = "";
        this._currentMeshes;
        this.currentBoundingBox;
        this._isInstaceMesh = false;
        this.instanceMesh;
        this._showing = false;
        this._showRender = false;
        viewer.clippingPlanes.onChangeValue.addEventListener(EventHelper.CHANGED_VALUE_NAME, this.#clippingPlanesChanged);

        this.onSelectIntersectEvent = new EventDispatcher();

        viewer.camera.enableLayer(this.layer);
    }

    get aug() {
        return this._viewer.aug;
    }

    addSelectEvent(event) {
        this.onSelectIntersectEvent.addEventListener("select_object", event);
    }

    addDeselectEvent(event) {
        this.onSelectIntersectEvent.addEventListener("deselect_object", event);
    }

    hasSelectedObjects() { return this.selectObjects !== undefined && this.selectObjects.length > 0; }

    getFirstSelectedObject() { return this.hasSelectedObjects() ? this.selectObjects[0] : void 0; }

    byIntersect(intersect) {
        if (intersect === undefined) return;

        let elementIndex = -1;
        if (intersect.instanceId !== undefined) {
            elementIndex = Data.getInstanceMesh(intersect.object.meshId, intersect.instanceId);
        }
        else {
            elementIndex = Data.getMergeMesh(intersect.faceIndex);
        }
        const element = this.aug.getElement(elementIndex);
        if (element === undefined) return;
        this.#applySelection(element);

        if (this.onSelectIntersectEvent === void 0) return;
        this.onSelectIntersectEvent.dispatchEvent({ type: "select_object", guid: this._currentGuid });
    }

    byGuid(guid) {
        if (guid === undefined) return false;

        const element = this.aug.getElementByGuid(guid);
        if (element === undefined) return false;
        this.#applySelection(element);
        return true;
    }

    deselect() {
        this.#removeCurrent();
        this._viewer.render();

        if (this.onSelectIntersectEvent === void 0) return;
        this.onSelectIntersectEvent.dispatchEvent({ type: "deselect_object" });
    }

    showRender(value) {
        this._showRender = value;
        this.selectObjects.forEach(object => {
            for (const mesh of object.children) {
                mesh.material = this.#changeMaterial(mesh.material);
            }
        });
    }

    showOutline(value) {
        if (this.hasSelectedObjects()) {
            if (value) {
                this._viewer.renderer.renderComposer.addOutlinePass(this._groupObject);
            }
            else {
                this._viewer.renderer.renderComposer.removeOutlinePass(this._groupObject);
            }
        }
        this._showing = value;
    }

    #applySelection(element) {
        if (this._currentGuid === element.guid) return;

        this.#reset();

        this._currentGuid = element.guid;

        const mesh = this.aug.createElementMesh(element);
        mesh.layers.set(this.layer);
        this._groupObject.add(mesh);
        this.selectObjects.push(mesh);

        this._viewer.scene.add(this._groupObject);

        this.currentBoundingBox = new Box3().setFromObject(this._groupObject);

        if (this._viewer.clippingPlanes !== void 0)
        {
            const inside = this.checkInsideOfClippingPlane(this._viewer, this._viewer.clippingPlanes.clippingPlaneBoundBox);
            this.showOutline(inside);
        }

        this._viewer.render();
    }

    #getMaterial(material) {
        material.depthTest = false;
        material = this.#changeMaterial(material);
        return material;
    }

    #changeMaterial(material) {
        material.transparent = !this._showRender;
        material.opacity = this._showRender ? 1 : 0;
        return material;
    }

    #reset() {
        this.#removeCurrent();
        this.selectObjects = [];
        this._groupObject = new Group();
    }

    #removeCurrent() {
        if (this.hasSelectedObjects()) {
            this._viewer.scene.remove(this._groupObject);

            this.selectObjects.forEach(object => {
                for (const mesh of object.children) {
                    mesh.geometry.dispose();
                    mesh.material.dispose();
                }
            });
            this.selectObjects.length = 0;

            this._groupObject = this.currentBoundingBox = void 0;
            this._currentGuid = "";
        }
    }

    #clippingPlanesChanged(event) {
        const viewer = event.viewer;
        const clippingPlaneBoundBox = event.clippingPlaneBoundBox;

        const selection = viewer.selection;

        const inside = viewer.selection.checkInsideOfClippingPlane(viewer, clippingPlaneBoundBox);
        if (inside) {
            if (!selection.showing) {
                viewer.renderer.renderComposer.addOutlinePass(selection._groupObject);
                selection.showing = true;
            }
        }
        else {
            if (selection.showing) {
                viewer.renderer.renderComposer.removeOutlinePass(selection._groupObject);
                selection.showing = false;
            }
        }
    }

    checkInsideOfClippingPlane(viewer, clippingPlaneBoundBox)
    {
        if (viewer.isolation.isActive()) return;

        const selection = viewer.selection;

        const currentBoundingBox = selection.currentBoundingBox;
        if (currentBoundingBox === undefined) return;

        return ObjectUtils.boxWholeInside(currentBoundingBox, clippingPlaneBoundBox);
    }
}