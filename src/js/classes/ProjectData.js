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

if (window.location.href.includes("http://127.0.0.1:3000")) {
    props["domainNameUrlVal"] = "http://127.0.0.1:3000";
    props["cdnVal"] = "/static";
}


export class ProjectData {
    static props = {
        domainNameUrlVal: props["domainNameUrlVal"],
        cdnVal: props["cdnVal"],
    }
}