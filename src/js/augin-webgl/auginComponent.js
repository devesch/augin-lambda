import { EventDispatcher } from "./threejs/three.module.js";
import { Viewer } from './augin/Viewer.js';
import { Filter } from './augin/Filter.js';

export const Axis = {
    X: 'X',
    Y: 'Y',
    Z: 'Z'
};

export const Side = {
    Left: 'Left',
    Right: 'Right'
};

const axisSideIndexMap = {
    [Axis.X + Side.Right]: 0,
    [Axis.X + Side.Left]: 1,
    [Axis.Y + Side.Right]: 2,
    [Axis.Y + Side.Left]: 3,
    [Axis.Z + Side.Right]: 4,
    [Axis.Z + Side.Left]: 5
};

export class auginComponent {

    constructor() {
        this.viewer = new Viewer();
    }

    updateSettings(settings) {
        this.viewer.settings = settings;
        this.viewer.camera.reinitializeParams();
        this.viewer.input.reinitializeParams();
    }

    /**
     * Passing HDR image url.
     *
     * @param {string} url Url HDR image.
    */
    setHdrBackground(url) {
        this.viewer.settings.background.hdrUrl = url;
    }

    /**
     * Get canvas (div element)
    */
    getCanvas() {
        return this.viewer.getContainer();
    }

    /**
     * Get canvas (div element)
    */
    resizeCanvas() {
        this.viewer.renderer.setSize();
    }

    /**
     * Initialize augin viewer passing a url.
     *
     * @param {string} url Url augin file.
     * @param {EventDispatcher} onLoadedEvent Add a callback when finish load
     * @param {EventDispatcher} onProgressEvent Add a callback to progress download and load file. returns: event.typeProgress, event.progress
    */
    load(url, { id = void 0, onLoadedEvent = void 0, onProgressEvent = void 0 }) {
        this.viewer.init(url, id, onLoadedEvent, onProgressEvent);
    }

    /**
     * Select object passing a guid string
    */
    selectObject(guid) {
        return this.viewer.selection.byGuid(guid);
    }

    focusSelectedObject() {
        const object = this.viewer.selection.getFirstSelectedObject();
        if (object !== void 0)
            this.viewer.camera.focusOnObject(object, true);
    }

    /**
     * Add a callback which returns guid of selected object
     *
     * @param {EventDispatcher} event returns: event.guid
    */
    addSelectObjectEvent(event) {
        this.viewer.selection.addSelectEvent(event);
    }

    /**
     * @param {EventDispatcher} event returns: event.guid
    */
    addLowFpsEvent(event) {
        this.viewer.addFpsLowEvent(event);
    }

    /**
     * Add a callback when none object is selected
     *
     * @param {EventDispatcher} event
    */
    addDeselectObjectEvent(event) {
        this.viewer.selection.addDeselectEvent(event);
    }

    /**
     * Toggle isolation mode
    */
    toggleIsolation() {
        if (this.viewer.isolation.isActive()) {
            this.viewer.isolation.remove();
        }
        else {
            this.viewer.isolation.apply();
        }
        return this.viewer.isolation.isActive();
    }

    /**
     * Toggle measure mode
    */
    toggleMeasure() {
        if (this.viewer.measure.isActive()) {
            this.viewer.measure.deselect();
        }
        else {
            this.viewer.measure.apply();
        }
        return this.viewer.measure.isActive();
    }

    /**
     * Add a callback which returns distance of measurement from points
     *
     * returns: event.distance
     *
     * @param {EventDispatcher} event
    */
    addMeasureDistanceEvent(event) {
        this.viewer.measure.addMeasureDistanceEvent(event);
    }

    removeMeasure() {
        this.viewer.measure.remove();
    }

    /**
     * Change and apply cut size value
     *
     * @param {Axis} axis: X, Y, Z
     * @param {Side} side: Left, Right
     * @param {number} value: -1.0 ~ 1.0
    */
    changeCut(axis, side, value) {
        const key = axis + side;
        const index = axisSideIndexMap[key];
        if (index !== void 0) {
            if (side === Side.Left) {
                value = -value;
            }
            this.viewer.clippingPlanes.changeClipPlane(index, value);
        }
    }

    resetCut() {
        this.viewer.clippingPlanes.reset();
    }

    /**
     * @param {boolean} value
    */
    showCutPlanes(value) {
        this.viewer.clippingPlanes.showPlanes(value);
    }

    toggleStats() {
        const value = !this.viewer.settings.showStats;
        this.showStats(value);
    }

    /**
     * @param {boolean} value
    */
    showStats(value) {
        this.viewer.settings.showStats = value;
        this.viewer.stats.active(value);
    }

    getTypes() {
        return this.viewer.aug.types;
    }

    getStoreys() {
        return this.viewer.aug.project.storeys;
    }

    async toggleType(type) {
        await this.#waitForEndOfFrame();
        await this.#waitForEndOfFrame();

        return new Promise((resolve, reject) => {
            try {
                Filter.toggleType(type);
                this.viewer.aug.updateObject();
                this.viewer.render();
                resolve();
            } catch (error) {
                reject(error);
            }
        });
    }

    async toggleStoreyByElevation(guid) {
        await this.#waitForEndOfFrame();
        await this.#waitForEndOfFrame();

        return new Promise((resolve, reject) => {
            try {
                Filter.toggleStoreyByElevation(this.viewer.aug.project.storeys, guid);
                this.viewer.aug.updateObject();
                this.viewer.render();
                resolve();
            } catch (error) {
                reject(error);
            }
        });
    }

    async toggleStorey(guid) {
        await this.#waitForEndOfFrame();
        await this.#waitForEndOfFrame();

        return new Promise((resolve, reject) => {
            try {
                Filter.toggleStorey(guid);
                this.viewer.aug.updateObject();
                this.viewer.render();
                resolve();
            } catch (error) {
                reject(error);
            }
        });
    }

    async toggleLayer(guid, elementsGuid) {
        await this.#waitForEndOfFrame();
        await this.#waitForEndOfFrame();

        return new Promise((resolve, reject) => {
            try {
                Filter.toggleLayer(guid, elementsGuid);
                this.viewer.aug.updateObject();
                this.viewer.render();
                resolve();
            } catch (error) {
                reject(error);
            }
        });
    }

    consoleInstancesQtd() {
        console.log("Instances qtd: " + this.viewer.aug.sceneBuilder.instanceLength);
    }

    #waitForEndOfFrame() {
        return new Promise((resolve) => {
            requestAnimationFrame(resolve);
        });
    }
}