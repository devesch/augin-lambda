import { PerspectiveCamera, Vector3 } from "../threejs/three.module.js";
import { CameraControls } from "./CameraControls.js";
import { AugUtils } from "./Utils/AugUtils.js";
import { GizmoUtils } from "./Utils/GizmoUtils.js";
import { ObjectUtils } from "./Utils/ObjectUtils.js";

export class Camera {
    constructor(viewer) {
        const scope = this;

        scope.camera = new PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.01, 100000);
        scope.cameraControls = new CameraControls(scope.camera, viewer.getContainer());
        scope.viewer = viewer;
        scope.showOrbitHelper = true;

        scope.reinitializeParams();

        scope.cameraControls.addEventListener('controlstart', (event) => {
            if (!scope.hasOrbitTarget) {
                scope.orbitOnCenter();
            }
            else {
                scope.orbitOnPoint(this.lastPoint);
            }
            if (scope.isUpdating && scope.rotateOrbit) {
                scope.rotateOrbit = false;
                scope.startRotate();
            } else if (scope.isUpdating && scope.rotateLookAround) {
                scope.stopRotate();
            }
        });

        scope.cameraControls.addEventListener('control', (event) => {
            if (event.target._isUserControllingTruck) {
                scope.cameraControls.truckSpeed = scope.#getMoveMultiplier();
            } else if (event.target._isUserControllingRotate && event.target._currentMouseButton == 2) {
                scope.rotateOrbit = true;
                if (this.showOrbitHelper)
                    scope.sphereHelper.visible = this.hasOrbitTarget;
            } else {
                if (this.showOrbitHelper)
                    scope.sphereHelper.visible = false;
            }
        });

        scope.cameraControls.addEventListener('controlend', (event) => {
            if (event.target._isUserControllingRotate && !scope.rotateLookAround) {
                scope.rotateOrbit = false;
            }
            if (this.showOrbitHelper)
                scope.sphereHelper.visible = false;
        });

        scope.cameraControls.addEventListener('sleep', (event) => {
            if (scope.rotateLookAround) {
                scope.stopRotate();
            }
        });
    }

    get position() {
        return this.camera.position;
    }

    get projectCenter() {
        return AugUtils.projectCenter(this.viewer.aug);
    }

    get forward() {
        return this.camera.getWorldDirection(new Vector3());
    }

    get target() {
        if (this.rotateLookAround) {
            let offset = new Vector3().subVectors(this.lastTarget, this.camera.position);
            let newTarget = this.position.clone().add(offset);
            return newTarget;
        } else {
            return this.cameraControls.getTarget();
        }
    }

    get orbitDistance() {
        if (this.rotateLookAround) {
            let position = new Vector3(0, 0, 0);
            this.cameraControls.getTarget(position, false);
            return this.camera.position.clone().distanceTo(position);
        } else {
            return this.cameraControls.distance;
        }
    }

    get isInsideProject() {
        return AugUtils.pointInsideProject(this.viewer.aug, this.camera.position);
    }

    reinitializeParams() {
        this.cameraSpeed = this.viewer.settings.camera.cameraSpeed;
        this.orbitSpeed = this.viewer.settings.camera.orbitSpeed;
        this.dollySpeed = this.viewer.settings.camera.dollySpeed;
        this.truckSpeed = this.viewer.settings.camera.truckSpeed;

        this.cameraControls.truckSpeed = this.truckSpeed;
        this.cameraControls.dollySpeed = this.dollySpeed;
        this.cameraControls.azimuthRotateSpeed = this.orbitSpeed;
        this.cameraControls.polarRotateSpeed = this.orbitSpeed;
        this.cameraControls.infinityDolly = true;
        this.cameraControls.restThreshold = 1;

        this.azimuthRotateSpeed = this.orbitSpeed;
        this.polarRotateSpeed = this.orbitSpeed;
        this.speed = 1;
        this.minDistanceOnTarget = 3;
        this.lastDistance = 0;
        this.rotateLookAround = false;
        this.rotateOrbit = false;
        this.hasOrbitTarget = false;
        this.lastPoint = new Vector3();
    }

    initialize(boundingBox) {
        this.cameraControls.rotateTo(0, Math.PI * 0.5, false);
        this.cameraControls.fitToBox(boundingBox, false);

        this.sphereHelper = GizmoUtils.drawSphere(this.cameraControls.getTarget(), 1, this.viewer.settings.camera.sphere.color);
        this.sphereHelper.visible = false;
        const scaleVector = new Vector3();
        const scope = this;
        this.sphereHelper.updateMatrixWorld = function (force) {
            scaleVector.set(scope.orbitDistance / 100, scope.orbitDistance / 100, scope.orbitDistance / 100);
            scope.sphereHelper.scale.copy(scaleVector);
            GizmoUtils.updateMatrixWorld(this, force);
        }
        this.viewer.scene.add(this.sphereHelper);

        this.cameraControls.infinityDolly = true;
        this.cameraControls.minDistance = this.minDistanceOnTarget;
        this.lastTarget = this.cameraControls.getTarget();
    }

    rotate(delta) {
        this.startRotate();
        this.cameraControls.rotate(-delta.x, -delta.y, true);
    }

    startRotate() {
        if (!this.rotateLookAround) {
            this.rotateLookAround = true;

            this.lastDistance = this.cameraControls.distance;
            this.lastTarget = this.cameraControls.getTarget();

            const targetPosition = this.camera.position.clone().add(this.forward.multiplyScalar(0.001));
            this.cameraControls.setOrbitPoint(targetPosition.x, targetPosition.y, targetPosition.z);

            this.cameraControls.azimuthRotateSpeed = 0.3;
            this.cameraControls.polarRotateSpeed = 0.3;
            this.cameraControls.minDistance = this.cameraControls.maxDistance = 1;

            this.cameraControls.distance = .001;
        }
    }

    stopRotate (force = false) {
        if (this.rotateLookAround || force) {
            this.rotateLookAround = false;

            this.cameraControls.azimuthRotateSpeed = this.azimuthRotateSpeed;
            this.cameraControls.polarRotateSpeed = this.polarRotateSpeed;
            this.cameraControls.minDistance = 1;
            this.cameraControls.maxDistance = Infinity;

            let offset = new Vector3().subVectors(this.lastTarget, this.camera.position);
            let newTarget = this.camera.position.clone().add(offset);

            this.cameraControls.distance = this.lastDistance;
            this.cameraControls.setOrbitPoint(newTarget.x, newTarget.y, newTarget.z);
        }
    }

    move (delta) {
        delta.multiplyScalar(this.#getVelocityMultiplier());
        // if (this.hasOrbitTarget)
        //     this.cameraControls.setOrbitPoint(this.lastPoint.x, this.lastPoint.y, this.lastPoint.z);
        // else
        //     this.cameraControls.setOrbitPoint(0, 0, 0);
        this.cameraControls.move(delta.x, delta.y, delta.z, true);
    }

    focusOnObject(object) {
        this.orbitOnObject(object);
        this.cameraControls.fitToSphere(object, true);
    }

    orbitOnObject(object) {
        const center = ObjectUtils.getBoundingBox(object).getCenter(new Vector3());
        this.orbitOnPoint(center);
    }

    orbitOnPoint(point) {
        this.hasOrbitTarget = true;
        this.infinityDolly = false;
        this.cameraControls.minDistance = 1;
        this.cameraControls.maxDistance = Infinity;
        this.cameraControls.setOrbitPoint(point.x, point.y, point.z);
        this.lastPoint.copy(point);
    }

    orbitOnCenter() {
        this.hasOrbitTarget = false;
        this.infinityDolly = true;
        this.cameraControls.minDistance = this.minDistanceOnTarget;
        this.cameraControls.maxDistance = Infinity;
        this.cameraControls.setOrbitPoint(0, 0, 0);
        this.lastPoint = new Vector3();
    }

    updateAspect() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
    }

    enableLayer(layer) {
        this.camera.layers.enable(layer);
    }

    update(delta) {
        let position = new Vector3(0, 0, 0);
        this.cameraControls.getTarget(position);
        this.isUpdating = this.cameraControls.update(delta);
        if (this.showOrbitHelper)
            this.sphereHelper.position.copy(new Vector3().addVectors(position, this.projectCenter));
        return this.isUpdating;
    }

    #getBaseMultiplier() {
        return Math.pow(1.25, this.speed);
    }

    #getMoveMultiplier() {
        // if (this.hasOrbitTarget)
        //     return this.orbitDistance * 0.1;
        return this.truckSpeed;
    }

    #getVelocityMultiplier() {
        // if (this.hasOrbitTarget)
        // {
        //     const distance = this.orbitDistance * 0.1;
        //     // console.log(distance);
        //     return this.#getBaseMultiplier() * distance;
        // }
        // else {
        //     const distance = Math.max(this.orbitDistance * 0.1, this.cameraSpeed);
        //     console.log(this.orbitDistance);
        //     return this.#getBaseMultiplier() * distance;
        // }
        return this.#getBaseMultiplier() * this.cameraSpeed;
    }
}