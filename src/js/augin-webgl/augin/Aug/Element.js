import { Matrix4 } from "../../threejs/three.module.js";

export class Element {
    constructor() {
        this.placement = Float32Array.from({ length: 16 }),
            this.boundingBox = Float32Array.from({ length: 6 }),
            this.guid = "",
            this.ifcType = "",
            this.hash = BigInt(0),
            this.perimeter = 0,
            this.storeysId = [],
            this.meshesInfoStartIndex = 0,
            this.meshesInfoCount = 0,
            this.hasTransparency = false
    }

    getMatrix() {
        const m00 = this.placement[0];
        const m01 = this.placement[1];
        const m02 = this.placement[2];
        const m03 = this.placement[3];
        const m10 = this.placement[4];
        const m11 = this.placement[5];
        const m12 = this.placement[6];
        const m13 = this.placement[7];
        const m20 = this.placement[8];
        const m21 = this.placement[9];
        const m22 = this.placement[10];
        const m23 = this.placement[11];
        const m30 = this.placement[12];
        const m31 = this.placement[13];
        const m32 = this.placement[14];
        const m33 = this.placement[15];

        let matrix = new Matrix4();
        matrix.set(
            m00, m01, -m02, m03,
            m10, m11, m12, m13,
            -m20, -m21, m22, -m23,
            m30, m31, m32, m33
        );

        return matrix;
    }
}