import { Vector2 } from "../../threejs/three.module.js";
import { InputAction } from "./InputAction.js";

const LEFT = "left";
const MIDDLE = "middle";
const RIGHT = "right";

export class MouseHandler {
    constructor(viewer) {
        this.viewer = viewer;
        this.camera = viewer.camera;
        this.raycast = viewer.raycast;
        this.buttonDown = void 0;
        this.hasMouseMoved = false;
    }

    reinitializeParams() {}

    register() {
        const renderer = this.viewer.renderer;

        renderer.addEventListener('mousedown', this.onMouseDown.bind(this));
        renderer.addEventListener('mouseup', this.onMouseUp.bind(this));
        renderer.addEventListener('wheel', this.onMouseWheel.bind(this));
        renderer.addEventListener('mousemove', this.onMouseMove.bind(this));
        renderer.addEventListener("dblclick", this.onDoubleClick.bind(this));
        document.addEventListener('mouseout', this.onMouseOut.bind(this));
        document.addEventListener('blur', this.onBlur.bind(this));
        renderer.addEventListener('contextmenu', function (e) {
            e.preventDefault();
        }, false);
    }

    onMouseDown(event) {
        event.preventDefault();
        event.stopImmediatePropagation();

        this.buttonDown = this.getButton(event);
    }

    onMouseUp(event) {
        event.preventDefault();
        event.stopImmediatePropagation();

        if (this.hasMouseMoved) {
            this.onDragEnd(event);

            this.buttonDown = void 0;
            this.hasMouseMoved = false;
            return;
        }

        const btn = this.getButton(event);
        if (btn !== this.buttonDown)
            this.onMouseClick(event);

        this.buttonDown = void 0;
    }

    onMouseClick(event) {

        switch (this.buttonDown) {
            case LEFT:
                this.onClick(event)
                break;
            default:
                break;
        }
    }

    onDoubleClick(event) {
        event.preventDefault();
        event.stopImmediatePropagation();

        if (event.button === 0)
            this.onClick(event, true)
    }

    onClick(event, doubleClick = false) {
        const action = new InputAction(
            doubleClick ? "double" : "main",
            this.getPosition(event),
            this.raycast
        );
        this.viewer.input.mainAction(action);
    }

    onMouseWheel(event) {
        event.preventDefault();
        event.stopImmediatePropagation();

        if (this.camera.isUpdating && this.camera.rotateLookAround) {
            this.camera.stopRotate(true);
        }
    }

    onMouseMove(event) {
        event.preventDefault();
        event.stopImmediatePropagation();
        this._mouseIsMoving = true;

        if (this.buttonDown)
            this.onMouseDrag(event);
    }

    onMouseOut(event) {
        if (!event.relatedTarget && !event.toElement) {
            if (this._mouseIsMoving) {
                this.buttonDown = void 0;
            }
            this._mouseIsMoving = false;
        }
    }

    onBlur(event) {
        if (this._mouseIsMoving) {
            this.buttonDown = void 0;
        }
        this._mouseIsMoving = false;
    }

    onMouseDrag(event) {
        const deltaX = event.movementX || event.mozMovementX || event.webkitMovementX || 0;
        const deltaY = event.movementY || event.mozMovementY || event.webkitMovementY || 0;
        const size = this.viewer.renderer.getSize();
        const delta = new Vector2(deltaX / size.x, deltaY / size.y);

        this.hasMouseMoved = true;

        switch (this.buttonDown) {
            case LEFT:
                this.onMouseLeftDrag(delta);
                break;
            case MIDDLE:
                this.onMouseMiddleDrag(delta);
                break;
            case RIGHT:
                this.onMouseRightDrag(delta);
                break;
        }
    }

    onMouseLeftDrag(delta) {
        this.camera.startRotate();
    }

    onMouseMiddleDrag(delta) {}

    onMouseRightDrag(delta) {
    }

    onDragEnd() {
        switch (this.buttonDown) {
            case LEFT:
                break;
            case MIDDLE:
                break;
            case RIGHT:
                break;
        }
    }

    getButton(event) {
        return event.buttons & 1 ? LEFT : event.buttons & 2 ? RIGHT : event.buttons & 4 ? MIDDLE : void 0;
    }

    getPosition(event) {
        const canvasPosition = this.viewer.renderer.getBoundingClientRect();

        var mouseX = event.clientX - canvasPosition.left;
        var mouseY = event.clientY - canvasPosition.top;

        return new Vector2(mouseX, mouseY);
    }
}