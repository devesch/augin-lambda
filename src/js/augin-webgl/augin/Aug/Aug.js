import {
	Box3,
	Loader,
	Scene,
	Vector3
} from "../../threejs/three.module.js";
import { Element } from "./Element.js";
import { MeshInfo } from "./MeshInfo.js";
import { Material as AugMaterial } from "./Material.js";
import { StructBytesSize } from "../Helpers/StructBytesSize.js";
import { Helper } from "../Helpers/Helper.js";
import { SceneBuilder } from '../MeshBuilder/SceneBuilder.js';
import { AugFileHandler } from './AugFileHandler.js';

const AUG_MAGIC = 0x6E677561;
const CLJ_MAGIC = 0x706A6C63;
const AUG_EXT = ".aug";
const MESHES_EXT = ".in";
const CLJ_EXT = ".clj";
const BATCH_SIZE = 64;
const PHONG_MAX_VALUE = 128.;

export class AugLoader extends Loader {
	constructor(manager) {
		super(manager);

		this.augVersion = 0;
		this.cljVersion = 0;
		this.materials = [];
		this.elements = [];
		this.meshesInfos = [];
		this.project = {};
		this.types = [];
		this.viewer = void 0;
	}

	setRenderer(renderer) {
		this.renderer = renderer;
	}

	async load(url, id, onLoad, onProgressDownload, onProgressLoad, onError) {
		const fileHandler = await new AugFileHandler(url, id, onProgressDownload);
		const files = fileHandler.unzip();

		const augData = files[AUG_EXT];
		const meshData = files[MESHES_EXT];
		const projectData = files[CLJ_EXT];

		if (onProgressLoad !== null)
			onProgressLoad(0);

		this.loadProject(new DataView(projectData));

		this.parseAugBinary(augData, meshData, onProgressLoad)
			.then((augScene) => {
				this.project.boundingBox = new Box3().setFromObject(augScene);
				window.addEventListener('beforeunload', this.clearObject);

				if (onLoad != null)
					onLoad(augScene);
			})
			.catch((error) => {
				console.error(error);
				if (onError != null)
					onError(error);
			});
	}

	parseAugBinary(augData, meshData, onProgressLoad) {
		const scope = this;
		let augDataView = null;
		let augScene = null;
		return new Promise((resolve, reject) => {
			const totalSteps = 4;
			let currentStep = 0;

			function performNextStep() {
				switch (currentStep) {
					case 0:
						if (onProgressLoad) onProgressLoad((currentStep + 1) / totalSteps);
						// Step 1: Perform first operation
						augDataView = new DataView(augData);
						const success = scope.checkHeader(augDataView);
						if (!success) {
							reject("Error occurred while checking header.");
							return;
						}
						break;

					case 1:
						if (onProgressLoad) onProgressLoad((currentStep + 1) / totalSteps);
						// Step 2: Perform second operation
						scope.loadIndexes(augDataView);
						break;

					case 2:
						if (onProgressLoad) onProgressLoad((currentStep + 1) / totalSteps);
						// Step 3: Perform third operation
						scope.meshDataView = new DataView(meshData);
						augScene = scope.generateObject();
						break;

					case 3:
						if (onProgressLoad) onProgressLoad(1);
						// Step 4: Perform final operation
						resolve(augScene);
						break;
				}

				currentStep++;

				// Call the next step after a small delay to allow UI updates
				setTimeout(performNextStep, 0);
			}

			// Start the process
			performNextStep();
		});
	}

	checkHeader(dataView) {
		const magic = dataView.getUint32(0, true);
		if (magic != AUG_MAGIC) {
			console.error("Invalid magic number");
			return false;
		}

		const version = dataView.getUint16(4, true);

		if (version < 1) {
			console.error("Version is not 1 or more");
			return false;
		}

		this.augVersion = version;

		return true;
	}

	loadIndexes(dataView) {
		let index = 6;
		const numMaterials = dataView.getUint32(index, true);
		index += StructBytesSize.INT;

		for (let i = 0; i < numMaterials; i++) {
			index = this.loadMaterial(dataView, index);
		}

		const numElements = dataView.getUint32(index, true);
		index += StructBytesSize.INT;

		for (let i = 0; i < numElements; i++) {
			index = this.loadElement(dataView, index);
		}
	}

	loadMaterial(dataView, index) {
		let tempMaterial = new AugMaterial();

		const r = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;
		const g = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;
		const b = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;
		const a = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;

		tempMaterial.color = new Float32Array([r, g, b, a]);

		tempMaterial.type = dataView.getUint16(index, true);
		index += StructBytesSize.SHORT;
		const sizeOfTexture = dataView.getUint16(index, true);
		tempMaterial.hasTexture = sizeOfTexture !== 0;
		index += StructBytesSize.SHORT;
		if (tempMaterial.hasTexture)
			tempMaterial.baseTexture = Helper.convertToString(dataView, index, sizeOfTexture);

		index += sizeOfTexture;

		const r2 = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;
		const g2 = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;
		const b2 = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;

		tempMaterial.secondColor = new Float32Array([r2, g2, b2, 1.0]);

		tempMaterial.factor = dataView.getFloat32(index, true);
		if (tempMaterial.factor > 1.0) // If value is more than 1f: is PHONG value, else is BLINN
			tempMaterial.factor /= PHONG_MAX_VALUE;
		index += StructBytesSize.FLOAT;

		const sizeOfSecondTexture = dataView.getUint16(index, true);
		tempMaterial.hasSecondTexture = sizeOfSecondTexture !== 0;
		index += StructBytesSize.SHORT;
		if (tempMaterial.hasSecondTexture)
			tempMaterial.secondTexture = Helper.convertToString(dataView, index, sizeOfSecondTexture);

		index += sizeOfSecondTexture;

		const sizeOfNormalTexture = dataView.getUint16(index, true);
		tempMaterial.hasNormal = sizeOfNormalTexture !== 0;
		index += StructBytesSize.SHORT;
		if (tempMaterial.hasNormal)
			tempMaterial.normalTexture = Helper.convertToString(dataView, index, sizeOfNormalTexture);

		index += sizeOfNormalTexture;

		this.materials.push(tempMaterial);
		return index;
	}

	loadElement(bytes, index) {
		let element = new Element();
		let dataView = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);

		let m00 = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;
		let m10 = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;
		let m20 = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;
		let m30 = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;

		let m01 = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;
		let m11 = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;
		let m21 = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;
		let m31 = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;

		let m02 = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;
		let m12 = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;
		let m22 = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;
		let m32 = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;

		let m03 = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;
		let m13 = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;
		let m23 = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;
		let m33 = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;

		element.placement = new Float32Array([
			m00, m01, -m02, m03,
			m10, m11, -m12, m13,
			-m20, -m21, m22, -m23,
			m30, m31, m32, m33,
		]);

		let bbMinX = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;
		let bbMinY = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;
		let bbMinZ = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;
		let bbMaxX = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;
		let bbMaxY = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;
		let bbMaxZ = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;

		element.boundingBox = new Float32Array([bbMinX, bbMinY, bbMinZ, bbMaxX, bbMaxY, bbMaxZ]);

		let guid = Helper.convertToString(bytes, index, 22);
		index += 22;

		[index, element.ifcType] = Helper.readString32(bytes, index);
		this.#addType(element.ifcType);

		element.guid = guid;

		let hash = Helper.getUint64(dataView, index);
		index += StructBytesSize.LONG;
		element.hash = hash;

		let perimeter = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;
		element.perimeter = perimeter;

		let storeysCount = dataView.getUint16(index, true);
		index += StructBytesSize.SHORT;

		let storeysId = new Array(storeysCount);

		if (storeysCount != 0) {
			for (let i = 0; i < storeysCount; i++) {
				storeysId[i] = dataView.getUint16(index, true);
				index += StructBytesSize.SHORT;
			}
		}

		element.storeysId = storeysId;

		if (this.augVersion == 2) {
			[index, element.storey] = Helper.readString32(bytes, index);
		}

		let meshCount = dataView.getUint32(index, true);
		index += StructBytesSize.INT;

		let countMeshes = this.meshesInfos.length;

		let vertexCount = 0, indexCount = 0;

		for (let i = 0; i < meshCount; i++) {
			let meshInfo = new MeshInfo();
			index = this.loadMeshInfo(dataView, index, meshInfo);

			if (this.materials[meshInfo.material].color.w != 1.0) {
				element.hasTransparency = true;
			}

			vertexCount += meshInfo.vertexCount;
			indexCount += meshInfo.faceCount;
		}

		element.meshesInfoStartIndex = countMeshes;
		element.meshesInfoCount = meshCount;
		element.meshInfo = { vertexCount: vertexCount, indexCount: indexCount };

		this.elements.push(element);
		return index;
	}

	loadMeshInfo(dataView, index, meshInfo) {
		let vertexCount = dataView.getUint32(index, true);
		index += StructBytesSize.INT;
		meshInfo.vertexCount = vertexCount;

		let faceCount = dataView.getUint32(index, true);
		index += StructBytesSize.INT;
		meshInfo.faceCount = faceCount;

		let offset = dataView.getUint32(index, true);
		index += StructBytesSize.INT;
		meshInfo.offset = offset;

		let materialId = dataView.getUint32(index, true);
		index += StructBytesSize.INT;
		meshInfo.material = materialId;

		this.meshesInfos.push(meshInfo);

		return index;
	}

	loadProject(dataView) {
		let index = 0; // Read magic

		const magic = dataView.getUint32(index, true);
		if (magic != CLJ_MAGIC) {
			console.error("Invalid magic number");
			return false;
		}

		index = 4; // Read version

		const version = dataView.getUint16(index, true);

		if (version < 1) {
			console.error("Version is not 1 or more");
			return false;
		}

		this.cljVersion = version;

		index = 6;

		const bbMinX = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;
		const bbMinY = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;
		const bbMinZ = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;
		const bbMaxX = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;
		const bbMaxY = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;
		const bbMaxZ = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;

		// this.project.boundingBox = new Box3(
		// 	new Vector3(bbMinX, bbMinY, bbMinZ),
		// 	new Vector3(bbMaxX, bbMaxY, bbMaxZ)
		// );

		const numStoreys = dataView.getUint16(index, true); // Read number storeys
		const storeys = [];
		index += StructBytesSize.SHORT;

		for (let i = 0; i < numStoreys; i++) {
			let storey = undefined;
			[index, storey] = this.loadStorey(dataView, index);
			storeys.push(storey);
		}

		this.project.storeys = storeys;

		if (dataView.byteLength > index || version > 1) // Has IFC Site Cartesian Points
		{
			const ifcSiteX = dataView.getFloat64(index, true);
			index += StructBytesSize.DOUBLE;
			const ifcSiteY = dataView.getFloat64(index, true);
			index += StructBytesSize.DOUBLE;
			const ifcSiteZ = dataView.getFloat64(index, true);
			index += StructBytesSize.DOUBLE;

			this.project.ifcSiteCartesianPoints = new Vector3(ifcSiteX, ifcSiteY, ifcSiteZ);
		}

		return true;
	}

	loadStorey(dataView, index) {
		const bbMinX = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;
		const bbMinY = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;
		const bbMinZ = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;
		const bbMaxX = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;
		const bbMaxY = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;
		const bbMaxZ = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;

		// const boundingBox = new Unity.Mathematics.float3x2(
		// 	new Unity.Mathematics.float3(bbMinX, bbMinY, bbMinZ),
		// 	new Unity.Mathematics.float3(bbMaxX, bbMaxY, bbMaxZ)
		// );

		const elevation = dataView.getFloat32(index, true);
		index += StructBytesSize.FLOAT;

		const guid = Helper.convertToString(dataView, index, 22); // GUID standard 22 chars
		index += 22;

		[index, name] = Helper.readString32(dataView, index);

		return [index, {name: name, guid: guid, elevation: elevation }];
	}

	#addType(type) {
		if (!this.types.includes(type))
		{
			this.types.push(type);
		}
	}

	generateObject() {
		const instances = this.getAllInstances();

		this.scene = new Scene();
		this.sceneBuilder = new SceneBuilder(this, instances);

		this._instancedMeshes = this.sceneBuilder.createInstancedMesh();
		this._mergedMeshes = this.sceneBuilder.createMergeMeshes();

		this.scene.add(this._instancedMeshes);
		this.scene.add(this._mergedMeshes);

		return this.scene;
	}

	createElementMesh(element) {
		return this.sceneBuilder.createSingleMesh(element);
	}

	updateObject() {
		this.clearObject();

		this._instancedMeshes = this.sceneBuilder.createInstancedMesh();
		this._mergedMeshes = this.sceneBuilder.createMergeMeshes();

		this.scene.add(this._instancedMeshes);
		this.scene.add(this._mergedMeshes);
	}

	getElement(index) {
		return index < this.elements.length ? this.elements[index] : void 0;
	}

	getElementByGuid(guid) {
		for (const element of this.elements) {
			if (element.guid === guid)
				return element;
		}

		return void 0;
	}

	getBoundingBox() {
		return this.project.boundingBox;
	}

	getOriginalBoundingBox() {
		return this.inCenter ? this.project.originalBoundingBox : this.getBoundingBox();
	}

	applyCenter() {
		if (this.inCenter !== void 0) return null;

		this.project.originalBoundingBox = this.project.boundingBox.clone();
		const centerPivot = this.project.boundingBox.getCenter(new Vector3());
		this.project.boundingBox.translate(new Vector3(-centerPivot.x, -centerPivot.y, -centerPivot.z));

		this.inCenter = true;

		return centerPivot;
	}

	getAllInstances() {
		let instances = {};
		const elements = this.elements;
		for (let elementIndex = 0; elementIndex < elements.length; elementIndex++) {
			const element = elements[elementIndex];
			if (element.hash in instances) {
				instances[element.hash].push(elementIndex);
			}
			else {
				instances[element.hash] = [elementIndex];
			}
		}
		const filteredObj = Object.fromEntries(
			Object.entries(instances).filter(([key, value]) => value.length > 1)
		);
		return filteredObj;
	}

	clearObject () {
		if (this._instancedMeshes !== void 0) {
			this._instancedMeshes.children.forEach(instanceMesh => {
				instanceMesh.geometry.dispose();
				instanceMesh.material.dispose();
			});
			this.scene.remove(this._instancedMeshes);
		}

		if (this._mergedMeshes !== void 0) {
			this._mergedMeshes.geometry.dispose();
			this._mergedMeshes.material.dispose();

			this.scene.remove(this._mergedMeshes);
		}

		this.sceneBuilder.clear();
	}
}