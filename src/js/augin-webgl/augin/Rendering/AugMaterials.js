import { Color, DoubleSide, MeshStandardMaterial, ShaderMaterial } from "../../threejs/three.module.js";

export class AugMaterials {
  constructor(viewer) {
    this._viewer = viewer;
    this.opaqueMaterial = this.createOpaque();
    this.transparentMaterial = this.createTransparent();
  }

  createOpaque() {
    const material = new MeshStandardMaterial({
      color: new Color(0xcccccc),
      vertexColors: true,
      flatShading: false,
      side: DoubleSide,
      roughness: this._viewer.settings.materials.render.roughness,
      metalness: this._viewer.settings.materials.render.metalness
    });

    return material;
  }

  createTransparent() {
    const mat = this.createOpaque();
    mat.transparent = true;
    mat.shininess = 70;
    return mat;
  }

  createIsolationMaterial(color = new Color(0xffffff), opacity = 0.5) {
    return new ShaderMaterial({
      uniforms: {
        opacity: { value: opacity },
        color: { value: color }
      },
      vertexColors: true,
      transparent: true,
      clipping: true,
      vertexShader: `
      #include <common>
      #include <logdepthbuf_pars_vertex>
      #include <clipping_planes_pars_vertex>

      void main() {
        #include <begin_vertex>
        #include <project_vertex>
        #include <clipping_planes_vertex>
        #include <logdepthbuf_vertex>

        // ORDERING
        gl_Position.z = 1.0f;
      }
      `,
      fragmentShader: `
      #include <clipping_planes_pars_fragment>
      uniform float opacity;
      uniform vec3 color;

      void main() {
        #include <clipping_planes_fragment>

        gl_FragColor = vec4(color, opacity);
      }
      `
    });
  }

  getOpaqueMaterial() {
    return this.opaqueMaterial;
  }

  getTransparentMaterial() {
    return this.transparentMaterial;
  }

  getMaterial(useAlpha) {
    return useAlpha ? this.getTransparentMaterial() : this.getOpaqueMaterial();
  }

  setClipPlanes(clipPlanes) {
    this.opaqueMaterial.clippingPlanes = clipPlanes;
    this.transparentMaterial.clippingPlanes = clipPlanes;
  }

  applyWireframe(value) {
    this.opaqueMaterial.wireframe = value;
    this.transparentMaterial.wireframe = value;
  }
}