import {
    ProjectData
} from "./classes/ProjectData.js";

export async function apiCaller(apiFunction, postData) {
    var response = await request(ProjectData.props.domainNameUrlVal + "/api/" + apiFunction, "POST", {
        "Content-Type": "application/x-www-form-urlencoded"
    }, postData, true);
    if ("success" in response) {
        console.log(apiFunction + " RESPONSE SUCCESS -> " + response["success"])
    }
    if ("error" in response) {
        console.log(apiFunction + " RESPONSE ERROR -> " + response["error"])
    }
    console.log(apiFunction + " RESPONSE EVENT -> " + response["event"])
    return response
}

export async function request(url, method = "GET", headers = {}, postData = {}, expected_json_res = true) {
    let myHeaders = new Headers();
    if (headers) {
        for (const property in headers) {
            myHeaders.append(property, headers[property]);
        }
    }

    let body_data = "";
    if (method !== "GET" && headers["Content-Type"]) {
        if (headers["Content-Type"] === "application/json") {
            body_data = JSON.stringify(postData);
        } else if (headers["Content-Type"] === "application/x-www-form-urlencoded") {
            body_data = new URLSearchParams();
            for (const property in postData) {
                body_data.append(property, postData[property]);
            }
        }
    }


    var requestOptions = {
        method: method,
        headers: myHeaders,
        body: body_data,
        redirect: 'follow',
        mode: 'no-cors'
    };
    if (method == "GET") {
        var requestOptions = {
            method: method,
            headers: myHeaders,
            redirect: 'follow',
            mode: 'no-cors'
        };
    }
    console.log("requestOptions ", requestOptions);
    const response = await fetch(url, requestOptions);
    console.log("request response ", response);
    console.log(response.status);
    if (response.status != 200) {
        //window.location = ProjectData.props.domainNameUrlVal + "/user_exit/";
        return "error";
    }

    if (expected_json_res) {
        return await response.json();
    } else {
        return await response.text();
    }
}