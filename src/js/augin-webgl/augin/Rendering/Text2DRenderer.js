import { CSS2DObject, CSS2DRenderer } from '../../threejs/jsm/renderers/CSS2DRenderer.js';

export class Text2DRenderer {
    constructor(viewer, container) {
        this.viewer = viewer;
        this.container = container;
        this.settings = viewer.settings;
        this.labelRenderer = new CSS2DRenderer();
        this.labels = [];
        this.text = this.labelRenderer.domElement;

        this.labelRenderer.setSize(container.clientWidth, container.clientHeight);
        this.text.style.position = "absolute";
        this.text.style.top = "0px";
        this.text.style.pointerEvents = "none";
        container.appendChild(this.text);
        this.labelRenderer.render(viewer.scene, viewer.getCamera());
    }

    create(object, position, text) {
        var div = document.createElement('div');
        div.textContent = text;
        div.style.backgroundColor = this.settings.text.measure.backgroundColor;
        div.style.color = this.settings.text.measure.color;
        div.style.padding = this.settings.text.measure.padding;
        div.style.borderRadius = this.settings.text.measure.borderRadius;
        div.style.fontFamily = this.settings.text.measure.fontFamily;
        div.style.fontWeight = this.settings.text.measure.fontWeight;
        div.style.fontSize = this.settings.text.measure.fontSize;

        var label = new CSS2DObject(div);
        label.position.set(position.x, position.y, position.z);
        object.add(label);

        this.labels.push(label);
        this.render();

        return this.labels.length - 1;
    }

    remove(object, index) {
        object.remove(this.labels[index]);
        this.render();
    }

    render() {
        this.labelRenderer.setSize(this.container.clientWidth, this.container.clientHeight);
        this.labelRenderer.render(this.viewer.scene, this.viewer.getCamera());
    }
}