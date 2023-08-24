import { Vector3 } from "../../threejs/three.module.js";

export class AugUtils {
    static projectCenter(aug) {
        return aug.getOriginalBoundingBox().getCenter(new Vector3());
    }

    static pointInsideProject(aug, point) {
        return aug.getBoundingBox().containsPoint(point);
    }
}