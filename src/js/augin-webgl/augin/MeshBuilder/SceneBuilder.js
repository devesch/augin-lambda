import { Group, Mesh } from "../../threejs/three.module.js";
import { MergeInfo } from './MergeInfo.js';
import { InstanceMeshBuilder } from "./InstanceMeshBuilder.js";
import { MergeMeshBuilder } from "./MergeMeshBuilder.js";
import { SingleMeshBuilder } from './SingleMeshBuilder.js';
import { Data } from './Data.js';

export class SceneBuilder {
    constructor(aug, instances) {
        this.aug = aug;
        this.meshDataView = aug.meshDataView;
        this.instances = instances;
        this.instanceLength = Object.keys(this.instances).length;
        this.instanceMeshBuilder = null;
        this.mergeMeshBuilder = null;
    }

    clear() {
        Data.clear();
    }

    createInstancedMesh() {
        this.instanceMeshBuilder = new InstanceMeshBuilder(this.aug);
        const instancedContainer = new Group();
        if (this.instanceLength > 0) {
            const meshes = this.instanceMeshBuilder.createInstancedMeshes(this.meshDataView, this.instances);
            for (let index = 0; index < meshes.length; index++) {
                const mesh = meshes[index];
                instancedContainer.add(mesh);
            }
        }
        return instancedContainer;
    }

    createMergeMeshes() {
        const mergeInfo = new MergeInfo().getMergeInfo(this.aug, this.instances)
        this.mergeMeshBuilder = new MergeMeshBuilder(mergeInfo, this.aug);
        this.mergeMeshBuilder.createMergeMeshes(this.meshDataView, this.instances);
        const geometry = this.mergeMeshBuilder.generateGeometry();
        const material = this.aug.renderer.materials.getMaterial(this.mergeMeshBuilder.useAlpha);

        let mesh = new Mesh(geometry, material);
        mesh.name = "MergedMesh";
        return mesh;
    }

    createSingleMesh(element) {
        const useAlpha = false;
        const singleMeshBuilder = new SingleMeshBuilder(this.aug, element.meshInfo.vertexCount, element.meshInfo.indexCount, useAlpha);
        singleMeshBuilder.createSingleMesh(this.meshDataView, element);
        const geometry = singleMeshBuilder.generateGeometry();
        const material = this.aug.renderer.materials.getMaterial(useAlpha);

        return new Mesh(geometry, material);
    }
}