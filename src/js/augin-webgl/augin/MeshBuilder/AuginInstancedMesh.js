export class AuginInstancedMesh {
    constructor(geometry, material) {
		this.geometry = geometry,
		this.material = material,
		this.numberOfObjects = 0,
		this.matrices = []
	}

	increment (matrix)
	{
		this.numberOfObjects++;
		this.matrices.push(matrix);
	}
}