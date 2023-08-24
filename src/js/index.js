import "../style/style.scss";
import {
    ProjectData
} from './classes/ProjectData.js';
import {
    apiCaller
} from "./api.js";
import AnchorLinkUtils from "./utils.js";
// import "./tooltip.js";

import * as _accordion from "./accordion.js";
export function getAccordion() {
    return _accordion;
}


import * as _webView from "./webview.js";
export function getWebView() {
    return _webView;
}

/**
 * Function to sanitize the input value
 * @param {String} input The input value to sanitize
 * @returns The sanitized input value
 */
function sanitize(input) {
    let div = document.createElement('div');
    div.appendChild(document.createTextNode(input));
    return div.innerHTML;
}

/**
 * Prevents rapid, repeated firing of an event that might be triggered multiple times in a short period.
 * @param {HTMLElement} callback 
 * @param {int} delay 
 * @returns 
 */
export function debounce(callback, delay = 1000) {
    let timeout;

    return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            callback(...args);
        }, delay);
    };
}

/** @constant
 * @type {HTMLInputElement}
 * @default
 */
const SearchModelByNameInput = document.querySelector("#search_model_by_name_input");
if (SearchModelByNameInput) {

    /** @constant
     * @type {Function}
     * @default
     */
    const debouncedSearchModelByName = debounce((input) => {
        SearchModelByName(input);
    }, 500);

    SearchModelByNameInput.addEventListener("input", () => {
        debouncedSearchModelByName(SearchModelByNameInput);
    });

    /** @constant
     * @type {HTMLUListElement}
     * @default
     */
    const searchModelDropdown = document.getElementById("search_model_by_name_input_ul_div");

    SearchModelByNameInput.addEventListener("keyup", function (event) {
        if (event.key === "Escape" || event.key === 27) {
            searchModelDropdown.style.display = "none";
        }
    });

    /**
     * When input search loses focus, hide the <ul> with search results.
     */
    /* Declare blurTimeout variable */
    let blurTimeout;
    SearchModelByNameInput.addEventListener("blur", function () {
        /* Clear previous timeout (if any) */
        clearTimeout(blurTimeout);
        blurTimeout = setTimeout(() => {
            searchModelDropdown.style.display = "none";
        }, 200);
    });

    /**
     * When input search gains focus, show the <ul> with search results if there are search results.
     */
    SearchModelByNameInput.addEventListener("focus", function () {
        if (searchModelDropdown.childNodes.length > 0) {
            searchModelDropdown.style.display = "block";
        }
    });
}

export async function updateModelPassword() {
    console.log("Running updateModelPassword");
    var model_id = document.getElementById("update_model_id_input");
    var project_is_password_protected_input = document.getElementById("project_is_password_protected_input");
    var project_password_input = document.getElementById("project_password_input");

    let update_model_is_password_protected_response = await apiCaller("update_model_is_password_protected", {
        "model_id": model_id.value,
        "model_password": project_password_input.value,
        "model_is_password_protected": project_is_password_protected_input.checked
    });
    console.log("update_model_is_password_protected_response ", update_model_is_password_protected_response);
    if ("success" in update_model_is_password_protected_response) {
        location.reload();
    }
}

export async function CheckIfThereAreNewProcessingProjects() {
    let processing_projects_check_if_new_project_response = await apiCaller("processing_projects_check_if_new_project", {});
    if ("success" in processing_projects_check_if_new_project_response) {
        location.reload();
    }
}


export async function webviewUpdateMenuCount() {
    console.log("Running webviewUpdateMenuCount");
    var in_processing_projects_amount_span = document.getElementById("in_processing_projects_amount_span");
    var pending_projects_amount_span = document.getElementById("pending_projects_amount_span");

    let webview_update_menu_count_response = await apiCaller("webview_update_menu_count", {});
    console.log("webview_update_menu_count_response ", webview_update_menu_count_response);

    if (webview_update_menu_count_response == "error" || "error" in webview_update_menu_count_response) {
        window.location = ProjectData.props.domainNameUrlVal + "/user_exit/";
        return
    }
    if ("success" in webview_update_menu_count_response) {
        in_processing_projects_amount_span.innerText = webview_update_menu_count_response["success"]["in_processing_projects_amount"];
        pending_projects_amount_span.innerText = webview_update_menu_count_response["success"]["pending_projects_amount"];
    }
    if (webview_update_menu_count_response["success"]["in_processing_projects_amount"] == "0") {
        in_processing_projects_amount_span.style.display = "none";
    } else {
        in_processing_projects_amount_span.style.display = "";
    }
    if (webview_update_menu_count_response["success"]["pending_projects_amount"] == "0") {
        pending_projects_amount_span.style.display = "none";
    } else {
        pending_projects_amount_span.style.display = "";
    }
}


export async function updateModelIFC() {
    console.log("Running updateModelIFC");
    var model_id_input = document.getElementById("model_id_input");
    var output_model_id_input = document.getElementById("output_model_id_input");
    var ifc_error_msg = document.getElementById("ifc_error_msg");
    var search_model_by_name_input = document.getElementById("search_model_by_name_input");

    let update_model_ifc_file_response = await apiCaller("update_model_ifc_file", {
        "input_model_id": model_id_input.value,
        "output_model_id": output_model_id_input.value
    });
    console.log("update_model_ifc_file_response ", update_model_ifc_file_response);
    if ("success" in update_model_ifc_file_response) {
        ifc_error_msg.style.color = "#0FA958";
        ifc_error_msg.innerHTML = update_model_ifc_file_response["success"];
        search_model_by_name_input.value = "";
        listWaitingForDataModels();
        closeUpdateIFCFileDiv();
        returnToUpdateModal();
        closeModal('.modal.update-modal');
        updatePendingProjectsAmountSpan();
    }
    if ("error" in update_model_ifc_file_response) {
        ifc_error_msg.style.color = "#F24E1E";
        ifc_error_msg.innerHTML = update_model_ifc_file_response["error"];
    }
    ifc_error_msg.style.display = "block";
}

/**
 * Updates element text with specific id by button param string
 * @param {HTMLButtonElement} input_element 
 * @param {string} output_element_id 
 */
export function copyInnerHTMLToElement(input_element, output_element_id) {
    console.log("Running copyInnerHTMLToElement");
    var output_element_id = document.getElementById(output_element_id);
    output_element_id.innerHTML = input_element.innerHTML;
}

export function copyValueToElement(input_value, output_element_id) {
    console.log("Running copyValueToElement");
    var output_element_id = document.getElementById(output_element_id);
    output_element_id.innerHTML = input_value;
}

export function showHideElement(event, element_id) {
    // console.log("Running showHideElement");
    // event.stopPropagation(); // Stops propagation of the click event.
    var element = document.getElementById(element_id);

    // if (element.style.display == "none") {
    //     element.style.display = "block";
    //     return
    // }

    // element.style.display = "none";

    element.classList.toggle("open");

}

/**
 * Close menu mobile
 * @param {HTMLElement} menuMobile 
 * @param {HTMLElement} button 
 */
export function closeMenuMobile(menuMobile, button) {
    menuMobile.classList.remove("open");
    menuMobile.setAttribute("aria-hidden", "true");
    menuMobile.setAttribute("hidden", "hidden");
    button.setAttribute("aria-expanded", "false");
}

/**
 * Open menu mobile
 * @param {HTMLElement} menuMobile 
 * @param {HTMLElement} button 
 */
export function openMenuMobile(menuMobile, button) {
    menuMobile.classList.add("open");
    menuMobile.removeAttribute("aria-hidden");
    menuMobile.removeAttribute("hidden");
    button.setAttribute("aria-expanded", "true");
}


/**
 * Toggle menu mobile by checking if button has aria-expanded true/false
 * @param {HTMLElement} button 
 */
export function toggleMenuMobile(button) {
    console.log(button);
    const menuMobile = document.getElementById(button.getAttribute("aria-controls"));
    console.log(button.getAttribute("aria-expanded"));
    if (button.getAttribute("aria-expanded") == "true") {
        button.setAttribute("aria-label", "Fechar menu mobile");
        closeMenuMobile(menuMobile, button);
    } else {
        button.setAttribute("aria-label", "Abrir menu mobile");
        openMenuMobile(menuMobile, button);
    }
}


/**
 * Add event listeners to show/hide mobile menu:
 * When the user clicks outside the mobile menu, close it.
 * When mobile menu loses focus, close it.
 * When user presses ESC key, close it.
 * When mobile menu gains focus, open it.
 * @param {HTMLElement} button 
 */
export function menuMobileEvents(button) {
    const menuMobile = document.getElementById(button.getAttribute("aria-controls"));

    document.addEventListener("click", function (event) {
        if (button.getAttribute("aria-expanded") == "true") {
            if (!menuMobile.contains(event.target) && !button.contains(event.target)) {
                console.log("Clicked outside the menu and button");
                closeMenuMobile(menuMobile, button);
            }
        }
    });

    menuMobile.addEventListener('blur', function (event) {
        console.log("Focus outside the menu");
        closeMenuMobile(menuMobile, button);
    }, true);

    document.addEventListener('keydown', function (event) {
        if (event.key === "Escape") {
            closeMenuMobile(menuMobile, button);
        }
    });

    menuMobile.addEventListener('focus', function (event) {
        openMenuMobile(menuMobile, button);
    }, true);
}


/**
 * 
 * @param {HTMLElement} input 
 * @returns 
 */
export async function SearchModelByName(input) {
    console.log("Running SearchModelByName");

    /** @constant
        @type {HTMLUListElement}
        @default
    */
    const search_model_by_name_input_ul_div = document.getElementById("search_model_by_name_input_ul_div");

    if (!search_model_by_name_input_ul_div) {
        console.error("search_model_by_name_input_ul_div is null. Please ensure the element exists.");
        return;
    }

    let inputValue = input.value;

    if (inputValue == "") {
        search_model_by_name_input_ul_div.innerHTML = "";
        search_model_by_name_input_ul_div.style.display = "none";
        checkIfCloseSuggestionButtonShouldAppear(input, "close_search_model_by_name_img", "search_model_by_name_img");
        return;
    }

    // Sanitize the input value
    let sanitizedInputValue = sanitize(inputValue);

    let search_model_by_name_response;

    try {
        search_model_by_name_response = await apiCaller("search_model_by_name", {
            "model_name": sanitizedInputValue
        });
    } catch (error) {
        console.error("Error calling search_model_by_name API: ", error);
        return;
    }

    console.log("search_model_by_name_response ", search_model_by_name_response);

    if ("success" in search_model_by_name_response) {
        if (search_model_by_name_response["success"] == "") {
            search_model_by_name_input_ul_div.innerHTML = "";
            search_model_by_name_input_ul_div.style.display = "none";
        } else {
            search_model_by_name_input_ul_div.innerHTML = search_model_by_name_response["success"];
            search_model_by_name_input_ul_div.style.display = "block";
        }
    } else {
        search_model_by_name_input_ul_div.innerHTML = "";
        search_model_by_name_input_ul_div.style.display = "none";
    }

    checkIfCloseSuggestionButtonShouldAppear(input, "close_search_model_by_name_img", "search_model_by_name_img");

}


/**
 * Toggles between search input close icon and search icon depending of input.value
 * @param {HTMLInputElement} input 
 * @param {string} x_button_img_id 
 * @param {string} search_button_img_id 
 */
export async function checkIfCloseSuggestionButtonShouldAppear(input, x_button_img_id, search_button_img_id = "") {
    console.log("Running checkIfCloseSuggestionButtonShouldAppear");

    /** @constant
        @type {HTMLImageElement}
        @default
    */
    const x_button_img = document.getElementById(x_button_img_id);

    /** @constant
        @type {HTMLImageElement}
        @default
    */
    const search_button_img = document.getElementById(search_button_img_id);

    console.log(input.value);
    console.log(x_button_img);
    console.log(search_button_img);
    if (input.value != "") {
        x_button_img.style.display = "";

        if (search_button_img) {
            search_button_img.style.display = "none";
        }

    } else {
        x_button_img.style.display = "none";

        if (search_button_img) {
            search_button_img.style.display = "";
        }

    }
}

/**
 * When user clicks on search input close/X icon
 * remove search input value and search results list
 * hide close search input icon and show search input default icon.
 * @param {string} closeButton 
 * @param {string} search_input_id 
 * @param {string} suggestion_div_id 
 * @param {string} searchButton 
 */
export async function closeSearchSuggestion(closeButton, search_input_id, suggestion_div_id, searchButton) {
    console.log("Running closeSearchSuggestion");
    let search_input = document.getElementById(search_input_id);
    let suggestion_div = document.getElementById(suggestion_div_id);
    suggestion_div.innerHTML = "";
    search_input.value = "";
    suggestion_div.style.display = "none";
    document.getElementById(closeButton).style.display = "none";
    document.getElementById(searchButton).style.display = "";

    if (window.location.href.includes("&model_id=")) {
        window.location.href = window.location.href.split("&model_id=")[0];
    }

}

/**
 * Copies the text from button.value to navigator clipboard
 * @param {HTMLButtonElement} input 
 */
export async function copyValueToClipboard(input) {
    console.log("Running copyValueToClipboard");
    navigator.clipboard.writeText(input.value);
    input.innerText = "Copiado!";
    await sleep(2000);
    input.innerText = "Copiar";
}

export async function returnToUpdateModal() {
    console.log("Running returnToUpdateModal");
    let model_id_input = document.getElementById("model_id_input");
    let ifc_project_filename_span = document.getElementById("ifc_project_filename_span");

    closeModal('.modal.update-ifc-modal');
    openModalUpdateModel(model_id_input.value, ifc_project_filename_span.innerHTML)
}

/**
 * Update IFC to last uploaded IFC divs when clicked
 * @param {string} model_id 
 * @param {string} model_filename 
 * @param {string} model_name 
 * @param {string} model_work 
 * @param {string} model_region 
 * @param {string} model_city 
 * @param {string} model_builder 
 * @param {string} model_category 
 */
export async function openUpdateIFCFileDiv(model_id, model_filename, model_name = "", model_work = "", model_region = "", model_city = "", model_builder = "", model_category = "") {
    console.log("Running openUpdateIFCFileDiv");
    let return_button_div = document.getElementById("return_button_div");
    let save_button_div = document.getElementById("save_button_div");
    let search_model_by_name_input_ul_div = document.getElementById("search_model_by_name_input_ul_div");
    let search_model_by_name_input = document.getElementById("search_model_by_name_input");
    let output_model_id_input = document.getElementById("output_model_id_input");
    let ifc_error_msg = document.getElementById("ifc_error_msg");
    let pending_box_search_div = document.getElementById("pending_box_search_div");
    let completed_models_suggestion_div = document.getElementById("completed_models_suggestion_div");

    output_model_id_input.value = model_id;
    ifc_error_msg.style.display = "none";
    return_button_div.style.display = "none";
    pending_box_search_div.style.display = "none";
    completed_models_suggestion_div.style.display = "none";
    save_button_div.style.display = "block";
    search_model_by_name_input_ul_div.innerHTML = "";
    search_model_by_name_input.value = model_name;
}

export async function closeUpdateIFCFileDiv() {
    console.log("Running closeUpdateIFCFileDiv");
    let return_button_div = document.getElementById("return_button_div");
    let save_button_div = document.getElementById("save_button_div");
    let search_model_by_name_input = document.getElementById("search_model_by_name_input");
    let pending_box_search_div = document.getElementById("pending_box_search_div");
    let completed_models_suggestion_div = document.getElementById("completed_models_suggestion_div");

    return_button_div.style.display = "block";
    save_button_div.style.display = "none";
    search_model_by_name_input.value = "";
    pending_box_search_div.style.display = "";
    completed_models_suggestion_div.style.display = "";
}


export async function openModalUpdateIFCProject() {
    console.log("Running openModalUpdateIFCProject");
    let project_filename_span = document.getElementById("project_filename_span");
    let ifc_project_filename_span = document.getElementById("ifc_project_filename_span");
    let ifc_actual_project_filename_span = document.getElementById("ifc_actual_project_filename_span");
    let return_button_div = document.getElementById("return_button_div");
    let save_button_div = document.getElementById("save_button_div");

    return_button_div.style.display = "block";
    save_button_div.style.display = "none";
    ifc_project_filename_span.innerHTML = project_filename_span.innerHTML;
    ifc_actual_project_filename_span.innerHTML = project_filename_span.innerHTML;
    closeModal('.modal.update-modal');
    openModal('.modal.update-ifc-modal');
}

export async function openModalShareProject(model_id, model_name, model_share_link, model_share_link_qrcode, model_is_password_protected, model_password) {
    console.log("Running openModalShareProject");
    let share_project_name_span = document.getElementById("share_project_name_span");
    let copy_share_link_button = document.getElementById("copy_share_link_button");
    let update_model_id_input = document.getElementById("update_model_id_input");
    let copy_share_link_input = document.getElementById("copy_share_link_input");
    let model_share_link_qrcode_img = document.getElementById("model_share_link_qrcode_img");
    let project_is_password_protected_input = document.getElementById("project_is_password_protected_input");
    let project_password_div = document.getElementById("project_password_div");
    let project_password_input = document.getElementById("project_password_input");

    if (model_is_password_protected == "True") {
        project_is_password_protected_input.checked = "checked";
        project_password_div.style.display = "block";
    } else {
        project_is_password_protected_input.checked = "";
        project_password_div.style.display = "none";
    }

    project_password_input.value = model_password;
    update_model_id_input.value = model_id;
    share_project_name_span.innerText = model_name;
    copy_share_link_button.value = model_share_link;
    copy_share_link_input.value = model_share_link;
    model_share_link_qrcode_img.src = model_share_link_qrcode;
    openModal('.modal.share-modal');
}

/**
 * Sort elements and change url params.
 * @param {string} category 
 * @param {HTMLSelectElement} input 
 */
export async function sortBy(category, input) {
    console.log("Running sortBy");
    /** @constant
        @type {HTMLInputElement}
        @default
    */
    const customer_id_input = document.getElementById("customer_id_input");

    /** @constant
        @type {HTMLInputElement}
        @default
    */
    const order_input = document.getElementById("order_input");

    /** @constant
        @type {HTMLInputElement}
        @default
    */
    const reverse_input = document.getElementById("reverse_input");

    var new_href = ProjectData.props["domainNameUrlVal"] + "/projects/?order=" + order_input.value + "&reverse=" + reverse_input.value;
    if (customer_id_input.value !== "") {
        new_href += "&customer_id=" + customer_id_input.value;
    }
    if (input.value !== "" && category !== "") {
        new_href += "&" + category + "=" + input.value;
    }
    location.href = new_href;

}

export async function deleteModel() {
    // console.log("Running deleteModel");
    const delete_model_input = document.getElementById("delete_model_input");
    const delete_model_response = await apiCaller("delete_model", {
        "model_id": delete_model_input.value,
    });
    // console.log("delete_model_response ", delete_model_response);
    if ("success" in delete_model_response) {
        const model_thumb = document.getElementById("model_" + delete_model_input.value + "_thumb_div");
        model_thumb.parentNode.removeChild(model_thumb);
        closeModal('.modal.delete-modal');
    }
    reducePaginationCount();
}


export async function WebviewReprocessModelCheckIfCompleted() {
    let model_id = document.getElementById("model_id_input").value;
    console.log("Running WebviewReprocessModelCheckIfCompleted");
    let webview_reprocess_model_check_if_completed_response = await apiCaller("webview_reprocess_model_check_if_completed", {
        "model_id": model_id
    });
    console.log("webview_reprocess_model_check_if_completed_response ", webview_reprocess_model_check_if_completed_response);
    if (webview_reprocess_model_check_if_completed_response["success"] == "True") {
        window.location = webview_reprocess_model_check_if_completed_response["redirect"];
    }
}

export async function deleteModelProcessingWithError(model_id) {
    console.log("Running deleteModelProcessingWithError");
    let delete_model_response = await apiCaller("delete_model", {
        "model_id": model_id
    });
    console.log("delete_model_response ", delete_model_response);
    await js.index.processingProjectsUpdateDiv();
}

export async function openModalDeleteProject(model_id, model_name) {
    console.log("Running openModalDeleteProject");
    let delete_model_input = document.getElementById("delete_model_input");
    let project_name_span = document.getElementById("project_name_span");
    delete_model_input.value = model_id;
    project_name_span.innerText = model_name;
    openModal('.modal.delete-modal');
}



export function convertFormToJson(formElement) {
    var formData = new FormData(formElement);
    var jsonObject = {};
    for (const [key, value] of formData.entries()) {
        jsonObject[key] = value;
    }
    return jsonObject
}

export async function openModalUpdateModel(model_id, model_filename, model_name = "", model_work = "", model_region = "", model_city = "", model_builder = "", model_category = "") {
    console.log("Running openModalUpdateModel");
    let project_filename_span = document.getElementById("project_filename_span");
    let model_id_input = document.getElementById("model_id_input");
    let model_name_input = document.getElementById("model_name_input");
    let model_work_input = document.getElementById("model_work_input");
    let model_region_input = document.getElementById("model_region_input");
    let model_city_input = document.getElementById("model_city_input");
    let model_builder_input = document.getElementById("model_builder_input");
    let model_category_input = document.getElementById("model_category_input");
    let open_modal_update_ifc_project_button = document.getElementById("open_modal_update_ifc_project_button");
    let error_msg = document.getElementById("error_msg");

    project_filename_span.innerHTML = model_filename;
    model_id_input.value = model_id;
    model_name_input.value = model_name;
    model_work_input.value = model_work;
    model_region_input.value = model_region;
    model_city_input.value = model_city;
    model_builder_input.value = model_builder;
    model_category_input.value = model_category;
    error_msg.style.display = "none";
    if (location.href.includes("pending_projects")) {
        open_modal_update_ifc_project_button.style.display = "block";
    } else {
        open_modal_update_ifc_project_button.style.display = "none";
    }
    openModal('.modal.update-modal');
}

export async function listWaitingForDataModels() {
    console.log("Running listWaitingForDataModels");
    let list_waiting_for_data_models_div = document.getElementById("list_waiting_for_data_models_div");
    let update_waiting_for_data_model_response = await apiCaller("list_waiting_for_data_models", {});
    console.log("update_waiting_for_data_model_response ", update_waiting_for_data_model_response);
    if ("redirect" in update_waiting_for_data_model_response) {
        location.href = update_waiting_for_data_model_response["redirect"]
        return
    }
    list_waiting_for_data_models_div.innerHTML = update_waiting_for_data_model_response["success"];
}

export async function updateWaitingForDataModel(form_id) {
    console.log("Running updateWaitingForDataModel");
    let form = document.getElementById(form_id);
    let post_data = convertFormToJson(form);
    let error_msg = document.getElementById("error_msg");
    console.log(post_data);
    let update_waiting_for_data_model_response = await apiCaller("update_waiting_for_data_model",
        post_data
    );
    console.log("update_waiting_for_data_model_response ", update_waiting_for_data_model_response);
    if ("error" in update_waiting_for_data_model_response) {
        error_msg.style.color = "#F24E1E";
        error_msg.innerText = update_waiting_for_data_model_response["error"];
    }
    if ("success" in update_waiting_for_data_model_response) {
        error_msg.style.color = "#0FA958";
        error_msg.innerText = update_waiting_for_data_model_response["success"];
        if (location.href.includes("pending_projects")) {
            listWaitingForDataModels();
            closeModal('.modal.update-modal');
            updatePendingProjectsAmountSpan();
        } else {
            location.reload();
        }
    }
    error_msg.style.display = ""
}

export async function updatePendingProjectsAmountSpan() {
    console.log("Running updatePendingProjectsAmountSpan");
    let pending_projects_amount_span = document.getElementById("pending_projects_amount_span");
    let get_pending_projects_amount_response = await apiCaller("get_pending_projects_amount", {});
    console.log("get_pending_projects_amount_response ", get_pending_projects_amount_response);
    if (get_pending_projects_amount_response["success"] != "0") {
        pending_projects_amount_span.innerHTML = get_pending_projects_amount_response["success"];
    }
}

export async function userSendResetPassEmail() {
    console.log("Running userSendResetPassEmail");
    let error_msg = document.getElementById("error_msg_span");
    let user_email = document.getElementById("user_email");
    let api_response = await apiCaller("user_send_reset_password_email", {
        'user_email': user_email.value
    });
    console.log("api_response " + api_response);
    if (api_response.success) {
        error_msg.innerHTML = api_response.success;
        error_msg.style.color = "#0FA958";
    }
    if (api_response.error) {
        error_msg.innerHTML = api_response.error;
        error_msg.style.color = "#F24E1E";
    }
    error_msg.style.display = "";
    return
}

export function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

export function goToHref(destiny_href) {
    window.location.href = destiny_href;
}

export function openModal(css_class) {
    let modal = document.querySelector(css_class);
    modal.classList.add('active');
}

export function closeModal(css_class) {
    let modal = document.querySelector(css_class);
    modal.classList.remove('active');
}

export async function updatePaginationProgressBar() {
    let pagination_actual_itens_count_span = document.getElementById("pagination_actual_itens_count_span");
    let pagination_total_itens_count_span = document.getElementById("pagination_total_itens_count_span");
    let ProgressBar = document.querySelector(".progress-pagination.upload-bar");
    ProgressBar.style = 'width:' + parseInt((parseInt(pagination_actual_itens_count_span.innerHTML) / parseInt(pagination_total_itens_count_span.innerHTML)) * 100) + "%; color:transparent";
}

export async function loadMoreOnScroll(query) {
    var last_scroll_position = -1;
    var do_not_call_api = false;

    window.onscroll = async function () {
        let current_scroll_position = this.scrollY;
        let last_scroll_position_input = document.getElementById("last_scroll_position");
        last_scroll_position_input.value = current_scroll_position;

        if (do_not_call_api == false) {
            do_not_call_api = true;
            console.log("do no call api");
            await js.index.sleep(300);
            console.log("you may call api");
            do_not_call_api = false;
        }
    };

    window.onkeydown = async function (event) {
        console.log("event ", event);
        if (event.keyCode == 34) {
            let current_scroll_position = this.scrollY;
            let last_scroll_position_input = document.getElementById("last_scroll_position");
            last_scroll_position_input.value = current_scroll_position;

            if (last_scroll_position != current_scroll_position || last_scroll_position == -1) {
                console.log("last_scroll_position", last_scroll_position);
                console.log("current_scroll_position", current_scroll_position);
                last_scroll_position = current_scroll_position;
                return
            }
            if (do_not_call_api == false) {
                let pagination_actual_itens_count_span = document.getElementById("pagination_actual_itens_count_span");
                let pagination_total_itens_count_span = document.getElementById("pagination_total_itens_count_span");
                if (pagination_actual_itens_count_span.innerHTML != pagination_total_itens_count_span.innerHTML) {
                    do_not_call_api = true;
                    await loadMoreCallApiPagination();
                    await js.index.sleep(300);
                    last_scroll_position = -1;
                    do_not_call_api = false;
                }
            }
        }
    };

    window.onwheel = async function () {
        let current_scroll_position = this.scrollY;
        let last_scroll_position_input = document.getElementById("last_scroll_position");
        last_scroll_position_input.value = current_scroll_position;

        if (last_scroll_position != current_scroll_position || last_scroll_position == -1) {
            console.log("last_scroll_position", last_scroll_position);
            console.log("current_scroll_position", current_scroll_position);
            last_scroll_position = current_scroll_position;
            return
        }
        if (do_not_call_api == false) {
            let pagination_actual_itens_count_span = document.getElementById("pagination_actual_itens_count_span");
            let pagination_total_itens_count_span = document.getElementById("pagination_total_itens_count_span");
            if (pagination_actual_itens_count_span.innerHTML != pagination_total_itens_count_span.innerHTML) {
                do_not_call_api = true;
                await loadMoreCallApiPagination();
                await js.index.sleep(300);
                last_scroll_position = -1;
                do_not_call_api = false;
            }
        }
    };
}

export async function loadMoreCallApiPagination() {
    console.log("running loadMorePagination");
    let query_filter_input = document.getElementById("query_filter");
    let query_filter_value = ""
    if (query_filter_input) {
        query_filter_value = query_filter_input.value
    }
    let reverse = document.getElementById("reverse_input");
    let last_evaluated_key_input = document.getElementById("last_evaluated_key");
    let query_input = document.getElementById("query");
    let pagination_queries_response = await apiCaller("pagination_queries", {
        "query": query_input.value,
        "last_evaluated_key": last_evaluated_key_input.value,
        "query_filter": query_filter_value,
        "reverse": reverse.value
    });
    console.log("pagination_queries_response", pagination_queries_response);

    let pagination_component = document.getElementById("pagination_component");
    pagination_component.innerHTML += pagination_queries_response["success"];
    console.log("updating last_evaluated_key with ", pagination_queries_response["last_evaluated_key"]);
    let pagination_actual_itens_count_span = document.getElementById("pagination_actual_itens_count_span");
    let pagination_total_itens_count_span = document.getElementById("pagination_total_itens_count_span");
    let showing_total_count_input = document.getElementById("showing_total_count");
    let ProgressBar = document.querySelector(".progress-pagination.upload-bar");

    last_evaluated_key_input.value = JSON.stringify(pagination_queries_response["last_evaluated_key"]);
    pagination_actual_itens_count_span.innerHTML = parseInt(pagination_actual_itens_count_span.innerHTML) + parseInt(pagination_queries_response["new_itens_count"])
    ProgressBar.style = 'width:' + parseInt((parseInt(pagination_actual_itens_count_span.innerHTML) / parseInt(pagination_total_itens_count_span.innerHTML)) * 100) + "%; color:transparent";
    showing_total_count_input.value = pagination_actual_itens_count_span.innerHTML;

    if (parseInt(pagination_actual_itens_count_span.innerHTML) == parseInt(pagination_total_itens_count_span.innerHTML)) {
        let load_more_pagination_button = document.getElementById("load_more_pagination_button");
        load_more_pagination_button.style.display = "none";
    }
}

export async function reducePaginationCount() {
    const pagination_actual_itens_count_span = document.getElementById("pagination_actual_itens_count_span");
    const pagination_total_itens_count_span = document.getElementById("pagination_total_itens_count_span");
    const showing_total_count_input = document.getElementById("showing_total_count");
    const progressBar = document.querySelector(".progress-pagination.upload-bar");

    pagination_total_itens_count_span.innerHTML = parseInt(pagination_total_itens_count_span.innerHTML) - 1
    pagination_actual_itens_count_span.innerHTML = parseInt(pagination_actual_itens_count_span.innerHTML) - 1
    progressBar.style = 'width:' + parseInt((parseInt(pagination_actual_itens_count_span.innerHTML) / parseInt(pagination_total_itens_count_span.innerHTML)) * 100) + "%; color:transparent";
    showing_total_count_input.value = pagination_actual_itens_count_span.innerHTML;

    if (parseInt(pagination_actual_itens_count_span.innerHTML) == parseInt(pagination_total_itens_count_span.innerHTML)) {
        let load_more_pagination_button = document.getElementById("load_more_pagination_button");
        load_more_pagination_button.style.display = "none";
    }
}

/**
 * Toggles project filter menu
 * @param {string} button 
 * @param {string} menu 
 */
export async function toggleProjectFilterMenu(button, menu) {
    const buttonElement = document.querySelector(button);
    const menuElement = document.querySelector(menu);

    buttonElement.addEventListener("click", function () {
        const isMenuOpen = buttonElement.getAttribute("aria-expanded");

        if (isMenuOpen == "true") {
            buttonElement.setAttribute("aria-expanded", "false");
            buttonElement.setAttribute("aria-label", "Abrir filtros");
            buttonElement.setAttribute("title", "Abrir filtros");
            menuElement.setAttribute("aria-hidden", "true");
            return;
        }

        buttonElement.setAttribute("aria-expanded", "true");
        buttonElement.setAttribute("aria-label", "Fechar filtros");
        buttonElement.setAttribute("title", "Fechar filtros");
        menuElement.setAttribute("aria-hidden", "false");
        return;

    });
}

/**
 * Controls input password text visibility
 */
function showPassword() {
    let iconShowPasswordOff = document.querySelectorAll('.input-password__icon-show-password-off');

    for (var i = 0, length = iconShowPasswordOff.length; i < length; i++) {
        let element = iconShowPasswordOff[i];
        let input = element.previousElementSibling;

        element.addEventListener("click", function () {
            if (input.type == "password") {
                element.setAttribute('src', (props.cdnVal + "/assets/icons/icon-password-show-resized.svg"));
                input.type = "text";
            } else {
                element.setAttribute('src', (props.cdnVal + "/assets/icons/icon-password-show-off-resized.svg"));
                input.type = "password";
            }
        });
    }
}

if (document.querySelector('.input-password__icon-show-password-off')) {
    showPassword();
}

const PASSWORD_SHOW_ICON = "icon-password-show-resized.svg";
const PASSWORD_HIDE_ICON = "icon-password-show-off-resized.svg";
const PASSWORD_SHOW_LABEL = "Mostrar senha.";
const PASSWORD_HIDE_LABEL = "Ocultar senha.";

/**
 * Hides/show input type password text
 * by changing input type to text/password
 * @param {HTMLButtonElement} button 
 * @param {string} input_id 
 * @returns 
 */
export function togglePasswordText(button, input_id) {
    var input = document.getElementById(input_id);
    var icon_img = button.querySelector("img");

    if (input.type == "password") {
        input.type = "text";
        button.setAttribute("aria-label", PASSWORD_HIDE_LABEL);
        icon_img.src = icon_img.src.replace(PASSWORD_HIDE_ICON, PASSWORD_SHOW_ICON);
        return;
    }
    input.type = "password";
    button.setAttribute("aria-label", PASSWORD_SHOW_LABEL);
    icon_img.src = icon_img.src.replace(PASSWORD_SHOW_ICON, PASSWORD_HIDE_ICON);
    return;
}

export async function processingProjectsUpdateDiv() {
    // console.log("Running processingProjectsUpdateDiv");
    let models_in_process_div = document.getElementById("models_in_process_div");
    let in_processing_projects_amount_span = document.getElementById("in_processing_projects_amount_span");
    let pending_projects_amount_span = document.getElementById("pending_projects_amount_span");

    let processing_projects_update_div_response = await apiCaller("processing_projects_update_div", {});
    // console.log("processing_projects_update_div_response", processing_projects_update_div_response);

    if ("error" in processing_projects_update_div_response) {
        location.href = ProjectData.props["domainNameUrlVal"] + "/pending_projects";
    }
    if (processing_projects_update_div_response["models_in_processing_count"] == "0") {
        in_processing_projects_amount_span.style.display = "none";
        location.href = ProjectData.props["domainNameUrlVal"] + "/pending_projects";
    } else {
        in_processing_projects_amount_span.style.display = "";
    }
    if (processing_projects_update_div_response["models_waiting_for_data_count"] == "0") {
        pending_projects_amount_span.style.display = "none";
    } else {
        pending_projects_amount_span.style.display = "";
    }

    models_in_process_div.innerHTML = processing_projects_update_div_response["success"];
    in_processing_projects_amount_span.innerHTML = processing_projects_update_div_response["models_in_processing_count"];
    pending_projects_amount_span.innerHTML = processing_projects_update_div_response["models_waiting_for_data_count"];

    // if (processing_projects_update_div_response["project_still_processing"] == "True") {
    //     var processing_loader_div = document.getElementById("processing_loader_div");
    //     processing_loader_div.style.display = "block";
    // } else {
    //     var processing_loader_div = document.getElementById("processing_loader_div");
    //     processing_loader_div.style.display = "none";
    // }

    await animatingProgressBar();

}

/**
 * 
 * @param {HTMLInputElement} input 
 */
export async function uploadProjectFileToS3(input) {
    console.log("Running uploadProjectFileToS3");
    var url = document.getElementById("url_input").value;
    var key = document.getElementById("key_input").value;
    var AWSAccessKeyId = document.getElementById("AWSAccessKeyId_input").value;
    var policy = document.getElementById("policy_input").value;
    var signature = document.getElementById("signature_input").value;
    var file = input.files[0];
    var form = document.getElementById("project_create_upload_file_form");
    let projectProgressBar = document.querySelector(".project-progress-bar");
    projectProgressBar.removeAttribute("hidden");
    input.style.display = "none";
    document.querySelector(".label-input-file").style.display = "none";
    document.querySelector(".creating-project-message").removeAttribute("hidden");

    /**
     * @param {string} key
     * @param {string} AWSAccessKeyId
     * @param {string} policy
     * @param {string} signature
     * @param {File} file
     */
    let post_data = {
        "key": key,
        "AWSAccessKeyId": AWSAccessKeyId,
        "policy": policy,
        "signature": signature,
        "file": file
    }

    let onProgress = progress => {
        console.log(Math.round(progress * 100) + '%');
        projectProgressBar.value = Math.round(progress * 100);
    }

    let uploadWithProgressBar_response = await uploadWithProgressBar(url, post_data, onProgress);

    projectProgressBar.setAttribute("hidden", "hidden");
    document.querySelector(".creating-project-message").setAttribute("hidden", "hidden");
    document.querySelector(".project-create-loader").removeAttribute("hidden");
    form.submit();
    // loader
}

/**
 * Show/Hide profile dropdown when button is clicked
 * @param {HTMLButtonElement} button 
 */
export async function toggleProfileDropdown(button, event) {
    // event.stopPropagation();

    // console.log(button);
    let dropdownContainer = document.getElementById(button.getAttribute("aria-controls"));
    // console.log(dropdownContainer);
    // console.log(button.getAttribute("aria-expanded"));
    if (button.getAttribute("aria-expanded") == "true") {
        dropdownContainer.classList.remove("open");
        button.setAttribute("aria-expanded", "false");
    } else {
        dropdownContainer.classList.add("open");
        button.setAttribute("aria-expanded", "true");
    }
}


/**
 * Toggle button dropdowns
 */
export async function toggleAllButtonDropdowns() {
    let mainElement = document.querySelector("html");
    let toggleButtons = document.querySelectorAll("button[aria-controls]");

    // console.log(toggleButtons);

    mainElement.addEventListener("click", function (event) {
        var i = 0,
            buttonLength = toggleButtons.length;
        while (i < buttonLength) {
            let dropdownElement = document.getElementById(toggleButtons[i].getAttribute("aria-controls"));

            if (dropdownElement) {
                console.log(!dropdownElement.contains(event.target));
                console.log(!toggleButtons[i].contains(event.target));
                if (!dropdownElement.contains(event.target) && !toggleButtons[i].contains(event.target)) {
                    dropdownElement.classList.remove("open");
                    dropdownElement.setAttribute("aria-hidden", "true");
                    toggleButtons[i].setAttribute("aria-expanded", "false");
                }
            } else {
                console.warn(toggleButtons[i]);
            }

            i++;
        }
    });
}

export function wasElementClicked(element, event) {
    return (element.contains(event.target));
}

export async function closeProfileDropdown(button, event) {
    event.stopPropagation();
    let dropdownContainer = document.getElementById(button.getAttribute("aria-controls"));
    dropdownContainer.classList.remove("open");
    button.setAttribute("aria-expanded", "false");
}

/**
 * Controls current webviewer quality
 * @param {HTMLInputElement} checkbox_input 
 */
export async function changeWebViewQuality(checkbox_input) {
    var checkbox_input = document.getElementById("toggle-polygons-input");
    console.log("Running changeWebViewQuality");
    console.log(checkbox_input.checked);

    var selected_quality = "";
    var current_quality = "";

    if (checkbox_input.checked == true) {
        selected_quality = "hd";
        current_quality = "sd";
    } else {
        selected_quality = "sd";
        current_quality = "hd";
    }

    var quality_substring = "&quality=";
    if ((window.location.href).includes(quality_substring)) {
        window.location.href = (window.location.href).replace(quality_substring + current_quality, quality_substring + selected_quality);
    } else {
        window.location.href = window.location.href + quality_substring + selected_quality;
    }
}

/**
 * Replaces quality=hd url param for sd
 * If there's no quality param in url, add one.
 */
export async function changeWebViewToPerformanceMode() {
    if (window.location.href.includes("&quality=hd")) {
        window.location.href = window.location.href.replace("&quality=hd", "&quality=sd");
    } else {
        window.location.href = window.location.href + "&quality=sd";
    }
}


/**
 * Animates progress bar stripe pattern movement by changing css variable value
 */
export async function animatingProgressBar() {
    let progressBars = document.querySelectorAll('.project-progress-bar');

    if (progressBars.length > 0) {
        let observer = new MutationObserver((mutationsList, observer) => {
            var mutationLength = mutationsList.length;
            for (var j = 0; j < mutationLength; j++) {
                let mutation = mutationsList[j];
                if (mutation.type === 'attributes' && mutation.attributeName === 'value') {
                    let target = mutation.target;
                    let value = target.value;

                    target.style.setProperty("--progress-bar-after-width", `${value}%`);
                }
            }
        });

        const progressBarsLength = progressBars.length;
        for (var i = 0; i < progressBarsLength; i++) {
            let progressBar = progressBars[i];
            let initialValue = progressBar.value;
            progressBar.style.setProperty("--progress-bar-after-width", `${initialValue}%`);
            observer.observe(progressBar, {
                attributes: true
            });
        }
    }
}

/**
 * Updates progress bar values through file upload
 * @param {string} url 
 * @param {object} post_data 
 * @param {function} onProgress 
 * @returns 
 */
const uploadWithProgressBar = (url, post_data, onProgress) =>
    new Promise((resolve, reject) => {
        console.log("running uploadWithProgressBar")
        let xhr = new XMLHttpRequest();
        xhr.upload.addEventListener('progress', (e) => {
            onProgress(e.loaded / e.total)
        });
        xhr.addEventListener('load', () => resolve({
            status: xhr.status,
            body: xhr.responseText
        }));
        xhr.addEventListener('error', () => reject(new Error('File upload failed')));
        xhr.addEventListener('abort', () => reject(new Error('File upload aborted')));
        xhr.open('POST', url, true);
        let formData = new FormData();
        for (let property in post_data) {
            formData.append(property, post_data[property]);
        }
        xhr.send(formData);
    });