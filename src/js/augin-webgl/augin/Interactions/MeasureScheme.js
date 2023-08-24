export class MeasureScheme {
    constructor(viewer)
    {
        this.viewer = viewer;
    }

    onMainAction(action)
    {
        if (!(action == null ? void 0 : action.object)) return;

        this.viewer.measure.setPoint(action.intersection.point);
    }
}