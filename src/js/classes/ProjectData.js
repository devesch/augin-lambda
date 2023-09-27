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
}