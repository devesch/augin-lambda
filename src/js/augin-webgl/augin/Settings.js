import { Color, Vector3 } from "../threejs/three.module.js";

export class Settings {
    static defaultSettings = {
        background: {
            hdrUrl: "augin-webgl/resources/viewer-skybox.hdr",
            color1: new Color(0xadd8e6),
            color2: new Color(0xf0faff)
        },
        camera: {
            cameraSpeed: 1.0,
            orbitSpeed: 1.0,
            dollySpeed: 1.0,
            truckSpeed: 2.0,
            shiftMultiplierSpeed: 2.0,
            sphere: {
                color: 0xffffff
            }
        },
        skylight: {
            skyColor: new Color().setHSL(0, 0, 0.95),
            groundColor: new Color().setHSL(0, 0, 0.95),
            intensity: 1
        },
        sunLights: [
            {
                position: new Vector3(-45, 40, -23),
                color: new Color().setHSL(1, 1, 1),
                intensity: 0.3
            },
            {
                position: new Vector3(45, 40, 23),
                color: new Color().setHSL(1, 1, 1),
                intensity: 0.3
            }
        ],
        materials: {
            render: {
                roughness: 0.65,
                metalness: 0
            },
            isolation: {
                color: new Color(0xdddddd),
                opacity: 0.1
            },
            outline: {
                intensity: 3,
                blur: 2,
                color: new Color(0x00ffff)
            },
            measure: {
                sphere: {
                    color: new Color(0x0590CC),
                    size: 0.25
                },
                line: {
                    color: new Color(0xfffff),
                    width: 10
                }
            }
        },
        text: {
            measure: {
                backgroundColor: 'rgba(0, 0, 0, 0.2)',
                color: 'white',
                padding: '12px',
                borderRadius: '10px',
                fontFamily: '',
                fontWeight: '',
                fontSize: '16px'
            }
        },
        quality: {
            maximumLowFps: 15,
            secondsInLowFps: 5,
        },
        showStats: true,
    }

    constructor(settings = null) {
        if (settings === null) {
            this.current = Settings.defaultSettings;
        } else {
            this.current = settings;
        }
    }

    get background() {
        return this.current.background;
    }

    get camera() {
        return this.current.camera;
    }

    get skylight() {
        return this.current.skylight;
    }

    get sunLights() {
        return this.current.sunLights;
    }

    get materials() {
        return this.current.materials;
    }

    get text() {
        return this.current.text;
    }

    get quality() {
        return this.current.quality;
    }

    get showStats() {
        return this.current.showStats;
    }

    set showStats(value) {
        this.current.showStats = value;
    }
}