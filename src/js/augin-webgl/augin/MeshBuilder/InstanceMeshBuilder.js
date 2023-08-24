import { BufferAttribute, BufferGeometry, InstancedMesh, Color, Vector3, Quaternion } from "../../threejs/three.module.js";
import { StructBytesSize } from "../Helpers/StructBytesSize.js";
import { Data } from './Data.js';
import { Filter } from '../Filter.js';
import { SingleMeshBuilder } from "./SingleMeshBuilder.js";

export class InstanceMeshBuilder {
    constructor(aug) {
        this.aug = aug;
    }

    hasAlpha(element) {
        // for (let meshIndex = 0; meshIndex < element.meshesInfoCount; meshIndex++) {
        //     const meshInfo = this.aug.meshesInfos[element.meshesInfoStartIndex + meshIndex];
        //     const augMaterial = this.aug.materials[meshInfo.material];
        //     if (augMaterial.color[3] < 1)
        //         return true;
        // }
        return false;
    }

    createInstancedMeshes(meshDataView, instances) {
        const result = [];

        const elements = this.aug.elements;

        let instanceMeshId = 0;
        for (const key in instances) {
            const elementIndexes = instances[key];
            let instancedMeshes;
            const currentElements = this.filterElements(elementIndexes, elements);
            for (let index = 0; index < currentElements.length; index++) {
                const element = currentElements[index].element;

                if (!instancedMeshes) {
                    instancedMeshes = this.generateGeometry(meshDataView, element, currentElements.length);
                }

                for (const instancedMesh of instancedMeshes) {
                    const matrix = element.getMatrix();
                    instancedMesh.setMatrixAt(index, matrix);
                    instancedMesh.instanceMatrix.needsUpdate = true;
                    instancedMesh.meshId = instanceMeshId;
                    result.push(instancedMesh);
                }

                Data.addInstanceElement(instanceMeshId, currentElements[index].elementIndex);
            }
            instancedMeshes = void 0;
            instanceMeshId++;
        }

        return result;
    }

    generateGeometry(meshDataView, element, instanceLength, applyColor = true) {
        const { meshesInfoCount, meshesInfoStartIndex } = element;
        const instancedMeshes = [];

        for (let meshIndex = 0; meshIndex < meshesInfoCount; meshIndex++) {
            const meshInfo = this.aug.meshesInfos[meshesInfoStartIndex + meshIndex];

            const vertices = new Float32Array(meshDataView.buffer, meshInfo.offset, meshInfo.vertexCount);
            const faces = new Uint32Array(meshDataView.buffer, meshInfo.offset + meshInfo.vertexCount * StructBytesSize.INT, meshInfo.faceCount);

            const geometry = new BufferGeometry();
            geometry.setAttribute('position', new BufferAttribute(vertices, 3));
            geometry.setIndex(new BufferAttribute(faces, 1));
            const material = this.aug.renderer.materials.getMaterial(this.hasAlpha(element));
            if (applyColor) {
                const augMaterial = this.aug.materials[meshInfo.material];
                const colorSize = augMaterial.color[3] < 1 ? 4 : 3;
                const colors = new Float32Array(faces.length * colorSize);

                for (let faceIndex = 0; faceIndex < faces.length; faceIndex++) {
                    const v = faceIndex * colorSize;
                    colors[v] = augMaterial.color[0];
                    colors[v + 1] = augMaterial.color[1];
                    colors[v + 2] = augMaterial.color[2];
                    if (colorSize > 3) {
                        colors[v + 3] = augMaterial.color[3];
                    }
                }
                geometry.setAttribute("color", new BufferAttribute(colors, colorSize));
            }

            geometry.computeVertexNormals();

            // Workaround for instance meshes lighting issues
            let normals = geometry.attributes.normal;
            for (let i = 0; i < normals.count; i++) {
                normals.setXYZ(i, -normals.getX(i), -normals.getY(i), -normals.getZ(i));
            }
            normals.needsUpdate = true;

            const instancedMesh = new InstancedMesh(geometry, material, instanceLength);
            instancedMeshes.push(instancedMesh);
        }

        return instancedMeshes;
    }

    filterElements(elementIndexes, elements) {
        let currentElements = [];
        for (let instanceIndex = 0; instanceIndex < elementIndexes.length; instanceIndex++) {
            const elementIndex = elementIndexes[instanceIndex];
            const element = elements[elementIndex];

            if (!Filter.has(element)) {
                currentElements.push({ element, elementIndex} );
            }
        }
        return currentElements;
    }
}