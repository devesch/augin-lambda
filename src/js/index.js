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
    let update_model_response = await apiCaller("update_model", {
        "command": "delete_model",
        "model_id": model_id
    });
    await js.index.processingProjectsUpdateUl();
}

export async function deleteModelFromExplore() {
    var model_id_delete_input = document.getElementById("model_id_delete_input");
    var model_delete_error_span = document.getElementById("model_delete_error_span");

    let update_model_response = await apiCaller("update_model", {
        "command": "delete_model",
        "model_id": model_id_delete_input.value
    });

    if ("error" in update_model_response) {
        model_delete_error_span.innerHTML = update_model_response["error"]
    }

    await js.index.showUserDicts();
    closeModal(".modal.delete-modal");
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

const uploadedFilesNames = [];
export async function uploadModel(input) {
    const files = input.files;
    const process_to_bucket = "upload.augin.app";
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        if (uploadedFilesNames.includes(file.name)) {
            continue;
        }

        checkIfCreateProjectSubmitButtonIsAvailable(false);

        uploadedFilesNames.push(file.name);


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

        let uploading_div = document.getElementById("uploading_div");
        uploading_div.insertAdjacentHTML("beforeend", panel_create_project_uploading_html_response["success"]);
        // Increment the index for the next upload
        uploading_index_input.value = parseInt(current_index) + 1;
        uploadWithProgressBar(panel_get_aws_upload_keys_response["success"]['url'], post_data);
    }
}


export async function checkUploadModelFile(post_data) {
    let translate_response = await apiCaller("translate", {
        "key": "Verificando arquivos..."
    });

    let message = document.getElementById("message_" + post_data["element_index"]);
    message.innerHTML = translate_response["success"];

    let panel_create_project_check_file_response = await apiCaller("panel_create_project_check_file", {
        "key": post_data["key"]
    });

    let delete_button = document.getElementById("delete_button_" + post_data["element_index"]);
    let model_id = document.getElementById("model_id_" + post_data["element_index"]);
    let has_more_than_one_file = document.getElementById("has_more_than_one_file_" + post_data["element_index"]);
    let progress_element = document.getElementById("progress_" + post_data["element_index"]);

    if ("error" in panel_create_project_check_file_response) {
        progress_element.classList.add("failed");
        let message = document.getElementById("message_" + post_data["element_index"]);
        message.innerHTML = panel_create_project_check_file_response["error"];
        delete_button.style = "";
        let has_error = document.getElementById("has_error_" + post_data["element_index"]);
        has_error.value = "True";
        checkIfCreateProjectSubmitButtonIsAvailable(false);
    } else {
        progress_element.classList.add("success");
        model_id.value = panel_create_project_check_file_response["models_ids"];
        has_more_than_one_file.value = panel_create_project_check_file_response["has_more_than_one_file"];

        let translate_response = await apiCaller("translate", {
            "key": "Upload realizado com sucesso."
        });

        let message = document.getElementById("message_" + post_data["element_index"]);
        message.innerHTML = translate_response["success"];
        let has_error = document.getElementById("has_error_" + post_data["element_index"]);
        has_error.value = "False";
        checkIfCreateProjectSubmitButtonIsAvailable();
        checkIfCreateProjectIsFederated();
    }
}


export async function checkIfCreateProjectIsFederated() {
    let federated_switch_div = document.getElementById("federated_switch_div");
    let uploading_element_has_more_than_one_file = document.querySelectorAll('[id^="has_more_than_one_file_"]');
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
    let has_errors = document.querySelectorAll('[id^="has_error_"]');

    if (is_submitable) {
        for (let has_error of has_errors) {
            if (has_error.value === "") {
                submit_form_button.setAttribute("disabled", "disabled");
                return
            }
        }
        if (is_submitable) {
            submit_form_button.removeAttribute("disabled");
        }
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
            sleep(500);
            checkUploadModelFile(post_data);
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

export async function openModalDeleteProject(model_id, model_name, model_used_in_federated_ids) {
    var delete_model_name_span = document.getElementById("delete_model_name_span");
    var model_id_delete_input = document.getElementById("model_id_delete_input");
    var model_delete_error_span = document.getElementById("model_delete_error_span");
    var delete_model_used_in_federated_ids_span = document.getElementById("delete_model_used_in_federated_ids_span");

    console.log("model_used_in_federated_ids", model_used_in_federated_ids);
    if (model_used_in_federated_ids === "True") {
        delete_model_used_in_federated_ids_span.style.display = "";
    } else {
        delete_model_used_in_federated_ids_span.style.display = "none";
    }
    delete_model_name_span.innerText = model_name;
    model_id_delete_input.value = model_id;
    model_delete_error_span.innerHTML = "";
    openModal(".modal.delete-modal");

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

export async function openModalFavoriteProject(model_id, model_is_favorite) {
    let update_model_response = await apiCaller("update_model", {
        "command": "update_favorite",
        "model_id": model_id,
        "model_is_favorite": model_is_favorite
    });
    showUserDicts();
}

export async function showUserDicts() {
    var user_folder_rows_tbody = document.getElementById("user_folder_rows_tbody");
    var sort_attribute_input = document.getElementById("sort_attribute_input");
    var sort_reverse_input = document.getElementById("sort_reverse_input");
    var folder_path_span = document.getElementById("folder_path_span");

    var folder_id_input = document.getElementById("folder_id_input");
    var folder_path_input = document.getElementById("folder_path_input");

    var user_dicts_return_to_root_span = document.getElementById("user_dicts_return_to_root_span");

    let panel_explore_project_user_dicts_html_response = await apiCaller("panel_explore_project_user_dicts_html", {
        "sort_attribute": sort_attribute_input.value,
        "sort_reverse": sort_reverse_input.value,
        "folder_id": folder_id_input.value,
    });

    user_folder_rows_tbody.innerHTML = panel_explore_project_user_dicts_html_response["success"];
    folder_path_span.innerHTML = folder_path_input.value;

    if (folder_path_input.value) {
        user_dicts_return_to_root_span.style.display = "";
    } else {
        user_dicts_return_to_root_span.style.display = "none";
    }
}

export async function openModalRenameProject(model_id, model_name) {
    var model_name_input = document.getElementById("model_name_input");
    var model_id_name_input = document.getElementById("model_id_name_input");

    model_name_input.value = model_name;
    model_id_name_input.value = model_id;
    openModal('.modal.rename-modal');
}

export async function saveModelName() {
    var model_name_input = document.getElementById("model_name_input");
    var model_id_name_input = document.getElementById("model_id_name_input");
    var model_name_error_span = document.getElementById("model_name_error_span");

    let update_model_response = await apiCaller("update_model", {
        "command": "update_name",
        "model_id": model_id_name_input.value,
        "model_name": model_name_input.value
    });

    if ("error" in update_model_response) {
        model_name_error_span.innerHTML = update_model_response["error"]
    }
    showUserDicts()
    closeModal('.modal.rename-modal');
}

export async function updateModelPassword() {
    var model_id = document.getElementById("update_model_id_input");
    var project_is_password_protected_input = document.getElementById("project_is_password_protected_input");
    var project_password_input = document.getElementById("project_password_input");
    var model_password_error_span = document.getElementById("model_password_error_span");

    let update_model_response = await apiCaller("update_model", {
        "command": "update_password",
        "model_id": model_id.value,
        "model_password": project_password_input.value,
        "model_is_password_protected": project_is_password_protected_input.checked
    });

    if ("error" in update_model_response) {
        model_password_error_span.innerHTML = update_model_response["error"]
        return
    }
    showUserDicts()
    closeModal('.modal.share-modal');
}


export async function togglePasswordText(button, input_id) {
    var input = document.getElementById(input_id);
    var icon_img = button.querySelector("img");

    const PASSWORD_SHOW_ICON = "visibility.svg";
    const PASSWORD_HIDE_ICON = "visibility_off.svg";
    let PASSWORD_SHOW_LABEL = "Mostrar senha.";
    let PASSWORD_HIDE_LABEL = "Ocultar senha.";
    if (input.type == "password") {
        input.type = "text";
        let translate_response = await apiCaller("translate", {
            "key": PASSWORD_HIDE_LABEL
        });
        PASSWORD_HIDE_LABEL = translate_response["success"];
        button.setAttribute("aria-label", PASSWORD_HIDE_LABEL);
        icon_img.src = icon_img.src.replace(PASSWORD_SHOW_ICON, PASSWORD_HIDE_ICON);
        return;
    }
    input.type = "password";
    icon_img.src = icon_img.src.replace(PASSWORD_HIDE_ICON, PASSWORD_SHOW_ICON);
    let translate_response = await apiCaller("translate", {
        "key": PASSWORD_SHOW_LABEL
    });
    PASSWORD_SHOW_LABEL = translate_response["success"];
    button.setAttribute("aria-label", PASSWORD_SHOW_LABEL);
    return;
}


export async function sortProjectsBy(sort_attribute) {
    let sort_attribute_input = document.getElementById("sort_attribute_input");
    let sort_reverse_input = document.getElementById("sort_reverse_input");
    let sort_image = document.getElementById(sort_attribute + "_sort_image");

    if (sort_attribute_input.value === sort_attribute) {
        if (sort_reverse_input.value === "True") {
            sort_reverse_input.value = "False"
        } else {
            sort_reverse_input.value = "True"
        }
    }
    sort_attribute_input.value = sort_attribute;

    if (sort_reverse_input.value === "False") {
        sort_image.style.transform = "";
        let translate_response = await apiCaller("translate", {
            "key": "Ícone de seta para baixo"
        });
        sort_image.alt = translate_response["success"]
    } else {
        sort_image.style.transform = "rotate(180deg)";
        let translate_response = await apiCaller("translate", {
            "key": "Ícone de seta para cima"
        });
        sort_image.alt = translate_response["success"]
    }

    var sort_images = document.querySelectorAll('[id$="_sort_image"]');
    for (let image of sort_images) {
        if (sort_image.id != image.id) {
            image.style.display = "none";
        } else {
            image.style.display = "";
        }
    }
    showUserDicts();
}



export async function openModalCategoryProject(model_id, model_category) {
    var model_id_selected_category_input = document.getElementById("model_id_selected_category_input");
    var model_category_error_span = document.getElementsByName("model_category_error_span");

    model_id_selected_category_input.value = model_id;
    model_category_error_span.innerHTML = "";

    var select_category_inputs = document.getElementsByName("select_category");
    for (let category of select_category_inputs) {
        if (category.checked) {
            category.checked = false;
        }
    }

    if (model_category != "") {
        var model_category_radio_input = document.getElementById(model_category);
        model_category_radio_input.checked = true;
    }

    openModal(".modal.select-category-modal");
}

export async function updateModelCategory() {
    var model_id_selected_category_input = document.getElementById("model_id_selected_category_input");
    var select_category_inputs = document.getElementsByName("select_category");
    var model_category_error_span = document.getElementsByName("model_category_error_span");

    var selected_category = "";

    for (let cat of select_category_inputs) {
        if (cat.checked) {
            selected_category = cat.id;
        }
    }

    let update_model_response = await apiCaller("update_model", {
        "command": "update_category",
        "model_id": model_id_selected_category_input.value,
        "model_category": selected_category
    });

    if ("error" in update_model_response) {
        model_category_error_span.innerHTML = update_model_response["error"];
    }

    showUserDicts();
    closeModal(".modal.select-category-modal");
}



document.addEventListener("DOMContentLoaded", function (event) {
    // your code here
    detectClickOutsideElement();
    activateAuginSubscriptionSelection();
    activateDraggableItems();
});



export async function openModalUpdateProject(model_id) {
    var model_id_update_model_input = document.getElementById("model_id_update_model_input");
    var model_update_error_span = document.getElementById("model_update_error_span");
    var update_model_user_folder_rows_tbody = document.getElementById("update_model_user_folder_rows_tbody");
    var update_modal_return_folder_span = document.getElementById("update_modal_return_folder_span");
    var update_modal_folder_path_span = document.getElementById("update_modal_folder_path_span");

    update_modal_return_folder_span.style.display = "none";
    update_modal_folder_path_span.style.display = "none";

    var panel_explore_project_user_dicts_html_response = await apiCaller("panel_explore_project_user_dicts_html", {
        "model_html": "update"
    })

    model_id_update_model_input.value = model_id;
    model_update_error_span.innerHTML = "";

    update_model_user_folder_rows_tbody.innerHTML = panel_explore_project_user_dicts_html_response["success"];

    var model_for_updates = document.getElementsByName("model_for_update");
    for (let model_for_update of model_for_updates) {
        model_for_update.checked = false;
    }

    openModal(".modal.update-modal");
}





export async function openModalConfirmUpdateProject() {
    var model_id_update_model_input = document.getElementById("model_id_update_model_input");
    var model_update_error_span = document.getElementById("model_update_error_span");
    var model_for_updates = document.getElementsByName("model_for_update");
    var selected_model_id = "";

    for (let model_for_update of model_for_updates) {
        if (model_for_update.checked) {
            selected_model_id = model_for_update.value;
        }
    }

    if (selected_model_id === "") {
        var translate_response = await apiCaller("translate", {
            "key": "É necessário selecionar o projeto que será usado para atualizar o projeto atual."
        })
        model_update_error_span.innerHTML = translate_response["success"];
        return
    }


    var panel_explore_projects_modal_update_confirm_html_response = await apiCaller("panel_explore_projects_modal_update_confirm_html", {
        "original_model_id": model_id_update_model_input.value,
        "new_model_id": selected_model_id
    })

    var update_confirm_modal_div = document.getElementById("update_confirm_modal_div");
    var model_update_confirm_error_span = document.getElementById("model_update_confirm_error_span");

    update_confirm_modal_div.innerHTML = panel_explore_projects_modal_update_confirm_html_response["success"];
    model_update_confirm_error_span.innerHTML = "";

    closeModal(".modal.update-modal");
    openModal(".modal.update-confirm-modal");
}

export async function closeModalConfirmUpdateProject() {
    closeModal(".modal.update-confirm-modal");
    openModal(".modal.update-modal");
}

export async function updateProjectFile() {
    var model_id_update_model_input = document.getElementById("model_id_update_model_input");
    var model_for_updates = document.getElementsByName("model_for_update");
    var selected_model_id = "";
    var model_update_confirm_error_span = document.getElementById("model_update_confirm_error_span");

    for (let model_for_update of model_for_updates) {
        if (model_for_update.checked) {
            selected_model_id = model_for_update.value;
        }
    }

    let update_model_response = await apiCaller("update_model", {
        "command": "update_model_files",
        "model_id": model_id_update_model_input.value,
        "selected_model_id": selected_model_id
    });

    if ("error" in update_model_response) {
        model_update_confirm_error_span.innerHTML = update_model_response["error"];
    } else {
        showUserDicts();
        closeModal(".modal.update-confirm-modal");
    }
}



export async function openModalCreateFolder() {
    var create_folder_error_span = document.getElementsByName("create_folder_error_span");
    var folder_name_input = document.getElementById("folder_name_input");

    folder_name_input.value = "";
    create_folder_error_span.innerHTML = "";
    openModal('.modal.create-folder-modal');
}

export async function saveCreateFolder() {
    var folder_name_input = document.getElementById("folder_name_input");
    var folder_id_input = document.getElementById("folder_id_input");
    var create_folder_error_span = document.getElementsByName("create_folder_error_span");

    var update_user_response = await apiCaller("update_user", {
        "command": "create_folder",
        "folder_name": folder_name_input.value,
        "folder_id": folder_id_input.value,
    });

    if ("error" in update_user_response) {
        create_folder_error_span.innerHTML = update_user_response["error"];
    } else {
        folder_name_input.value = "";
        showUserDicts();
        closeModal(".modal.create-folder-modal");
    }
}

export async function openFolder(folder_id, folder_path, return_folder_path = false) {
    var folder_id_input = document.getElementById("folder_id_input");
    var folder_path_input = document.getElementById("folder_path_input");
    folder_id_input.value = folder_id;

    if (!return_folder_path) {
        if (folder_path) {
            folder_path_input.value = folder_path_input.value + folder_path;
        } else {
            folder_path_input.value = ""
        }
    } else {
        folder_path_input.value = folder_path_input.value.split(folder_path)[0];
        folder_path_input.value += folder_path;
    }
    showUserDicts();
}


export async function openReturnFolder() {
    var folder_id_input = document.getElementById("folder_id_input");

    var update_user_response = await apiCaller("update_user", {
        "command": "get_root_folder",
        "folder_id": folder_id_input.value
    });

    if ("success" in update_user_response) {
        openFolder(update_user_response["success"]["folder_id"], update_user_response["success"]["folder_path"], true)
    } else {
        openFolder("", "")
    }
}




export async function openModalDeleteFolder(folder_id, folder_name) {
    var folder_delete_folder_id_input = document.getElementById("folder_delete_folder_id_input");
    var delete_folder_name_span = document.getElementById("delete_folder_name_span");
    var delete_folder_error_span = document.getElementById("delete_folder_error_span");

    folder_delete_folder_id_input.value = folder_id;
    delete_folder_name_span.innerHTML = folder_name;
    delete_folder_error_span.innerHTML = "";
    openModal('.modal.delete-folder-modal')
}


export async function openModalRenameFolders(folder_id, folder_name) {
    var folder_rename_folder_id = document.getElementById("folder_rename_folder_id");
    var folder_rename_input = document.getElementById("folder_rename_input");
    var rename_folder_error_span = document.getElementsByName("rename_folder_error_span");

    folder_rename_folder_id.value = folder_id;
    folder_rename_input.value = folder_name;
    rename_folder_error_span.innerHTML = "";
    openModal('.modal.rename-folder-modal')
}

export async function saveRenameFolder() {
    var folder_rename_input = document.getElementById("folder_rename_input");
    var folder_rename_folder_id = document.getElementById("folder_rename_folder_id");
    var rename_folder_error_span = document.getElementsByName("rename_folder_error_span");

    var update_user_response = await apiCaller("update_user", {
        "command": "rename_folder",
        "folder_new_name": folder_rename_input.value,
        "folder_id": folder_rename_folder_id.value,
    });

    if ("error" in update_user_response) {
        rename_folder_error_span.innerHTML = update_user_response["error"];
    } else {
        showUserDicts();
        closeModal(".modal.rename-folder-modal");
        folder_rename_input.value = "";
    }
}

export async function saveDeleteFolder() {
    var folder_delete_folder_id_input = document.getElementById("folder_delete_folder_id_input");
    var delete_folder_name_span = document.getElementById("delete_folder_name_span");
    var delete_folder_error_span = document.getElementById("delete_folder_error_span");

    var update_user_response = await apiCaller("update_user", {
        "command": "delete_folder",
        "folder_id": folder_delete_folder_id_input.value
    });

    if ("error" in update_user_response) {
        delete_folder_error_span.innerHTML = update_user_response["error"];
    } else {
        showUserDicts();
        closeModal('.modal.delete-folder-modal')
        delete_folder_error_span.innerHTML = "";
        delete_folder_name_span.innerHTML = "";
    }
}

export async function FavoriteFolder(folder_id, folder_is_favorite) {
    let update_user = await apiCaller("update_user", {
        "command": "update_folder_favorite",
        "folder_id": folder_id,
        "folder_is_favorite": folder_is_favorite
    });
    showUserDicts();
}


export async function refreshUpdateModal(folder_id) {
    var update_modal_folder_id = document.getElementById("update_modal_folder_id");
    var update_model_user_folder_rows_tbody = document.getElementById("update_model_user_folder_rows_tbody");
    var update_modal_folder_path_span = document.getElementById("update_modal_folder_path_span");
    var update_modal_return_folder_span = document.getElementById("update_modal_return_folder_span");

    var panel_explore_project_user_dicts_html_response = await apiCaller("panel_explore_project_user_dicts_html", {
        "folder_id": folder_id,
        "model_html": "update"
    })

    if (folder_id) {
        var update_user_response = await apiCaller("update_user", {
            "command": "get_folder",
            "folder_id": folder_id
        });
        update_modal_folder_path_span.innerHTML = update_user_response["success"]["folder_path"];
        update_modal_folder_path_span.style.display = "";
        update_modal_return_folder_span.style.display = "";
    } else {
        update_modal_folder_path_span.style.display = "none";
        update_modal_return_folder_span.style.display = "none";
    }
    update_modal_folder_id.value = folder_id;
    update_model_user_folder_rows_tbody.innerHTML = panel_explore_project_user_dicts_html_response["success"];
}

export async function openReturnFolderModalUpdate() {
    var update_modal_folder_id = document.getElementById("update_modal_folder_id");

    var update_user_response = await apiCaller("update_user", {
        "command": "get_root_folder",
        "folder_id": update_modal_folder_id.value
    });
    if ("success" in update_user_response) {
        refreshUpdateModal(update_user_response["success"]["folder_id"]);
    } else {
        refreshUpdateModal("");
    }
}


export async function openModalMoveProject(model_id) {
    var model_id_move_modal_input = document.getElementById("model_id_move_modal_input");
    var move_modal_error_span = document.getElementById("move_modal_error_span");
    var move_model_user_folder_rows_tbody = document.getElementById("move_model_user_folder_rows_tbody");
    var move_modal_return_folder_span = document.getElementById("move_modal_return_folder_span");
    var move_modal_folder_path_span = document.getElementById("move_modal_folder_path_span");
    var move_modal_folder_id = document.getElementById("move_modal_folder_id");

    move_modal_return_folder_span.style.display = "none";
    move_modal_folder_path_span.style.display = "none";

    var panel_explore_project_user_dicts_html_response = await apiCaller("panel_explore_project_user_dicts_html", {
        "model_html": "move"
    })

    model_id_move_modal_input.value = model_id;
    move_modal_error_span.innerHTML = "";
    move_modal_folder_id.value = "";
    move_model_user_folder_rows_tbody.innerHTML = panel_explore_project_user_dicts_html_response["success"];


    openModal(".modal.move-modal");
}


export async function openModalMoveFolder(folder_id) {
    var folder_id_move_folder_modal_input = document.getElementById("folder_id_move_folder_modal_input");
    var move_folder_modal_error_span = document.getElementById("move_folder_modal_error_span");
    var move_folder_model_user_folder_rows_tbody = document.getElementById("move_folder_model_user_folder_rows_tbody");
    var move_folder_modal_return_folder_span = document.getElementById("move_folder_modal_return_folder_span");
    var move_folder_modal_folder_path_span = document.getElementById("move_folder_modal_folder_path_span");
    var move_folder_modal_folder_id = document.getElementById("move_folder_modal_folder_id");

    move_folder_modal_return_folder_span.style.display = "none";
    move_folder_modal_folder_path_span.style.display = "none";

    var panel_explore_project_user_dicts_html_response = await apiCaller("panel_explore_project_user_dicts_html", {
        "model_html": "move_folder"
    })

    folder_id_move_folder_modal_input.value = folder_id;
    move_folder_modal_error_span.innerHTML = "";
    move_folder_modal_folder_id.value = "";
    move_folder_model_user_folder_rows_tbody.innerHTML = panel_explore_project_user_dicts_html_response["success"];


    openModal(".modal.move-folder-modal");
}


export async function refreshMoveFolderModal(folder_id) {
    var move_folder_modal_folder_id = document.getElementById("move_folder_modal_folder_id");
    var move_folder_model_user_folder_rows_tbody = document.getElementById("move_folder_model_user_folder_rows_tbody");
    var move_folder_modal_return_folder_span = document.getElementById("move_folder_modal_return_folder_span");
    var move_folder_modal_folder_path_span = document.getElementById("move_folder_modal_folder_path_span");


    var panel_explore_project_user_dicts_html_response = await apiCaller("panel_explore_project_user_dicts_html", {
        "folder_id": folder_id,
        "model_html": "move_folder"
    })

    if (folder_id) {
        var update_user_response = await apiCaller("update_user", {
            "command": "get_folder",
            "folder_id": folder_id
        });
        move_folder_modal_return_folder_span.style.display = "";
        move_folder_modal_folder_path_span.innerHTML = update_user_response["success"]["folder_path"];
        move_folder_modal_folder_path_span.style.display = "";
    } else {
        move_folder_modal_return_folder_span.style.display = "none";
        move_folder_modal_folder_path_span.style.display = "none";
    }

    move_folder_modal_folder_id.value = folder_id;
    move_folder_model_user_folder_rows_tbody.innerHTML = panel_explore_project_user_dicts_html_response["success"];

}


export async function openReturnFolderModalMoveFolder() {
    var move_folder_modal_folder_id = document.getElementById("move_folder_modal_folder_id");

    var update_user_response = await apiCaller("update_user", {
        "command": "get_root_folder",
        "folder_id": move_folder_modal_folder_id.value
    });
    if ("success" in update_user_response) {
        refreshMoveFolderModal(update_user_response["success"]["folder_id"]);
    } else {
        refreshMoveFolderModal("");
    }
}




export async function saveConfirmMoveFolder() {
    var folder_id_move_folder_modal_input = document.getElementById("folder_id_move_folder_modal_input");
    var move_folder_modal_error_span = document.getElementById("move_folder_modal_error_span");
    var move_folder_modal_folder_id = document.getElementById("move_folder_modal_folder_id");

    var update_user_response = await apiCaller("update_user", {
        "command": "move_folder_to_another_folder",
        "folder_id": folder_id_move_folder_modal_input.value,
        "selected_folder_id": move_folder_modal_folder_id.value
    })

    if ("error" in update_user_response) {
        move_folder_modal_error_span.innerHTML = update_user_response["error"];
        return
    }

    closeModal(".modal.move-folder-modal");
    showUserDicts();
}

export async function refreshMoveModal(folder_id) {
    var move_modal_folder_id = document.getElementById("move_modal_folder_id");
    var move_model_user_folder_rows_tbody = document.getElementById("move_model_user_folder_rows_tbody");
    var move_modal_return_folder_span = document.getElementById("move_modal_return_folder_span");
    var move_modal_folder_path_span = document.getElementById("move_modal_folder_path_span");


    var panel_explore_project_user_dicts_html_response = await apiCaller("panel_explore_project_user_dicts_html", {
        "folder_id": folder_id,
        "model_html": "move"
    })

    if (folder_id) {
        var update_user_response = await apiCaller("update_user", {
            "command": "get_folder",
            "folder_id": folder_id
        });
        move_modal_return_folder_span.style.display = "";
        move_modal_folder_path_span.innerHTML = update_user_response["success"]["folder_path"];
        move_modal_folder_path_span.style.display = "";
    } else {
        move_modal_return_folder_span.style.display = "none";
        move_modal_folder_path_span.style.display = "none";
    }

    move_modal_folder_id.value = folder_id;
    move_model_user_folder_rows_tbody.innerHTML = panel_explore_project_user_dicts_html_response["success"];

}

export async function openReturnFolderModalMove() {
    var move_modal_folder_id = document.getElementById("move_modal_folder_id");

    var update_user_response = await apiCaller("update_user", {
        "command": "get_root_folder",
        "folder_id": move_modal_folder_id.value
    });
    if ("success" in update_user_response) {
        refreshMoveModal(update_user_response["success"]["folder_id"]);
    } else {
        refreshMoveModal("");
    }
}

export async function saveConfirmMoveProject() {
    var model_id_move_modal_input = document.getElementById("model_id_move_modal_input");
    var move_modal_error_span = document.getElementById("move_modal_error_span");
    var move_modal_folder_id = document.getElementById("move_modal_folder_id");

    var update_user_response = await apiCaller("update_user", {
        "command": "move_model_folder",
        "model_id": model_id_move_modal_input.value,
        "selected_folder_id": move_modal_folder_id.value
    })

    if ("error" in update_user_response) {
        move_modal_error_span.innerHTML = update_user_response["error"];
        return
    }

    closeModal(".modal.move-modal");
    showUserDicts();
}

export async function downloadFolders(folder_id) {
    var generate_download_folder_error_span = document.getElementById("generate_download_folder_error_span");
    generate_download_folder_error_span.innerHTML = "";
    openModal(".modal.generate-download-folder-modal");

    var update_user_response = await apiCaller("update_user", {
        "command": "download_folder",
        "folder_id": folder_id
    });

    if ("success" in update_user_response) {
        downloadFileFromList(update_user_response["success"])
        closeModal(".modal.generate-download-folder-modal");
    } else {
        generate_download_folder_error_span.innerHTML = update_user_response["error"];
    }
}

export async function downloadFileFromList(download_list) {
    const models = download_list;

    for (const model of models) {
        const modelLink = model['model_link'];
        const modelName = model['model_save_name'];
        try {
            const response = await fetch(modelLink);
            if (response.ok) {
                const blob = await response.blob();
                const blobUrl = URL.createObjectURL(blob);
                const anchor = document.createElement('a');
                anchor.style.display = 'none';
                anchor.href = blobUrl;
                anchor.download = modelName;
                document.body.appendChild(anchor);
                anchor.click();
                document.body.removeChild(anchor);
                URL.revokeObjectURL(blobUrl);
            } else {
                console.error(`Failed to fetch ${modelLink}: ${response.statusText}`);
            }
        } catch (err) {
            console.error(`An error occurred while downloading ${modelLink}: ${err}`);
        }
    }
}


export async function openModalDownloadProject(model_id) {
    var generate_download_error_span = document.getElementById("generate_download_error_span");
    generate_download_error_span.innerHTML = "";
    openModal(".modal.generate-download-modal");

    var update_user_response = await apiCaller("update_user", {
        "command": "download_model",
        "model_id": model_id
    });

    if ("success" in update_user_response) {
        downloadFileFromList(update_user_response["success"])
        closeModal(".modal.generate-download-modal");
    } else {
        generate_download_error_span.innerHTML = update_user_response["error"];
    }
}

export async function openModalCreateFederatedProject() {
    closeModal(".modal.create-federated-select-models-modal");
    openModal(".modal.create-federated-modal");
}

export async function saveCreateFederatedProject() {
    var create_federated_model_user_folder_rows_tbody = document.getElementById("create_federated_model_user_folder_rows_tbody");
    var panel_explore_project_user_dicts_html_response = await apiCaller("panel_explore_project_user_dicts_html", {
        "model_html": "create_federated"
    })
    create_federated_model_user_folder_rows_tbody.innerHTML = panel_explore_project_user_dicts_html_response["success"];
    closeModal(".modal.create-federated-modal");
    openModal(".modal.create-federated-select-models-modal");
}

export async function saveConfirmCreateFederatedProject() {
    var federated_model_name_input = document.getElementById("federated_model_name_input");
    var create_federated_error_span = document.getElementById("create_federated_error_span");

    var update_model_response = await apiCaller("update_model", {
        "command": "create_federated",
        "federated_name": federated_model_name_input.value,
        "federated_required_ids": federated_required_ids_list
    })

    if ("error" in update_model_response) {
        create_federated_error_span.innerHTML = update_model_response["error"];
    } else {
        federated_model_name_input.value = "";
        create_federated_error_span.innerHTML = "";
        closeModal(".modal.create-federated-select-models-modal");
    }
}

export async function openReturnFolderModalCreateFederated() {
    var create_federated_modal_folder_id = document.getElementById("create_federated_modal_folder_id");

    var update_user_response = await apiCaller("update_user", {
        "command": "get_root_folder",
        "folder_id": create_federated_modal_folder_id.value
    });
    if ("success" in update_user_response) {
        refreshCreateFederatedModal(update_user_response["success"]["folder_id"]);
    } else {
        refreshCreateFederatedModal("");
    }
}


export async function refreshCreateFederatedModal(folder_id) {
    var create_federated_modal_folder_id = document.getElementById("create_federated_modal_folder_id");
    var create_federated_model_user_folder_rows_tbody = document.getElementById("create_federated_model_user_folder_rows_tbody");
    var create_federated_modal_folder_path_span = document.getElementById("create_federated_modal_folder_path_span");
    var create_federated_modal_return_folder_span = document.getElementById("create_federated_modal_return_folder_span");

    var panel_explore_project_user_dicts_html_response = await apiCaller("panel_explore_project_user_dicts_html", {
        "folder_id": folder_id,
        "model_html": "create_federated"
    })

    if (folder_id) {
        var update_user_response = await apiCaller("update_user", {
            "command": "get_folder",
            "folder_id": folder_id
        });
        create_federated_modal_folder_path_span.innerHTML = update_user_response["success"]["folder_path"];
        create_federated_modal_folder_path_span.style.display = "";
        create_federated_modal_return_folder_span.style.display = "";
    } else {
        create_federated_modal_folder_path_span.style.display = "none";
        create_federated_modal_return_folder_span.style.display = "none";
    }
    create_federated_modal_folder_id.value = folder_id;
    create_federated_model_user_folder_rows_tbody.innerHTML = panel_explore_project_user_dicts_html_response["success"];

    var federated_required_id_inputs = document.querySelectorAll('[id$="_federated_required_id_input"]');
    for (let federated_required_id_input of federated_required_id_inputs) {
        if (federated_required_ids_list.includes(federated_required_id_input.value)) {
            federated_required_id_input.checked = true;
        } else {
            federated_required_id_input.checked = false;
        }
    }

}

const federated_required_ids_list = [];

export async function addOrRemoveModelFromCreateFederatedList(input) {
    console.log("input", input);
    console.log("input.checked", input.checked);

    if (federated_required_ids_list.includes(input.value) && !input.checked) {
        federated_required_ids_list.splice(federated_required_ids_list.indexOf(input.value), 1);
    } else if (!federated_required_ids_list.includes(input.value) && input.checked) {
        federated_required_ids_list.push(input.value);
    }

    console.log("federated_required_ids_list", federated_required_ids_list);
}