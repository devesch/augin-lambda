import { SphereGeometry, Mesh, EdgesGeometry, LineBasicMaterial, LineSegments } from "../../threejs/three.module.js";

export class GizmoUtils {
    static drawSphere(position, radius, color) {
        const geometry = new SphereGeometry(radius, 6, 6);
        var geo = new EdgesGeometry(geometry);
        var mat = new LineBasicMaterial({ color: color, linewidth: 5 });
        mat.depthTest = false;
        var wireframe = new LineSegments(geo, mat);
        wireframe.position.copy(position);
        wireframe.layers.set(31);
        return wireframe;
    }

    static updateMatrixWorld(scope, force) {
        Mesh.prototype.updateMatrixWorld.call(scope, force);
    }
}