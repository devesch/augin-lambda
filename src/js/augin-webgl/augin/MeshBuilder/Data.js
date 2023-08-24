export class Data
{
    static instanceElements = {};
    static mergeIndices = [];
    static mergeElements = [];

    static clear () {
        this.instanceElements = {};
        this.mergeIndices = [];
        this.mergeElements = [];
    }

    static addInstanceElement(instanceMeshId, elementIndex)
    {
        if (instanceMeshId in Data.instanceElements) {
            Data.instanceElements[instanceMeshId].push(elementIndex);
        }
        else {
            Data.instanceElements[instanceMeshId] = [elementIndex];
        }
    }

    static getInstanceMesh(instanceMeshId, instanceId)
    {
        const instanceElements = Data.instanceElements[instanceMeshId];

        return instanceElements[instanceId];
    }

    static addMergeMeshAndElement(indexStart, elementIndex)
    {
        Data.mergeIndices.push(indexStart);
        Data.mergeElements.push(elementIndex);
    }

    static getMergeMesh(faceIndex)
    {
        function binarySearch(array, target) {
            let left = 0;
            let right = array.length - 1;
            while (left <= right) {
                const mid = Math.floor((left + right) / 2);
                let currentIndex = target - array[mid];

                if (currentIndex > 0) {
                    left = mid + 1;
                } else if (currentIndex < 0) {
                    right = mid - 1;
                } else {
                    return mid;
                }
            }
            return left - 1;
        }

        const index = binarySearch(Data.mergeIndices, faceIndex * 3);
        return Data.mergeElements[index];
    }
}