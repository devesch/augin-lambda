import { Vector2, Raycaster } from "../../threejs/three.module.js";

export class Raycast {
    constructor(viewer) {
        this.pointer = new Vector2;
        this.raycaster = new Raycaster();
        this.viewer = viewer;
    }

    getIntersection(position) {
        const scene = this.viewer.scene;
        const camera = this.viewer.getCamera();

        const canvasPosition = this.viewer.renderer.getBoundingClientRect();

        this.pointer.x = 2 * (position.x / canvasPosition.width) - 1;
        this.pointer.y = 1 - 2 * (position.y / canvasPosition.height);

        camera.updateMatrixWorld();
        this.raycaster.setFromCamera(this.pointer, camera);

        const intersects = this.raycaster.intersectObjects(scene.children);

        if (intersects.length > 0) {
            let currentIndex = 0;
            let foundObject = false;
            let intersect;
            while (currentIndex < intersects.length && !foundObject) {
                intersect = intersects[currentIndex];
                foundObject = this.viewer.clippingPlanes.insideClippingPlane(intersect.point);
                if (!foundObject)
                    currentIndex++;
            }

            if (foundObject) {
                return intersect;
            }
        }

        return void 0;
    }
}