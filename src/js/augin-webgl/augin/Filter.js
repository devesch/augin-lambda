export class Filter {
    static filteredTypes = new Set();
    static filteredStoreysElevation = new Set();
    static filteredStoreys = new Set();
    static filteredLayers = new Map();

    static currentFilterType = undefined;
    static currentFilterGuid = undefined;

    static toggleType(type) {
        if (this.filteredTypes.has(type)) {
            this.currentFilterType = undefined;
            this.currentFilterGuid = undefined;

            this.filteredTypes.delete(type);
        }
        else {
            this.currentFilterType = undefined;
            this.currentFilterGuid = undefined;

            this.filteredTypes.add(type);
        }
    }

    static toggleStoreyByElevation(storeys, guid) {
        const itemIndex = storeys.findIndex(storey => storey.guid === guid);

        if (itemIndex === -1) {
            console.error(`Storey "${guid}" not found!`);
            return;
        }

        if (this.filteredStoreysElevation.has(itemIndex)) {
            this.currentFilterType = undefined;
            this.currentFilterGuid = undefined;

            this.filteredStoreysElevation.delete(itemIndex);
        }
        else {
            this.currentFilterType = undefined;
            this.currentFilterGuid = undefined;

            this.filteredStoreysElevation.add(itemIndex);
        }
    }

    static toggleStorey(guid) {
        if (this.filteredStoreys.has(guid)) {
            this.currentFilterType = undefined;
            this.currentFilterGuid = undefined;

            this.filteredStoreys.delete(guid);
        }
        else {
            this.currentFilterType = undefined;
            this.currentFilterGuid = undefined;

            this.filteredStoreys.add(guid);
        }
    }

    static toggleLayer(guid, elementsGuid) {
        if (this.filteredLayers.has(guid)) {
            this.currentFilterType = undefined;
            this.currentFilterGuid = undefined;

            this.filteredLayers.delete(guid);
        }
        else {
            this.currentFilterType = "layer";
            this.currentFilterGuid = guid;

            this.filteredLayers.set(guid, elementsGuid);
        }
    }

    static has(element) {
        let hasStoreyElevation = false;
        const filteredStoreysElevationArray = [...this.filteredStoreysElevation];
        if (filteredStoreysElevationArray.length !== 0) {
            hasStoreyElevation = element.storeysId.every(index => filteredStoreysElevationArray.includes(index));
        }

        let hasLayer = false;
        if (element.layerGuid !== undefined) {
            hasLayer = this.filteredLayers.has(element.layerGuid);
        }
        else {
            if (this.currentFilterType === "layer") {
                const values = this.filteredLayers.get(this.currentFilterGuid);
                hasLayer = values && values.includes(element.guid);
                if (hasLayer) {
                    element.layerGuid = this.currentFilterGuid;
                }
            }
            else {
                const foundEntry = [...this.filteredLayers.entries()].find(([key, value]) => value.includes(element.guid));
                if (foundEntry) {
                    hasStorey = true;
                    element.layerGuid = foundEntry[0];
                }
            }
        }

        return this.filteredTypes.has(element.ifcType) ||
            hasStoreyElevation ||
            this.filteredStoreys.has(element.storey) ||
            hasLayer;
    }
}