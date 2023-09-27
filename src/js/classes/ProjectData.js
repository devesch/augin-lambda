import environment_variables from "../../../.vscode/enviroment_variables.json"

var props = {
    domainNameUrlVal: `https://web.augin.app`,
    cdnVal: `https://cdn.augin.app`,
}


if (location.href.includes("dev-")) {
    props = {
        domainNameUrlVal: `https://web.augin.app`,
        cdnVal: `https://cdn.augin.app`,
    }
}

export class ProjectData {
    // GENERAL //
    static props = {
        domainNameUrlVal: props["domainNameUrlVal"],
        cdnVal: props["cdnVal"],
    }

    static settings = {
        colors: {
            lightBlue: new Color(0xadd8e6),
            veryLightBlue: new Color(0xe0f7fa),
            ultraLightBlue: new Color(0xf0faff),
            sphereMeasureBlue: new Color(0x0590CC)
        }
    }

    static viewerSettings = {
        background: {
            hdrUrl: this.props.cdnVal + "/assets/web_view/tqs-viewer-skybox.hdr",
            color1: this.settings.colors.lightBlue,
            color2: this.settings.colors.ultraLightBlue
        },
        camera: {
            cameraSpeed: 0.2,
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
        sunLights: [{
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
                roughness: 0.75,
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
                    color: this.settings.colors.sphereMeasureBlue,
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
        showStats: false
    }
}