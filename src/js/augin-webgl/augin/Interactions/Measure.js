import { EventDispatcher } from "../../threejs/three.module.js";
import { MeasureLine } from "./MeasureLine.js";
import { MeasurePoint } from "./MeasurePoint.js";
import { MeasureScheme } from "./MeasureScheme.js";

export class Measure {
    constructor(viewer) {
        this.viewer = viewer;
        this.point1 = new MeasurePoint(viewer);
        this.point2 = new MeasurePoint(viewer);
        this.line = new MeasureLine(viewer);
        this.layer = 3;
        this._measureScheme = new MeasureScheme(viewer);
        this._previousScheme;

        this._active = false;

        this.onMeasureDistanceEvent = new EventDispatcher();

        viewer.camera.enableLayer(this.layer);
    }

    addMeasureDistanceEvent(event) {
        this.onMeasureDistanceEvent.addEventListener("measure_distance", event);
    }

    isActive() { return this._active; }

    apply() {
        if (this._active) return;

        this._previousScheme = this.viewer.input.scheme;
        this.viewer.input.scheme = this._measureScheme;
        this._active = true;
    }

    deselect() {
        if (!this._active) return;

        this.viewer.input.scheme = this._previousScheme;
        this._active = false;
    }

    remove() {
        if (this.point1.isSet)
            this.point1.remove();
        if (this.point2.isSet) {
            this.point2.remove();
            this.line.remove();
        }
    }

    setPoint(point) {
        if (this.point2.isSet) {
            this.point1.remove();
            this.point2.remove();
            this.line.remove();
        }

        if (!this.point1.isSet) {
            this.point1.setPoint(point);
        }
        else {
            this.point2.setPoint(point);
            const distance = this.point1.position.distanceTo(this.point2.position);
            this.line.drawLine(this.point1.position, this.point2.position, distance);

            this.onMeasureDistanceEvent.dispatchEvent({ type: "measure_distance", distance: distance });
        }
    }
}