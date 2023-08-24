export class Material {
    constructor() {
        this.color = new Float32Array(4);
        this.type = 0;
        this.hasTexture = false;
        this.baseTexture = "";
        this.secondColor = new Float32Array(4);
        this.factor = 0.0;
        this.hasSecondTexture = false;
        this.secondTexture = "";
        this.hasNormal = false;
        this.normalTexture = "";
    }
}