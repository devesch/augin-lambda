import {
    ProjectData
} from './classes/ProjectData.js';
import {
    apiCaller
} from "./api.js";
import {
    auginComponent,
    Axis,
    Side
} from "./augin-webgl/auginComponent.js";
import noUiSlider from "./nouislider.min.mjs";
import {
    formatFileSize
} from "./helpers/FileHelper.js";

import {
    openModal
} from "./index.js"

let isWebviewPage = location.href.includes("/webview/");

const webView = {
    component: undefined,
    panels: {
        explorePanel: undefined,
        cutPanel: undefined,
        menuPanel: undefined
    }
};

const TOGGLE_DETAILS_BUTTON = document.querySelector(".toggle-details-button");
// TOGGLE_DETAILS_BUTTON.addEventListener("click", function() {
//     showPropertyWindow(true);
// });

export async function showPropertyButton() {
    TOGGLE_DETAILS_BUTTON.classList.add("show");
}

export async function hidePropertyButton() {
    TOGGLE_DETAILS_BUTTON.classList.remove("show");
}
export async function preventLandscapeOrientation() {


    let element = document.querySelector("html");

    if (screen.orientation && screen.orientation.lock) {

        screen.orientation.lock("portrait-primary")

        screen.orientation.addEventListener("change", () => {
            if (document.documentElement.requestFullscreen)
                element.requestFullscreen();
            else if(document.documentElement.webkitRequestFullScreen)
                element.webkitRequestFullScreen();
            else if (element.msRequestFullscreen) // for Internet Explorer
                element.msRequestFullscreen();

            screen.orientation.lock("portrait-primary");
        });
    } else {
        console.warn("Device doesn't have screen.orientation");
    }

}

if (isWebviewPage) {
    preventLandscapeOrientation();

    // CUT WINDOW

    // DOUBLE RANGE SLIDER

    var sliderSettings = {
        start: [-1, 1], // Initial range values
        connect: true,
        range: {
            min: -1,
            max: 1
        },
        step: 0.01,
        cssPrefix: 'measureSlider-'
    };

    var xSlider = document.getElementById("x_slider");
    var ySlider = document.getElementById("y_slider");
    var zSlider = document.getElementById("z_slider");

    noUiSlider.create(xSlider, sliderSettings);
    noUiSlider.create(ySlider, sliderSettings);
    noUiSlider.create(zSlider, sliderSettings);

    const bottomMenuContainer = document.getElementById("web_view_bottom_menu_container");

    const loading = document.getElementById("loading");
    const loadingTitle = document.getElementById("loading_title");
    const loadingProgressText = document.getElementById("loading_progress_text");
    const loadingProgress = document.getElementById("loading_progress");

    // MENU BUTTONS
    const explorePanel = {
        viewer: document.getElementById("web_view_folders"),
        button: document.getElementById("explore")
    };
    webView.panels.explorePanel = explorePanel;

    const cutPanel = {
        viewer: document.getElementById("web_view_cut_container"),
        button: document.getElementById("cut")
    };
    webView.panels.cutPanel = cutPanel;

    const measureButton = document.getElementById("measure");
    const isolationButton = document.getElementById("isolation");
    const measureRemoveButton = document.getElementById("measure_remove_button");

    const menuPanel = {
        viewer: document.getElementById("web_view_menu"),
        button: document.getElementById("menu")
    };
    webView.panels.menuPanel = menuPanel;

    var mainElement = document.querySelector("main#wrapper");
    var projectId = document.getElementById("project_id_input").value;
    var guid = document.getElementById("guid_input").value;
    var aug_zip_url = document.getElementById("aug_zip_url_input").value;
    var last_selected_element = document.getElementById("last_selected_element_input");
    var property_ids = document.getElementById("property_ids_input");
    var element_data_encoded = document.getElementById("element_data_encoded_input");
    var element_type = document.getElementById("element_type_input");
    var ifc_filesize = formatFileSize(document.getElementById("ifc_filesize_input").value);
    var quality = document.getElementById("quality_input").value;

    bottomMenuContainer.style.display = "none";
    measureRemoveButton.style.display = "none";

    openExplore(false);
    closePanel(menuPanel);
    closePanel(cutPanel);

    webView.component = new auginComponent();
    mainElement.appendChild(webView.component.getCanvas());

    webView.component.updateSettings(ProjectData.viewerSettings);
    webView.component.showStats(ProjectData.viewerSettings.showStats);
    if (quality.toLowerCase() == "hd")
        webView.component.addLowFpsEvent(onLowFps);
    webView.component.load(aug_zip_url, {
        id: projectId + quality,
        onLoadedEvent: onLoaded,
        onProgressEvent: onProgress
    });

    webView.component.addSelectObjectEvent(async (event) => {
        let get_element_data_response = await apiCaller("get_element_data", {
            "project_id": projectId,
            "element_id": event.guid
        });
        console.log("get_element_data_response", get_element_data_response);
        if ("redirect" in get_element_data_response) {
            window.location = get_element_data_response["redirect"];
            return;
        }

        closePanel(menuPanel);
        openDefaultFoldersHierarchy(projectId, event.guid);
        showPropertyButton();

        // Check if the media query is true
        if (isDesktop()) {
            // Then trigger an alert
            openPanel(webView.panels.explorePanel);
        };
        openProperty(projectId, get_element_data_response["success"]["property_ids"], get_element_data_response["success"]["element_data_encoded"], get_element_data_response["success"]["element_type"], event.guid);
    });

    webView.component.addDeselectObjectEvent(() => {
        const propertyData = document.getElementById("property_data");
        propertyData.innerHTML = "";
        showPropertyWindow(false);
        hidePropertyButton();
    });

    webView.component.addMeasureDistanceEvent(() => {
        measureRemoveButton.style.display = "";
    });

    function onLoaded() {
        webView.component.consoleInstancesQtd();
        loading.remove();
        openStoreyFilter(projectId, JSON.stringify(webView.component.getStoreys()));
        openTypeFilter(projectId, webView.component.getTypes());

        if (guid) {
            openProperty(projectId, property_ids.value, element_data_encoded.value, element_type.value, guid);
            openExplore(true);
            if (webView.component.selectObject(guid)) {
                webView.component.focusSelectedObject();
                fixWebviewPanelMargins();
                showPropertyButton();
            }
            updateLastSelectedElement(last_selected_element.value);
        }

        xSlider.noUiSlider.on("update", function (values, handle) {
            webView.component.changeCut(Axis.X, Side.Left, values[0])
            webView.component.changeCut(Axis.X, Side.Right, values[1])
        });

        ySlider.noUiSlider.on("update", function (values, handle) {
            webView.component.changeCut(Axis.Y, Side.Left, values[0])
            webView.component.changeCut(Axis.Y, Side.Right, values[1])
        });

        zSlider.noUiSlider.on("update", function (values, handle) {
            webView.component.changeCut(Axis.Z, Side.Left, values[0])
            webView.component.changeCut(Axis.Z, Side.Right, values[1])
        });

        bottomMenuContainer.style.display = "";

        var resetButton = document.getElementById('web_view_cut_reset_button');

        resetButton.addEventListener('click', function () {
            // Reset the slider values to the initial values
            resetCut();
        });

        fixWebviewPanelMargins();

        var timeout = false;
        window.addEventListener('resize', function (event) {
            // clear the timeout
            clearTimeout(timeout);
            // start timing for event "completion"
            timeout = setTimeout(fixWebviewPanelMargins, 500);
        }, true);

        window.addEventListener('orientationchange', () => fixWebviewPanelMargins, false);

    }

    function onProgress(event) {
        if (event.progressType === "download") {
            loadingTitle.innerText = `Baixando...  (${ifc_filesize})`;
        } else {
            loadingTitle.innerText = `Carregando... (${ifc_filesize})`;
        }
        loadingProgress.value = (100 * event.progress).toFixed(2);
        loadingProgressText.innerText = loadingProgress.value + "%";
        if (loading.style.display === "none") {
            loading.style.display = "";
        }
    }

    function onLowFps() {
        console.log("LOW FPS");
        openModal('.modal.update-quality-modal');
    }

    function openExplore(active) {
        if (active) {
            closePanel(menuPanel);
            openPanel(explorePanel);
        } else {
            closePanel(explorePanel);
        }
        // showPropertyWindow(active);
    }

    async function openTypeFilter(projectId, types) {
        var types_div = document.getElementById("types");
        var open_type_filter_response = await apiCaller("open_type_filter", {
            'project_id': projectId,
            'types': types,
        });
        console.log("open_type_filter_response ", open_type_filter_response);
        if ("redirect" in open_type_filter_response) {
            window.location = open_type_filter_response["redirect"];
            return
        }
        types_div.innerHTML = open_type_filter_response["success"];
    }

    async function openStoreyFilter(projectId, storeys) {
        var storeys_div = document.getElementById("storeys");
        var open_storey_filter_response = await apiCaller("open_storey_filter", {
            'project_id': projectId,
            'storeys': storeys,
        });
        console.log("open_storey_filter_response ", open_storey_filter_response);
        if ("redirect" in open_storey_filter_response) {
            window.location = open_storey_filter_response["redirect"];
            return
        }
        storeys_div.innerHTML = open_storey_filter_response["success"];
    }

    function toggleExplorePanel() {
        openExplore(panelIsClosed(explorePanel));
        if (!isDesktop()) {
            showPropertyWindow(false);
            closePanel(cutPanel);
        }
    }

    function resetCut() {
        xSlider.noUiSlider.reset();
        ySlider.noUiSlider.reset();
        zSlider.noUiSlider.reset();
    }

    explorePanel.viewer.querySelector(".js-close-panel-button").addEventListener("click", function () {
        openExplore(false);
    });

    menuPanel.viewer.querySelector(".js-close-panel-button").addEventListener("click", function () {
        closePanel(menuPanel);
    });

    explorePanel.button.addEventListener("click", toggleExplorePanel);

    cutPanel.viewer.querySelector(".js-close-panel-button").addEventListener("click", function () {
        closePanel(cutPanel);
    });

    cutPanel.button.addEventListener("click", function () {
        if (panelIsClosed(cutPanel)) {
            openPanel(cutPanel);
            showPropertyWindow(false);
        } else {
            closePanel(cutPanel);
            // showPropertyWindow(true);
        }
        if (!isDesktop()) {
            showPropertyWindow(false);
            closePanel(menuPanel);
            closePanel(explorePanel);
        }
    });

    const menuMobileButton = document.querySelector(".menu-mobile-button");
    if (menuMobileButton) {
        menuMobileButton.addEventListener("click", function () {
            closePanel(menuPanel);
            closePanel(cutPanel);
            closePanel(explorePanel);
            showPropertyWindow(false);
        });
    }

    measureButton.addEventListener("click", function () {
        const active = webView.component.toggleMeasure();
        active ? this.classList.add("active") : this.classList.remove("active");
    });

    measureRemoveButton.addEventListener("click", function () {
        webView.component.removeMeasure();
        measureRemoveButton.style.display = "none";
    });

    isolationButton.addEventListener("click", function () {
        const active = webView.component.toggleIsolation();
        active ? this.classList.add("active") : this.classList.remove("active");
    });

    menuPanel.button.addEventListener("click", function () {
        if (panelIsClosed(menuPanel)) {
            openExplore(false);
            openPanel(menuPanel);
        } else {
            closePanel(menuPanel);
        }

        if (!isDesktop()) {
            showPropertyWindow(false);
            closePanel(cutPanel);
        }
    });
}

export async function showPropertyWindow(value) {
    const webViewProperties = document.getElementById("web_view_properties");
    const propertyData = document.getElementById("property_data");
    if (value === true) {
        console.warn("showPropertyWindow true");
        webViewProperties.style.display = propertyData.innerHTML != "" ? "" : "none";
        if (!panelIsClosed(webView.panels.cutPanel)) {
            closePanel(webView.panels.cutPanel);
        }
    } else {
        webViewProperties.style.display = "none";
    }
}

window.testToggleStorey = testToggleStorey;

async function testToggleStorey() {
    await webView.component.toggleStorey("2PRsEndNz5nw9HXieK8W9Y");
}

export async function getFilterGuids(project_id, type, entity_id = "") {
    console.log("running getFilterGuids");
    console.log("type ", type);
    console.log("guid ", entity_id);
    showLoadingAnimation();
    if (type == "layer") {
        var get_filter_guids_response = await apiCaller("get_filter_guids", {
            'project_id': project_id,
            'type': type,
            'entity_id': entity_id
        });
        console.log("get_filter_guids_response", get_filter_guids_response);
        if ("redirect" in get_filter_guids_response) {
            window.location = get_filter_guids_response["redirect"];
        }
        await toggleFilter(type, {
            guid: entity_id,
            elementsGuid: get_filter_guids_response["success"]
        });
    } else {
        await toggleFilter(type, {
            guid: entity_id
        });
    }
}

export async function openSites(accordionElement, project_id) {
    console.log("running openSites");
    let response_div = document.getElementById("accordion_content_" + project_id);
    updateLastSelectedElement("accordion_header_" + project_id);

    if (response_div.innerHTML != "") {
        response_div.innerHTML = ""
        return
    }
    let open_sites_response = await apiCaller("open_sites", {
        'project_id': project_id
    });
    console.log("open_sites_response ", open_sites_response);
    if ("redirect" in open_sites_response) {
        window.location = open_sites_response["redirect"];
        return
    }

    response_div.innerHTML = open_sites_response["success"];

    if (response_div.innerHTML == "") {
        accordionElement.querySelector("img").src = accordionElement.querySelector("img").src.replace("chevron_right", "chevron_hyphen");
        accordionElement.classList.add("empty-accordion");
    }

}

export async function openBuildings(accordionElement, project_id, site_id, property_ids, element_data_encoded) {
    console.log("running openBuildings");
    let show_guid = document.getElementById("show_guid_input").value;
    let response_div = document.getElementById("accordion_content_" + project_id + site_id);
    updateLastSelectedElement("accordion_header_" + project_id + site_id);
    
    if (response_div.innerHTML != "") {
        response_div.innerHTML = ""
        return
    }
    let open_buildings_response = await apiCaller("open_buildings", {
        'project_id': project_id,
        'site_id': site_id,
        'show_guid': show_guid
    });
    console.log("open_buildings_response ", open_buildings_response);
    if ("redirect" in open_buildings_response) {
        window.location = open_buildings_response["redirect"];
        return
    }
    response_div.innerHTML = open_buildings_response["success"];
    if (response_div.innerHTML == "") {
        accordionElement.querySelector("img").src = accordionElement.querySelector("img").src.replace("chevron_right", "chevron_hyphen");
        accordionElement.classList.add("empty-accordion");
    }
    if (webView.component.selectObject(site_id)) {
        webView.component.focusSelectedObject();
        showPropertyButton();
    }
}

export async function openStoreys(accordionElement, project_id, site_id, building_id, property_ids, element_data_encoded) {
    console.log("running openStoreys");
    let show_guid = document.getElementById("show_guid_input").value;
    let response_div = document.getElementById("accordion_content_" + project_id + site_id + building_id);
    updateLastSelectedElement("accordion_header_" + project_id + site_id + building_id);
    
    if (response_div.innerHTML != "") {
        response_div.innerHTML = ""
        return
    }
    let open_storeys_response = await apiCaller("open_storeys", {
        'project_id': project_id,
        'site_id': site_id,
        'building_id': building_id,
        'show_guid': show_guid
    });
    console.log("open_storeys_response ", open_storeys_response);
    if ("redirect" in open_storeys_response) {
        window.location = open_storeys_response["redirect"];
        return
    }
    response_div.innerHTML = open_storeys_response["success"];
    if (response_div.innerHTML == "") {
        accordionElement.querySelector("img").src = accordionElement.querySelector("img").src.replace("chevron_right", "chevron_hyphen");
        accordionElement.classList.add("empty-accordion");
    }


}

export async function openCategorys(accordionElement, project_id, site_id, building_id, storey_id, property_ids, element_data_encoded) {
    let show_guid = document.getElementById("show_guid_input").value;
    let response_div = document.getElementById("accordion_content_" + project_id + site_id + building_id + storey_id);
    updateLastSelectedElement("accordion_header_" + project_id + site_id + building_id + storey_id);

    if (response_div.innerHTML != "") {
        response_div.innerHTML = ""
        return;
    }
    let open_categorys_response = await apiCaller("open_categorys", {
        'project_id': project_id,
        'site_id': site_id,
        'building_id': building_id,
        'storey_id': storey_id,
        'show_guid': show_guid
    });
    if ("redirect" in open_categorys_response) {
        window.location = open_categorys_response["redirect"];
        return;
    }
    response_div.innerHTML = open_categorys_response["success"];
    if (response_div.innerHTML == "") {
        accordionElement.querySelector("img").src = accordionElement.querySelector("img").src.replace("chevron_right", "chevron_hyphen");
        accordionElement.classList.add("empty-accordion");
    }
}

export async function openElements(page_direction, project_id, site_id, building_id, storey_id, category_id, page_index, show_more_div_id = "") {
    let show_guid = document.getElementById("show_guid_input").value;
    let pagination_size = document.getElementById("pagination_size_input").value;
    let response_div = document.getElementById("accordion_content_" + project_id + site_id + building_id + storey_id + category_id);

    if (page_direction != "end" && page_direction != "begin") {
        updateLastSelectedElement("accordion_header_" + project_id + site_id + building_id + storey_id + category_id);
        if (response_div.innerHTML != "") {
            response_div.innerHTML = ""
            return;
        }
    }
    let open_elements_response = await apiCaller("open_elements", {
        'project_id': project_id,
        'site_id': site_id,
        'building_id': building_id,
        'storey_id': storey_id,
        'category_id': category_id,
        'show_guid': show_guid,
        'pagination_size': pagination_size,
        'element_page_index': page_index,
        'element_page_direction': page_direction
    });
    if ("redirect" in open_elements_response) {
        window.location = open_elements_response["redirect"];
        return;
    }

    if (page_direction == "begin") {
        response_div.innerHTML = open_elements_response["success"] + response_div.innerHTML;
        let show_more_div = document.getElementById(show_more_div_id);
        show_more_div.remove();
    } else if (page_direction == "end") {
        response_div.innerHTML += open_elements_response["success"];
        let show_more_div = document.getElementById(show_more_div_id);
        show_more_div.remove();
    } else {
        response_div.innerHTML = open_elements_response["success"];
    }
}

export async function openSubElements(page_direction, project_id, site_id, building_id, storey_id, category_id, element_id, property_ids, element_data_encoded, element_has_sub_elements, page_index = "1", show_more_div_id = "") {
    let show_guid = document.getElementById("show_guid_input").value;
    let pagination_size = document.getElementById("pagination_size_input").value;

    let response_div = document.getElementById("accordion_content_" + project_id + site_id + building_id + storey_id + category_id + element_id);

    if (page_direction != "end" && page_direction != "begin") {
        updateLastSelectedElement("accordion_header_" + project_id + site_id + building_id + storey_id + category_id + element_id);

        if (isDesktop()) {
            openProperty(project_id, property_ids, element_data_encoded, "element", element_id);
            console.log("OpenProperty only on desktop");
        } else {
            console.warn("Close explore panel");
            closePanel(webView.panels.explorePanel);
        }

        if (webView.component.selectObject(element_id)) {
            webView.component.focusSelectedObject();
            showPropertyButton();
        }

        if (element_has_sub_elements == "False") {
            return;
        }
        if (response_div.innerHTML != "") {
            response_div.innerHTML = ""
            return;
        }
    }

    let open_sub_elements = await apiCaller("open_sub_elements", {
        'project_id': project_id,
        'site_id': site_id,
        'building_id': building_id,
        'storey_id': storey_id,
        'category_id': category_id,
        'element_id': element_id,
        'show_guid': show_guid,
        'pagination_size': pagination_size,
        'sub_element_page_index': page_index,
        'sub_element_page_direction': page_direction
    });

    if ("redirect" in open_sub_elements) {
        window.location = open_sub_elements["redirect"];
        return;
    }
    if (page_direction == "begin") {
        response_div.innerHTML = open_sub_elements["success"] + response_div.innerHTML;
        let show_more_div = document.getElementById(show_more_div_id);
        show_more_div.remove();
    } else if (page_direction == "end") {
        response_div.innerHTML += open_sub_elements["success"];
        let show_more_div = document.getElementById(show_more_div_id);
        show_more_div.remove();
    } else {
        response_div.innerHTML = open_sub_elements["success"];
    }
}

export async function openSubSubElements(page_direction, project_id, site_id, building_id, storey_id, category_id, element_id, sub_element_id, property_ids, element_data_encoded, sub_element_has_sub_sub_elements, page_index = "1", show_more_div_id = "") {
    let show_guid = document.getElementById("show_guid_input").value;
    let pagination_size = document.getElementById("pagination_size_input").value;
    let response_div = document.getElementById("accordion_content_" + project_id + site_id + building_id + storey_id + category_id + element_id + sub_element_id);

    if (page_direction != "end" && page_direction != "begin") {
        updateLastSelectedElement("accordion_header_" + project_id + site_id + building_id + storey_id + category_id + element_id + sub_element_id);

        if (isDesktop()) {
            openProperty(project_id, property_ids, element_data_encoded, "sub_element", sub_element_id);
            console.log("OpenProperty only on desktop");
        } else {
            console.warn("Close explore panel");
            closePanel(webView.panels.explorePanel);
        }

        if (webView.component.selectObject(sub_element_id)) {
            webView.component.focusSelectedObject();
            showPropertyButton();
        }
        if (sub_element_has_sub_sub_elements == "False") {
            return;
        }
        if (response_div.innerHTML != "") {
            response_div.innerHTML = ""
            return;
        }
    }

    let open_sub_sub_elements = await apiCaller("open_sub_sub_elements", {
        'project_id': project_id,
        'site_id': site_id,
        'building_id': building_id,
        'storey_id': storey_id,
        'category_id': category_id,
        'element_id': element_id,
        'sub_element_id': sub_element_id,
        'show_guid': show_guid,
        'pagination_size': pagination_size,
        'sub_sub_element_page_index': page_index,
        'sub_sub_element_page_direction': page_direction
    });

    if ("redirect" in open_sub_sub_elements) {
        window.location = open_sub_sub_elements["redirect"];
        return;
    }
    if (page_direction == "begin") {
        response_div.innerHTML = open_sub_sub_elements["success"] + response_div.innerHTML;
        let show_more_div = document.getElementById(show_more_div_id);
        show_more_div.remove();
    } else if (page_direction == "end") {
        response_div.innerHTML += open_sub_sub_elements["success"];
        let show_more_div = document.getElementById(show_more_div_id);
        show_more_div.remove();
    } else {
        response_div.innerHTML = open_sub_sub_elements["success"];
    }
}

export async function openNanoElements(page_direction, project_id, site_id, building_id, storey_id, category_id, element_id, sub_element_id, sub_sub_element_id, property_ids, element_data_encoded, sub_sub_element_has_nano_elements, page_index = "1", show_more_div_id = "") {
    let show_guid = document.getElementById("show_guid_input").value;
    let pagination_size = document.getElementById("pagination_size_input").value;
    let response_div = document.getElementById("accordion_content_" + project_id + site_id + building_id + storey_id + category_id + element_id + sub_element_id + sub_sub_element_id);

    if (page_direction != "end" && page_direction != "begin") {
        updateLastSelectedElement("accordion_header_" + project_id + site_id + building_id + storey_id + category_id + element_id + sub_element_id + sub_sub_element_id);

        if (isDesktop()) {
            openProperty(project_id, property_ids, element_data_encoded, "sub_sub_element", sub_sub_element_id);
            console.log("OpenProperty only on desktop");
        } else {
            console.warn("Close explore panel");
            closePanel(webView.panels.explorePanel);
        }

        if (webView.component.selectObject(sub_sub_element_id)) {
            webView.component.focusSelectedObject();
            showPropertyButton();
        }
        if (sub_sub_element_has_nano_elements == "False") {
            return;
        }
        if (response_div.innerHTML != "") {
            response_div.innerHTML = ""
            return;
        }
    }

    let open_nano_elements = await apiCaller("open_nano_elements", {
        'project_id': project_id,
        'site_id': site_id,
        'building_id': building_id,
        'storey_id': storey_id,
        'category_id': category_id,
        'element_id': element_id,
        'sub_element_id': sub_element_id,
        'sub_sub_element_id': sub_sub_element_id,
        'show_guid': show_guid,
        'pagination_size': pagination_size,
        'nano_element_page_index': page_index,
        'nano_element_page_direction': page_direction
    });

    if ("redirect" in open_nano_elements) {
        window.location = open_nano_elements["redirect"];
        return;
    }
    if (page_direction == "begin") {
        response_div.innerHTML = open_nano_elements["success"] + response_div.innerHTML;
        let show_more_div = document.getElementById(show_more_div_id);
        show_more_div.remove();
    } else if (page_direction == "end") {
        response_div.innerHTML += open_nano_elements["success"];
        let show_more_div = document.getElementById(show_more_div_id);
        show_more_div.remove();
    } else {
        response_div.innerHTML = open_nano_elements["success"];
    }
}

export async function selectNanoElement(accordionElement, project_id, site_id, building_id, storey_id, category_id, element_id, sub_element_id, sub_sub_element_id, nano_element_id, property_ids, element_data_encoded) {
    console.log("Running selectNanoElement");
    updateLastSelectedElement("accordion_header_" + project_id + site_id + building_id + storey_id + category_id + element_id + sub_element_id + sub_sub_element_id + nano_element_id);
    openProperty(project_id, property_ids, element_data_encoded, "nano_element", nano_element_id);
    if (webView.component.selectObject(nano_element_id)) {
        webView.component.focusSelectedObject();
        showPropertyButton();
    }
}


export async function openProperty(project_id, property_ids, element_data_encoded = {}, element_type = "", element_id = "") {
    let property_ids_input = document.getElementById("property_ids_input");
    let response_div = document.getElementById("web_view_properties");

    property_ids_input.value = property_ids;
    let open_property_response = await apiCaller("open_property", {
        'project_id': project_id,
        'property_ids': property_ids,
        'element_data_encoded': element_data_encoded,
        'element_type': element_type,
        'element_id': element_id
    });
    console.log("open_property_response", open_property_response);
    if ("redirect" in open_property_response) {
        window.location = open_property_response["redirect"];
        return
    }

    response_div.innerHTML = open_property_response["success"];
    if (isDesktop()) {
        if (open_property_response["success"] != "") {
            console.warn(open_property_response["containers_has_info"]);
            if (open_property_response["containers_has_info"] == true) {
                showPropertyWindow(true);
            } else {
                showPropertyWindow(false);
            }
        } else {
            showPropertyWindow(false);
        }
    }

    if (response_div.innerHTML == "") {
        accordionElement.querySelector("img").src = accordionElement.querySelector("img").src.replace("chevron_right", "chevron_hyphen");
        accordionElement.classList.add("empty-accordion");
    }
}

export async function toggleSectionInputRadio(form) {

    if (form.elements.length <= 0) {
        console.error("Error: toggleSectionInputRadio, form has no elements.");
        return;
    }

    for (let i = 0; i < form.elements.length; i++) {
        if (!form.elements[i].type) {
            continue;
        }

        if (form.elements[i].type !== "radio") {
            continue;
        }

        const inputRadio = form.elements[i];

        const toggleableContentDiv = document.querySelector("#" + inputRadio.getAttribute("aria-controls"));

        if (inputRadio.checked) {
            inputRadio.setAttribute("aria-expanded", "true");
            inputRadio.setAttribute("aria-selected", "true");
            toggleableContentDiv.removeAttribute("aria-hidden");
            toggleableContentDiv.removeAttribute("hidden");
            continue;
        }

        inputRadio.setAttribute("aria-expanded", "false");
        inputRadio.setAttribute("aria-selected", "false");
        toggleableContentDiv.setAttribute("aria-hidden", "true");
        toggleableContentDiv.setAttribute("hidden", "true");
        continue;
    }
}

async function toggleFilter(type, params) {
    try {
        switch (type) {
            case "type":
                await webView.component.toggleType(params.guid);
                break;
            case "storey":
                console.log("Running toggleStorey")
                console.log("params.guid ", params.guid);
                await webView.component.toggleStorey(params.guid);
                break;
            case "layer":
                await webView.component.toggleLayer(params.guid, params.elementsGuid);
                break;
            default:
                break;
        }
    } catch (error) {
        console.error('Error occurred during toggle:', error);
    } finally {
        hideLoadingAnimation();
    }
}

function showLoadingAnimationDelay(delayMS) {
    return setTimeout(showLoadingAnimation, delayMS);
}

function clearLoadingTimer(showLoadingTimer) {
    if (showLoadingTimer === undefined) return;
    clearTimeout(showLoadingTimer);
    hideLoadingAnimation();
}

function showLoadingAnimation() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'filter-loading';
    const loadingAnimationDiv = document.createElement('div');
    loadingAnimationDiv.className = 'loading-animation';

    loadingDiv.appendChild(loadingAnimationDiv);

    var mainElement = document.querySelector("main#wrapper");
    mainElement.appendChild(loadingDiv);
}

function hideLoadingAnimation() {
    const loadingDiv = document.querySelector('.filter-loading');
    if (loadingDiv) {
        loadingDiv.parentNode.removeChild(loadingDiv);
    }
}

function updateLastSelectedElement(new_last_selected_element_id) {
    console.log("Running updateLastSelectedElement");
    let last_selected_element = document.getElementById("last_selected_element_input");
    if (last_selected_element) {
        if (last_selected_element.value) {
            let last_element = document.getElementById(last_selected_element.value);
            if (last_element) {
                last_element.style = "font-weight: unset;"
            }
        }
        last_selected_element.value = new_last_selected_element_id;
    }

    console.log("Getting new last selected element: " + new_last_selected_element_id);
    let new_last_selected_element = document.getElementById(new_last_selected_element_id);
    new_last_selected_element.style = "font-weight: bold;";
    new_last_selected_element.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    });

}

export async function openDefaultFoldersHierarchy(project_id, guid_id) {
    let showLoadingDelay = showLoadingAnimationDelay(1000);

    let web_view_folders_main_explore = document.getElementById("web_view_folders_main_explore");
    let open_default_folders_hierarchy_response = await apiCaller("open_default_folders_hierarchy", {
        'project_id': project_id,
        'guid_id': guid_id
    });
    console.log("open_default_folders_hierarchy_response", open_default_folders_hierarchy_response);

    clearLoadingTimer(showLoadingDelay);

    if ("redirect" in open_default_folders_hierarchy_response) {
        window.location = open_default_folders_hierarchy_response["redirect"];
        return
    }

    web_view_folders_main_explore.innerHTML = open_default_folders_hierarchy_response["success"];
    updateLastSelectedElement(open_default_folders_hierarchy_response["last_selected_element"])
    hideLoadingAnimation();
    // activeButton("explore");
}

export function showStats() {
    webView.component.toggleStats();
}

export async function fixWebviewPanelMargins() {
    let header = document.querySelector("header");
    if (header) {
        let webViewFolders = document.querySelector(".web-view-folders");
        let webViewCut = document.querySelector(".web-view-cut-container");
        let webViewProperties = document.querySelector(".web-view-properties");
        let webViewMenu = document.querySelector(".web-view-menu");
        let webviewQualityModal = document.querySelector(".update-quality-modal");

        let offsetHeight = header.offsetHeight;

        webViewFolders.style.top = offsetHeight + "px";
        webViewCut.style.top = offsetHeight + "px";
        webViewProperties.style.top = offsetHeight + "px";
        webViewMenu.style.top = offsetHeight + "px";
        webviewQualityModal.style.top = offsetHeight + "px";

        var calcHeight = (window.innerHeight - (40 + offsetHeight)) + "px";
        var mediaQuery = window.matchMedia("(max-width: 1200px)")
        if (mediaQuery.matches) {
            var webViewBottomMenuContainerHeight = document.getElementById("web_view_bottom_menu_container").offsetHeight;
            calcHeight = (window.innerHeight - (40 + offsetHeight + webViewBottomMenuContainerHeight)) + "px";
        }

        webViewFolders.style.height = calcHeight;
        webViewProperties.style.maxHeight = calcHeight;
        webViewMenu.style.height = calcHeight;
    }
}

function panelIsClosed(panel) {
    return panel.viewer.style.display === "none";
}

function openPanel(panel) {
    panel.viewer.style.display = "";
    panel.viewer.classList.add("active");

    let panelId = panel.viewer.getAttribute("id");
    let buttons = document.querySelectorAll('button[aria-controls="' + panelId + '"]');
    if (buttons.length > 0) {
        for (let i = 0; i < buttons.length; i++) {
            buttons[i].setAttribute("aria-expanded", "true");
        }
    }

    if (panel.button !== undefined && !panel.button.classList.contains("active"))
        panel.button.classList.add("active");
}

function closePanel(panel) {
    panel.viewer.style.display = "none";
    panel.viewer.classList.remove("active");

    let panelId = panel.viewer.getAttribute("id");
    let buttons = document.querySelectorAll('button[aria-controls="' + panelId + '"]');
    if (buttons.length > 0) {
        for (let i = 0; i < buttons.length; i++) {
            console.log(buttons[i]);
            buttons[i].setAttribute("aria-expanded", "false");
        }
    }

    if (panel.button !== undefined && panel.button.classList.contains("active"))
        panel.button.classList.remove("active");
}

function activeButton(name) {
    const exploreButton = document.getElementById(name);
    if (!exploreButton.classList.contains("active")) {
        exploreButton.classList.add("active");
    }
}

function deactiveButton(name) {
    const exploreButton = document.getElementById(name);
    if (exploreButton.classList.contains("active")) {
        exploreButton.classList.remove("active");
    }
}

function isDesktop() {
    const mobileBreakpoint = 950;
    const mediaQuery = window.matchMedia('(min-width: ' + mobileBreakpoint + 'px)');
    return mediaQuery.matches;
}