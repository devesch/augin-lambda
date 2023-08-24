import { Filter } from '../Filter.js'

export class MergeInfo {
    constructor() {
        this.indexCount = 0;
        this.vertexCount = 0;
        this.useAlpha = false;
	}

    getMergeInfo(aug, instances) {
        for (let elementIndex = 0; elementIndex < aug.elements.length; elementIndex++) {
            const element = aug.elements[elementIndex];

            if (element.hash in instances) continue;
            if (Filter.has(element)) continue;

            for (let meshIndex = 0; meshIndex < element.meshesInfoCount; meshIndex++) {
                const meshInfo = aug.meshesInfos[element.meshesInfoStartIndex + meshIndex];
                this.vertexCount += meshInfo.vertexCount;
                this.indexCount += meshInfo.faceCount;

                // const augMaterial = aug.materials[meshInfo.material];
                // if (augMaterial.color[3] < 1)
                //     this.useAlpha = true;
            }
        }
        return this;
    }
}