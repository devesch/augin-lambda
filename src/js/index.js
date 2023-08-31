"use strict";

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

export function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

export async function deleteModel(model_id) {
    let model_delete_response = await apiCaller("model_delete", {
        "model_id": model_id
    });
    await js.index.processingProjectsUpdateUl();
    await js.index.showUserDicts();
}


export async function processingProjectsUpdateUl() {
    console.log("Running processingProjectsUpdateUl");
    let models_in_process_ul = document.getElementById("models_in_process_ul");
    let amount_of_models_in_processing_before_update = models_in_process_ul.getElementsByTagName("li").length;

    let panel_explore_projects_models_in_processing_html_response = await apiCaller("panel_explore_projects_models_in_processing_html", {});
    models_in_process_ul.innerHTML = panel_explore_projects_models_in_processing_html_response["success"];

    let amount_of_models_in_processing_after_update = models_in_process_ul.getElementsByTagName("li").length;
    if (amount_of_models_in_processing_before_update != amount_of_models_in_processing_after_update) {
        showUserDicts();
    }
}


export async function uploadModel(input) {
    checkIfCreateProjectSubmitButtonIsAvailable(false);
    const files = input.files;
    const process_to_bucket = "upload.augin.app";

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        let uploading_div = document.getElementById("uploading_div");
        let uploading_index_input = document.getElementById("uploading_index_input");

        // Create a unique identifier for this upload, could also be a timestamp or UUID
        let current_index = uploading_index_input.value;

        console.warn("current_index", current_index);

        let file_name_array = file["name"].split(".");
        let file_name_extension = file_name_array[file_name_array.length - 1];

        let panel_get_aws_upload_keys_response = await apiCaller("panel_get_aws_upload_keys", {
            "create_model": file["name"],
            "key_extension": file_name_extension,
            "bucket": process_to_bucket
        });

        let post_data = {
            "key": panel_get_aws_upload_keys_response["success"]['key'],
            "AWSAccessKeyId": panel_get_aws_upload_keys_response["success"]['AWSAccessKeyId'],
            "policy": panel_get_aws_upload_keys_response["success"]['policy'],
            "signature": panel_get_aws_upload_keys_response["success"]['signature'],
            "file": file,
            "element_index": current_index

        };

        let panel_create_project_uploading_html_response = await apiCaller("panel_create_project_uploading_html", {
            "model_filename": file["name"],
            "index": current_index,
        });

        uploading_div.innerHTML += panel_create_project_uploading_html_response["success"];

        // Increment the index for the next upload
        uploading_index_input.value = parseInt(current_index) + 1;
        uploadWithProgressBar(panel_get_aws_upload_keys_response["success"]['url'], post_data);
    }
}

export async function checkUploadModelFile(post_data, progress_element) {
    console.log("Running checkUploadModelFile")
    let message = document.getElementById("message_" + post_data["element_index"]);
    let delete_button = document.getElementById("delete_button_" + post_data["element_index"]);
    let model_id = document.getElementById("model_id_" + post_data["element_index"]);
    let has_error = document.getElementById("has_error_" + post_data["element_index"]);
    let has_more_than_one_file = document.getElementById("has_more_than_one_file_" + post_data["element_index"]);

    let panel_create_project_check_file_response = await apiCaller("panel_create_project_check_file", {
        "key": post_data["key"]
    });
    if ("error" in panel_create_project_check_file_response) {
        progress_element.classList.add("failed");
        message.innerHTML = panel_create_project_check_file_response["error"];
        delete_button.style = "";
        has_error.value = "True";
        checkIfCreateProjectSubmitButtonIsAvailable(false);
    } else {
        progress_element.classList.add("success");
        model_id.value = panel_create_project_check_file_response["models_ids"];
        has_more_than_one_file.value = panel_create_project_check_file_response["has_more_than_one_file"];

        let translate_response = await apiCaller("translate", {
            "key": "Upload realizado com sucesso"
        });

        message.innerHTML = translate_response["success"];
        checkIfCreateProjectSubmitButtonIsAvailable();
        checkIfCreateProjectIsFederated();
    }


}


export async function checkIfCreateProjectIsFederated() {
    let federated_switch_div = document.getElementById("federated_switch_div");
    let uploading_element_has_more_than_one_file = document.querySelectorAll(".uploading_element_has_more_than_one_file");
    let uploading_element_message = document.querySelectorAll(".uploading_element_message");

    if (uploading_element_message.length > 1) {
        federated_switch_div.style.display = "";
        return;
    } else {
        if (uploading_element_message.length === 1) {
            for (let has_more_than_one_file_input of uploading_element_has_more_than_one_file) {
                console.log("has_more_than_one_file_input", has_more_than_one_file_input.value);
                if (has_more_than_one_file_input.value === "true") {
                    federated_switch_div.style.display = "";
                    return;
                }
            }
        }
    }
    federated_switch_div.style.display = "none;";
}

export async function checkIfCreateProjectSubmitButtonIsAvailable(is_submitable = true) {
    let submit_form_button = document.getElementById("submit_form_button");
    let uploading_div = document.getElementById("uploading_div");
    let uploading_element_errors = document.querySelectorAll(".uploading_element_with_error");
    let uploading_element_message = document.querySelectorAll(".uploading_element_message");

    if (uploading_div.innerHTML.length < 1) {
        submit_form_button.setAttribute("disabled", "disabled");
        return;
    }
    for (let error_input of uploading_element_errors) {
        if (error_input.value === "True") {
            submit_form_button.setAttribute("disabled", "disabled");
            return;
        }
    }
    for (let element_message of uploading_element_message) {
        if (element_message.innerHTML === "") {
            submit_form_button.setAttribute("disabled", "disabled");
            return;
        }
    }
    if (is_submitable) {
        submit_form_button.removeAttribute("disabled");
    } else {
        submit_form_button.setAttribute("disabled", "disabled");
    }
}


export async function deleteUploadingElement(index) {
    console.log("Running deleteUploadingElement")
    let uploading_element = document.getElementById("uploading_element_" + index);
    uploading_element.remove();
    checkIfCreateProjectSubmitButtonIsAvailable()
}



const uploadWithProgressBar = (url, post_data) =>
    new Promise((resolve, reject) => {
        let xhr = new XMLHttpRequest();
        let progress_element;
        let current_progress;
        xhr.upload.addEventListener('progress', (e) => {
            progress_element = document.getElementById("progress_" + post_data["element_index"]);
            current_progress = Math.round((e.loaded / e.total) * 100);
            progress_element.value = current_progress;
            progress_element.title = current_progress + "%";
            checkIfCreateProjectSubmitButtonIsAvailable(false);
        });
        xhr.addEventListener('load', () => {
            checkUploadModelFile(post_data, progress_element);
            checkIfCreateProjectIsFederated()
            resolve({
                status: xhr.status,
                body: xhr.responseText
            });
        });
        xhr.addEventListener('error', () => {
            progress_element.classList.add("failed");
            reject(new Error('File upload failed'))
        });
        xhr.addEventListener('abort', () => {
            progress_element.classList.add("failed");
            reject(new Error('File upload aborted'))
        });
        xhr.open('POST', url, true);
        let formData = new FormData();
        for (let property in post_data) {
            formData.append(property, post_data[property]);
        }
        xhr.send(formData);
    });

export function openModal(css_class) {
    let modal = document.querySelector(css_class);
    modal.classList.add('active');
}

export function closeModal(css_class) {
    let modal = document.querySelector(css_class);
    modal.classList.remove('active');
}


export async function userSendResetPassEmail() {
    console.log("Running userSendResetPassEmail");
    let error_msg = document.getElementById("error_msg");
    let user_email = document.getElementById("user_email");
    let user_send_reset_password_email_response = await apiCaller("user_send_reset_password_email", {
        'user_email': user_email.value
    });

    if ("success" in user_send_reset_password_email_response) {
        error_msg.innerHTML = user_send_reset_password_email_response["success"]
        error_msg.style = ""
        return
    }
    if ("error" in user_send_reset_password_email_response) {
        error_msg.innerHTML = user_send_reset_password_email_response["error"]
        error_msg.style = ""
        return
    }
}


export function addEventListenerToVerificationCodeInputs() {
    console.log("Running addEventListenerToVerificationCodeInputs")
    let inputs = document.querySelectorAll('.page__box-email-verify__form__entry__box-code__code');
    let key = ""
    inputs = [...inputs];
    inputs.forEach((inputField, i) => {
        let currentInput = inputs[i];
        let nextInput = inputs[i + 1];
        let backInput = inputs[i - 1];
        currentInput.addEventListener("keydown", function (event) {
            key = event.keyCode || event.charCode;
            console.log("key " + key)
            if (key == 8) {
                if (currentInput == inputs[0]) {
                    inputs.forEach((inputField, i) => {
                        inputField.value = "";
                    })
                    currentInput.value = "";
                    inputs[0].focus()
                } else {
                    currentInput.value = "";
                    backInput.focus()
                }
            }
            if (key == 46) {
                inputs.forEach((inputField, i) => {
                    inputField.value = "";
                })
                currentInput.value = "";
                inputs[0].focus()
            }
            if (key == 37) {
                backInput.focus()
            }
            if (key == 39) {
                nextInput.focus()
            }
        })
        currentInput.addEventListener('paste', (event) => {
            event.preventDefault();
            let pastedText = (event.clipboardData || window.clipboardData).getData('text').trim();
            let inputs_paste = document.querySelectorAll('.page__box-email-verify__form__entry__box-code__code');
            let index_paste = 0
            inputs_paste = [...inputs_paste];

            if (pastedText.length > 6) {
                pastedText = String(pastedText).substring(0, 6);
            }

            for (let letter of pastedText) {
                inputs_paste[index_paste].value = letter
                index_paste = index_paste + 1
                console.log("letter " + letter)
            }
            verifySendEmailCode(inputs_paste)
        })
    })
}

export function getAllVerificationCodeInputs() {
    console.log("Running getAllVerificationCodeInputs")
    let inputs = document.querySelectorAll('.page__box-email-verify__form__entry__box-code__code');
    inputs = [...inputs];
    inputs.forEach((inputField, i) => {
        let currentInput = inputs[i];
        let nextInput = inputs[i + 1];
        if (i < 5) {
            if (currentInput.value > -1) {
                if (Number(currentInput.value)) {
                    nextInput.focus();
                } else {
                    currentInput.value = ""
                }
            } else {
                currentInput.value = ""
            }
        }
    })
    verifySendEmailCode(inputs)
}


export function verifySendEmailCode(inputs_array) {
    let form = document.querySelector('.page__box-email-verify__form');
    let submit_valid = true
    for (const index in inputs_array) {
        console.log(inputs_array[index]);
        if (inputs_array[index].value == "") {
            submit_valid = false;
        }
    }
    if (submit_valid) {
        form.submit();
    }
}

export function detectClickOutsideElement() {
    let main = document.querySelector(".body--my-plan");
    let openMobileMenuButton = document.querySelector(".menu-mobile-open-button");
    let closeMobileMenuButton = document.querySelector(".header__mobile-close-button");

    let exploreCreateButton = document.querySelector(".explore-create-more-options");

    document.addEventListener("click", function (event) {
        // console.log(event);
        // console.log(openMobileMenuButton);
        // console.log(closeMobileMenuButton);
        if (openMobileMenuButton && closeMobileMenuButton) {
            let mobileMenu = document.querySelector(".header--my-plan");
            // console.log(mobileMenu);
            if (mobileMenu) {
                // console.log(event.target);
                if (openMobileMenuButton.contains(event.target)) {
                    mobileMenu.classList.add("open");
                    openMobileMenuButton.setAttribute("aria-expanded", "true");
                }

                if (closeMobileMenuButton.contains(event.target)) {
                    mobileMenu.classList.remove("open");
                    openMobileMenuButton.setAttribute("aria-expanded", "false");
                }

            }
        }

        hideExploreMenuWhenClickedOutside(event.target);

        if (exploreCreateButton) {
            let currentMenu = document.getElementById(exploreCreateButton.getAttribute("aria-controls"));
            activateExploreCreateMenu(event.target, exploreCreateButton, currentMenu);
        }

    });
}

/**
 * 
 * @param {HTMLButtonElement} button 
 */
export function togglePasswordVisibility(button) {
    let image = button.querySelector("img");
    let input = document.getElementById(button.getAttribute("aria-controls"));
    if (image.src.includes("visibility_off")) {
        image.src = image.src.replace("visibility_off", "visibility");
        input.setAttribute("type", "text");
        button.setAttribute("aria-label", "Ocultar senha");
        button.setAttribute("title", "Ocultar senha");
    } else {
        image.src = image.src.replace("visibility", "visibility_off");
        input.setAttribute("type", "password");
        button.setAttribute("aria-label", "Exibir senha");
        button.setAttribute("title", "Exibir senha");
    }
}

/**
 * 
 * @param {HTMLElement} element 
 */
export function hideHtmlElement(element) {
    element.classList.add("none");
    element.setAttribute("aria-hidden", "true");
    element.setAttribute("hidden", "hidden");
}

/**
 * 
 * @param {HTMLElement} element 
 */
export function showHtmlElement(element) {
    element.classList.remove("none");
    element.setAttribute("aria-hidden", "false");
    element.removeAttribute("hidden");
}

export function activateAuginSubscriptionSelection() {
    let monthlyRadioButton = document.getElementById("monthly_augin_plan");
    let yearlyRadioButton = document.getElementById("yearly_augin_plan");

    if (monthlyRadioButton && yearlyRadioButton) {
        let monthlySubscriptionContainer = document.getElementById("monthly_subscription_container");
        let yearlySubscriptionContainer = document.getElementById("yearly_subscription_container");

        if (monthlySubscriptionContainer && yearlySubscriptionContainer) {
            if (monthlyRadioButton.checked) {
                showHtmlElement(monthlySubscriptionContainer);
                hideHtmlElement(yearlySubscriptionContainer);
            }

            if (yearlyRadioButton.checked) {
                hideHtmlElement(monthlySubscriptionContainer);
                showHtmlElement(yearlySubscriptionContainer);
            }

            monthlyRadioButton.addEventListener("change", function () {
                if (monthlyRadioButton.checked) {
                    showHtmlElement(monthlySubscriptionContainer);
                    hideHtmlElement(yearlySubscriptionContainer);
                }
            });

            yearlyRadioButton.addEventListener("change", function () {
                if (yearlyRadioButton.checked) {
                    hideHtmlElement(monthlySubscriptionContainer);
                    showHtmlElement(yearlySubscriptionContainer);
                }
            });
        } else {
            console.warn("monthlySubscriptionContainer and yearlySubscriptionContainer are not defined.");
        }
    }
}

/**
 * 
 * @param {event.target} clickTarget 
 */
export function hideExploreMenuWhenClickedOutside(clickTarget) {

    let buttons = document.querySelectorAll(".button--explore-more-options");
    let buttonsLength = buttons.length;

    if (buttonsLength > 0) {

        let i = 0;
        while (i < buttonsLength) {
            let currentMenu = document.getElementById(buttons[i].getAttribute("aria-controls"));

            if (!buttons[i].contains(clickTarget)) {
                currentMenu.classList.add("none");
                buttons[i].setAttribute("aria-expanded", "false");
            }

            i++;
        }
    }
}

/**
 * 
 */
export function toggleExploreMenu(button) {
    let menu = document.getElementById(button.getAttribute("aria-controls"));
    if (menu.classList.contains("none")) {
        menu.classList.remove("none");
        button.setAttribute("aria-expanded", "true");
    } else {
        menu.classList.add("none");
        button.setAttribute("aria-expanded", "false");
    }
}

/**
 * 
 * @param {event.target} clickTarget 
 * @param {HTMLButtonElement} button 
 * @param {HTMLMenuElement} currentMenu 
 */
export function activateExploreCreateMenu(clickTarget, button, currentMenu) {
    if (button.contains(clickTarget)) {
        if (currentMenu.classList.contains("none")) {
            currentMenu.classList.remove("none");
            button.setAttribute("aria-expanded", "true");
        } else {
            currentMenu.classList.add("none");
            button.setAttribute("aria-expanded", "false");
        }
    } else {
        currentMenu.classList.add("none");
        button.setAttribute("aria-expanded", "false");
    }
}

export function activateDraggableItems() {
    const draggableItems = document.getElementsByClassName("draggable");
    const draggableItemsLength = draggableItems.length;
    const container = document.getElementsByClassName("explore__table")[0];

    if (draggableItemsLength > 0) {

        for (var i = 0; i < draggableItemsLength; i++) {
            const currentItem = draggableItems[i];
            currentItem.addEventListener("dragstart", function () {
                currentItem.classList.add("dragging");
            });

            currentItem.addEventListener("dragend", function () {
                currentItem.classList.remove("dragging");
            });
        }

    }

    function initSortableList(event) {
        const draggingItem = container.querySelector(".dragging");
        let notDraggingItems = container.querySelectorAll("tbody tr:not(.dragging)");

        if (notDraggingItems.length() > 0) {
            const nextSibling = notDraggingItems.find(sibling => {
                return event.clientY <= sibling.offsetTop + sibling.offsetHeight / 2;
            });

            container.insertBefore(draggingItem)
        }
    }


    if (container) {
        container.addEventListener("dragover", initSortableList);
    }

}

export async function openModalShareProject(model_id, model_name, model_share_link, model_share_link_qrcode, model_is_password_protected, model_password) {
    let share_project_name_span = document.getElementById("share_project_name_span");
    let copy_share_link_button = document.getElementById("copy_share_link_button");
    let update_model_id_input = document.getElementById("update_model_id_input");
    let copy_share_link_input = document.getElementById("copy_share_link_input");
    let model_share_link_qrcode_img = document.getElementById("model_share_link_qrcode_img");
    let project_is_password_protected_input = document.getElementById("project_is_password_protected_input");
    let project_password_div = document.getElementById("project_password_div");
    let project_password_input = document.getElementById("project_password_input");
    let model_password_error_span = document.getElementById("model_password_error_span");

    if (model_is_password_protected == "True") {
        project_is_password_protected_input.checked = "checked";
        project_password_div.style.display = "block";
        project_password_div.classList.add("open");
    } else {
        project_is_password_protected_input.checked = "";
        project_password_div.style.display = "none";
        project_password_div.classList.remove("open");
    }

    model_password_error_span.innerHTML = "";
    project_password_input.value = model_password;
    update_model_id_input.value = model_id;
    share_project_name_span.innerText = model_name;
    copy_share_link_button.value = model_share_link;
    copy_share_link_input.value = model_share_link;
    model_share_link_qrcode_img.src = model_share_link_qrcode;
    openModal('.modal.share-modal');
}



export async function copyValueToClipboard(input) {
    navigator.clipboard.writeText(input.value);

    let translate_response = await apiCaller("translate", {
        "key": "Copiado!"
    });
    input.innerText = translate_response["success"];
    await sleep(2000);

    translate_response = await apiCaller("translate", {
        "key": "Copiar"
    });
    input.innerText = translate_response["success"];
}

export function showHideElement(element_id) {
    var element = document.getElementById(element_id);
    element.classList.toggle("open");
    if (element.classList.contains("open")) {
        element.style.display = "block";
    } else {
        element.style.display = "none";
    }
}

export async function updateModelFavorite(model_id, model_is_favorite) {
    let update_model_response = await apiCaller("update_model", {
        "model_id": model_id,
        "model_is_favorite": model_is_favorite
    });

    console.log(update_model_response["success"]);
    showUserDicts();
    detectClickOutsideElement()
}

export async function showUserDicts() {
    var user_folder_rows_tbody = document.getElementById("user_folder_rows_tbody");
    var sort_attribute_input = document.getElementById("sort_attribute_input");
    var sort_reverse_input = document.getElementById("sort_reverse_input");

    let panel_create_project_user_dicts_html_response = await apiCaller("panel_create_project_user_dicts_html", {
        "sort_attribute": sort_attribute_input.value,
        "sort_reverse": sort_reverse_input.value,
    });

    user_folder_rows_tbody.innerHTML = panel_create_project_user_dicts_html_response["success"];
}

export async function openRenameModel(model_id, model_filename) {
    var model_filename_input = document.getElementById("model_filename_input");
    var model_id_filename_input = document.getElementById("model_id_filename_input");

    model_filename_input.value = model_filename;
    model_id_filename_input.value = model_id;
    openModal('.modal.rename-modal');
}

export async function saveModelFilename() {
    var model_filename_input = document.getElementById("model_filename_input");
    var model_id_filename_input = document.getElementById("model_id_filename_input");
    var model_filename_error_span = document.getElementById("model_filename_error_span");

    let update_model_response = await apiCaller("update_model", {
        "model_id": model_id_filename_input.value,
        "model_filename": model_filename_input.value
    });

    if ("error" in update_model_response) {
        model_filename_error_span.innerHTML = update_model_response["error"]
    }
    closeModal('.modal.rename-modal');
    showUserDicts()
}

export async function updateModelPassword() {
    var model_id = document.getElementById("update_model_id_input");
    var project_is_password_protected_input = document.getElementById("project_is_password_protected_input");
    var project_password_input = document.getElementById("project_password_input");
    var model_password_error_span = document.getElementById("model_password_error_span");

    let update_model_response = await apiCaller("update_model", {
        "model_id": model_id.value,
        "model_password": project_password_input.value,
        "model_is_password_protected": project_is_password_protected_input.checked
    });

    if ("error" in update_model_response) {
        model_password_error_span.innerHTML = update_model_response["error"]
        return
    }
    closeModal('.modal.share-modal');
    showUserDicts()
}


export async function togglePasswordText(button, input_id) {
    var input = document.getElementById(input_id);
    var icon_img = button.querySelector("img");

    const PASSWORD_SHOW_ICON = "visibility.svg";
    const PASSWORD_HIDE_ICON = "visibility_off.svg";
    let PASSWORD_SHOW_LABEL = "Mostrar senha.";
    let PASSWORD_HIDE_LABEL = "Ocultar senha.";

    let translate_response = await apiCaller("translate", {
        "key": PASSWORD_SHOW_LABEL
    });

    PASSWORD_SHOW_LABEL = translate_response["success"];

    translate_response = await apiCaller("translate", {
        "key": PASSWORD_HIDE_LABEL
    });

    PASSWORD_HIDE_LABEL = translate_response["success"];

    if (input.type == "password") {
        input.type = "text";
        button.setAttribute("aria-label", PASSWORD_HIDE_LABEL);
        icon_img.src = icon_img.src.replace(PASSWORD_SHOW_ICON, PASSWORD_HIDE_ICON);
        return;
    }
    input.type = "password";
    button.setAttribute("aria-label", PASSWORD_SHOW_LABEL);
    icon_img.src = icon_img.src.replace(PASSWORD_HIDE_ICON, PASSWORD_SHOW_ICON);
    return;
}


export async function sortProjectsBy(sort_attribute) {
    console.log("Running sortProjectsBy");
    let sort_attribute_input = document.getElementById("sort_attribute_input");
    let sort_reverse_input = document.getElementById("sort_reverse_input");
    let sort_span = document.getElementById(sort_attribute + "_sort_span");

    if (sort_attribute_input.value === sort_attribute) {
        if (sort_reverse_input.value === "True") {
            sort_reverse_input.value = "False"
        } else {
            sort_reverse_input.value = "True"
        }
    }
    sort_attribute_input.value = sort_attribute;

    if (sort_reverse_input.value === "False") {
        sort_span.innerHTML = "v"
    } else {
        sort_span.innerHTML = "^"
    }

    showUserDicts();
}


document.addEventListener("DOMContentLoaded", function (event) {
    // your code here
    detectClickOutsideElement();
    activateAuginSubscriptionSelection();
    activateDraggableItems();
});