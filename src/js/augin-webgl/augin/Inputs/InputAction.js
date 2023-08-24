export class InputAction {
    constructor(type, position, raycast) {
      this.type = type;
      this._intersection = raycast.getIntersection(position);
    }

    get intersection() {
      return this._intersection;
    }

    get object() {
      return this._intersection == void 0 ? void 0 : this._intersection.object;
    }
}