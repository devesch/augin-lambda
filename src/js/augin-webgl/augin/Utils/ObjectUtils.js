import { Box3, Vector3 } from "../../threejs/three.module.js";

export class ObjectUtils {
    static getBoundingBox(object) {
        return new Box3().setFromObject(object);
    }

    static getObjectCenterAndSize(box) {
        const center = new Vector3();
        box.getCenter(center);

        const size = new Vector3();
        box.getSize(size);

        return [center, size];
    }

    static boxWholeInside(objectBox, objectWholeBox) {
        if (objectBox.min.x < objectWholeBox.min.x || objectBox.min.x > objectWholeBox.max.x) return false;
        if (objectBox.min.y < objectWholeBox.min.y || objectBox.min.y > objectWholeBox.max.y) return false;
        if (objectBox.min.z < objectWholeBox.min.z || objectBox.min.z > objectWholeBox.max.z) return false;
        if (objectBox.max.x < objectWholeBox.min.x || objectBox.max.x > objectWholeBox.max.x) return false;
        if (objectBox.max.y < objectWholeBox.min.y || objectBox.max.y > objectWholeBox.max.y) return false;
        if (objectBox.max.z < objectWholeBox.min.z || objectBox.max.z > objectWholeBox.max.z) return false;

        return true;
    }
}