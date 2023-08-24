import { BufferGeometry, Line, LineBasicMaterial, Vector3 } from "../../threejs/three.module.js";

export class MeasureLine {
    constructor(viewer) {
        this.viewer = viewer;
        this.renderer = viewer.renderer;
        this.textRenderer = viewer.renderer.text2DRenderer;
        this.line = void 0;
        this.textIndex = -1;
        this.material = new LineBasicMaterial({
            color: viewer.settings.materials.measure.line.color,
            linewidth: viewer.settings.materials.measure.line.width,
            linecap: 'round', //ignored by WebGLRenderer
            linejoin: 'round', //ignored by WebGLRenderer
            depthTest: false
        });
    }

    drawLine(point1, point2, distance) {
        const points = [];
        points.push(point1);
        points.push(point2);

        const geometry = new BufferGeometry().setFromPoints(points);
        this.line = new Line(geometry, this.material);
        this.line.renderOrder = 1;
        this.line.layers.set(this.viewer.measure.layer);

        const centerPoint = new Vector3().addVectors(point1, point2).multiplyScalar(0.5);

        this.textIndex = this.textRenderer.create(this.line, centerPoint.add(new Vector3(0, .25, 0)), distance.toFixed(2) + "m");

        this.renderer.textEnabled = true;

        this.viewer.scene.add(this.line);
        this.viewer.render();
    }

    remove() {
        if (this.line == null) return;

        this.viewer.scene.remove(this.line);

        if (this.line.geometry) {
            this.line.geometry.dispose();
        }
        if (this.line.material) {
            this.line.material.dispose();
        }

        this.textRenderer.remove(this.line, this.textIndex);

        this.line = void 0;
        this.viewer.render();
    }
}