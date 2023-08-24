import { EquirectangularReflectionMapping } from "../../threejs/three.module.js";
import { RGBELoader } from "../../threejs/jsm/loaders/RGBELoader.js";

export class Background {
    constructor(renderer, settings) {
        let promise = new Promise(function (resolve, reject) {
            new RGBELoader()
                .load(settings.background.hdrUrl, (texture) => {
                    texture.mapping = EquirectangularReflectionMapping;
                    resolve(texture);
                });
        });
        return promise;
    }
}