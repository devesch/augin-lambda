import { Vector2 } from "../../threejs/three.module.js";
import { InputAction } from "./InputAction.js";

export class TouchHandler {
    constructor(viewer) {
        this.viewer = viewer;
        this.camera = viewer.camera;
        this.raycast = viewer.raycast;
        this.isolation = viewer.isolation;

        this.initialScale = 1;
        this.touchStartTime = null;
        this.hasMoved = false;
        this.cameraIsInsideProject = false;

        this.DOUBLE_TAP_MS = 300;
        this.TAP_TIME_MS = 300;
        this.MIN_DELTA_MOVE = 0.01;

        this.reinitializeParams();
    }

    reinitializeParams() {
    }

    register() {
        const renderer = this.viewer.renderer;

        renderer.addEventListener("touchstart", this.onTouchStart.bind(this), false);
        renderer.addEventListener("touchmove", this.onTouchMove.bind(this), false);
        renderer.addEventListener("touchend", this.onTouchEnd.bind(this), false);

        renderer.addEventListener('contextmenu', function (e) {
            e.preventDefault();
        }, false);
    }

    reset() {
        this.touchStartTime = this.currentTouch = this.touch1 = this.touch2 = void 0;
    }

    onTouchStart(event) {
        event.preventDefault();
        event.stopImmediatePropagation();

        const touches = event.touches;

        if (touches.length === 1) {
            this.cameraIsInsideProject = this.camera.isInsideProject;
            this.currentTouch = this.touchToVector(touches[0]);
            this.touchStartTime = Date.now();
            this.hasMoved = false;
        } else if (touches.length === 2) {
            this.touch1 = this.touchToVector(touches[0]);
            this.touch2 = this.touchToVector(touches[1]);
            this.currentTouch = this.calculateMidpoint(this.touch1, this.touch2);
            this.initialScale = this.getCurrentScale();
        }
    }

    onTouchMove(event) {
        event.preventDefault();
        event.stopImmediatePropagation();

        const touches = event.touches;
        const size = this.viewer.renderer.getSize();

        if (touches.length === 1) {
            const newTouch = this.touchToVector(touches[0]);
            const delta = new Vector2();
            if (this.currentTouch != void 0) {
                delta.subVectors(newTouch, this.currentTouch).multiply(new Vector2(1 / size.x, 1 / size.y));
            }
            else {
                delta.subVectors(newTouch, new Vector2(0, 0)).multiply(new Vector2(1 / size.x, 1 / size.y));
            }
            this.currentTouch = newTouch;
            if (delta.x > this.MIN_DELTA_MOVE || delta.y > this.MIN_DELTA_MOVE) {
                this.hasMoved = true;
            }
            this.onDrag(delta);
        }
        if (!this.touch1 || !this.touch2)
            return;
        if (touches.length === 2) {
            const newTouch1 = this.touchToVector(touches[0]);
            const newTouch2 = this.touchToVector(touches[1]);
            const newTouch = this.calculateMidpoint(newTouch1, newTouch2);
            const newDistance = newTouch1.distanceTo(newTouch2);
            const moveDelta = new Vector2();
            moveDelta.subVectors(this.currentTouch, newTouch).multiplyScalar(-1 / size.x, -1 / size.y);
            const previousDistance = this.touch1.distanceTo(this.touch2);
            const minSize = Math.min(size.x, size.y);
            const zoomDelta = -(this.initialScale * (newDistance - previousDistance)) / minSize;
            this.currentTouch = newTouch;
            this.touch1 = newTouch1;
            this.touch2 = newTouch2;

            if (moveDelta.length() > Math.abs(zoomDelta)) {
                this.onMove(moveDelta);
            }
            else {
                this.onPinch(zoomDelta);
            }
        }
    }

    onTouchEnd(event) {
        event.preventDefault();
        event.stopImmediatePropagation();

        const touchDuration = Date.now() - this.touchStartTime;
        if (touchDuration <= this.TAP_TIME_MS && !this.hasMoved) {
            this.onTap();
        }

        this.reset();
    }

    onTap() {
        const time = new Date().getTime();
        const double = this._lastTapMs && time - this._lastTapMs < this.DOUBLE_TAP_MS;
        this._lastTapMs = new Date().getTime();

        const action = new InputAction(
            double ? "double" : "main",
            this.currentTouch,
            this.raycast
        );
        this.viewer.input.mainAction(action);
    }

    onDrag(delta) {
        if (this.cameraIsInsideProject && !this.isolation.isActive()) {
            this.camera.startRotate();
        }
    }

    onMove(delta) {
    }

    onPinch(delta) {
        if (this.camera.isUpdating && this.camera.rotateLookAround) {
            this.camera.stopRotate(true);
        }
    }

    touchToVector(touch) {
        return new Vector2(touch.pageX, touch.pageY);
    }

    getCurrentScale() {
        return 1;
    }

    calculateMidpoint(p1, p2) {
        const result = new Vector2();
        result.lerpVectors(p1, p2, 0.5);
        return result;
    }
}