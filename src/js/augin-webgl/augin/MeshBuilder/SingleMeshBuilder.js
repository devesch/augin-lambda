import { BufferAttribute, BufferGeometry, Vector3 } from "../../threejs/three.module.js";
import { StructBytesSize } from "../Helpers/StructBytesSize.js";

export class SingleMeshBuilder {
    constructor(aug, vertexCount, indexCount, useAlpha) {
        this.aug = aug;
        this.useAlpha = useAlpha;
        this.colorSize = useAlpha ? 4 : 3;
        this.indices = new Uint32Array(indexCount);
        this.vertices = new Float32Array(vertexCount);
        this.colors = new Float32Array(indexCount * this.colorSize);
    }

    createSingleMesh(meshDataView, element, applyMatrix = true) {
        let vertexStart = 0;
        let vertexEnd = 0;
        let indexOffset = 0;
        let index = 0;
        let verticesIndex = 0;

        const materials = this.aug.materials;

        const vector = new Vector3();

        for (let meshIndex = 0; meshIndex < element.meshesInfoCount; meshIndex++) {
            const meshInfo = this.aug.meshesInfos[element.meshesInfoStartIndex + meshIndex];
            let intialOffset = meshInfo.offset;
            let lengthOffset = meshInfo.vertexCount;
            vertexEnd += lengthOffset;

            const matrix = element.getMatrix();
            const currentVertices = new Float32Array(meshDataView.buffer, intialOffset, lengthOffset);
            for (let v = 0; v < currentVertices.length; v += 3) {
                vector.fromArray(currentVertices, v);
                if (applyMatrix) {
                    vector.applyMatrix4(matrix);
                }
                vector.toArray(this.vertices, verticesIndex + v);
            }

            verticesIndex += currentVertices.length;

            intialOffset += meshInfo.vertexCount * StructBytesSize.INT;
            lengthOffset = meshInfo.faceCount;

            const currentFaces = new Uint32Array(meshDataView.buffer, intialOffset, lengthOffset);
            const augMaterial = materials[meshInfo.material];
            for (let indicesIndex = 0; indicesIndex < currentFaces.length; indicesIndex++) {
                const newIndex = currentFaces[indicesIndex] + indexOffset;
                this.indices[index++] = newIndex;

                const v = newIndex * this.colorSize;
                this.colors[v] = augMaterial.color[0];
                this.colors[v + 1] = augMaterial.color[1];
                this.colors[v + 2] = augMaterial.color[2];
                if (this.useAlpha)
                    this.colors[v + 3] = augMaterial.color[3];
            }

            indexOffset += (vertexEnd - vertexStart) / 3;

            vertexStart = vertexEnd;
        }
    }

    generateGeometry() {
        const geometry = new BufferGeometry();
        geometry.setAttribute("position", new BufferAttribute(this.vertices, 3));
        geometry.setIndex(new BufferAttribute(this.indices, 1));
        if (this.colors) {
            geometry.setAttribute(
                "color",
                new BufferAttribute(this.colors, this.colorSize)
            );
        }
        geometry.computeVertexNormals();
        return geometry;
    }
}