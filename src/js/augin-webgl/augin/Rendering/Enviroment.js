import { HemisphereLight, DirectionalLight } from "../../threejs/three.module.js";
import { GroundPlane } from "./GroundPlane.js";

export class Environment {
    constructor(settings) {
        // this.groundPlane = new GroundPlane();
        this.skyLight = new HemisphereLight();
        this.sunLights = [];
        this.applySettings(settings);
    }

    getObjects() {
        // return [this.groundPlane.mesh, this.skyLight, ...this.sunLights];
        return [this.skyLight, ...this.sunLights];
    }

    applySettings(settings) {
        this.skyLight.color.copy(settings.skylight.skyColor);
        this.skyLight.groundColor.copy(settings.skylight.groundColor);
        this.skyLight.intensity = settings.skylight.intensity;
        const count = settings.sunLights.length;
        for (let i = 0; i < count; i++) {
            if (!this.sunLights[i]) {
                this.sunLights[i] = new DirectionalLight();
            }
            const color = settings.sunLights[i].color;
            const pos = settings.sunLights[i].position;
            const intensity = settings.sunLights[i].intensity;
            if (color) {
                this.sunLights[i].color.copy(color);
            }
            if (pos) {
                this.sunLights[i].position.copy(pos);
            }
            if (intensity) {
                this.sunLights[i].intensity = intensity;
            }
        }
    }

    applySkylightPosition(position) {
        this.skyLight.position.set(position.x, position.y, position.z);
    }

    enableGround(value) {
        // this.groundPlane.visible = value;
    }

    adaptGroundToContent(box) {
        // this.groundPlane.adaptToContent(box);
    }

}