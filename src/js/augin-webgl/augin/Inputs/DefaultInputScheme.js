import { Vector3 } from "../../threejs/three.module.js";

export class DefaultInputScheme {
    constructor(viewer)
    {
        this.viewer = viewer;
    }

    onMainAction(action)
    {
        if (this.viewer.isolation.isActive()) return;

        const camera = this.viewer.camera;
        const selection = this.viewer.selection;
        if (!(action == null ? void 0 : action.object)) {
            selection.deselect();
            camera.orbitOnCenter();
            return;
        }

        selection.byIntersect(action.intersection);
        if (action.type === "double") {
            camera.focusOnObject(this.viewer.selection.getFirstSelectedObject(), true);
        }
        else {
            camera.orbitOnPoint(action.intersection.point);
        }
    }
}