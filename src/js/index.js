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

export async function deleteModelProcessing(model_id) {
    console.log("Running deleteModelProcessing");
    let model_delete_response = await apiCaller("model_delete", {
        "model_id": model_id
    });
    await js.index.processingProjectsUpdateUl();
}

export async function processingProjectsUpdateUl() {
    console.log("Running processingProjectsUpdateUl");
    let models_in_process_ul = document.getElementById("models_in_process_ul");
    let panel_explore_projects_models_in_processing_html_response = await apiCaller("panel_explore_projects_models_in_processing_html", {});
    models_in_process_ul.innerHTML = panel_explore_projects_models_in_processing_html_response["success"];
    // await animatingProgressBar();
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

export async function checkUploadModelFile(post_data) {
    console.log("Running checkUploadModelFile")
    let message = document.getElementById("message_" + post_data["element_index"]);
    let delete_button = document.getElementById("delete_button_" + post_data["element_index"]);
    let model_id = document.getElementById("model_id_" + post_data["element_index"]);
    let has_error = document.getElementById("has_error_" + post_data["element_index"]);

    let panel_create_project_check_file_response = await apiCaller("panel_create_project_check_file", {
        "key": post_data["key"]
    });
    if ("error" in panel_create_project_check_file_response) {
        message.innerHTML = panel_create_project_check_file_response["error"];
        delete_button.style = "";
        has_error.value = "True";
        checkIfCreateProjectSubmitButtonIsAvailable(false);
    } else {
        model_id.value = panel_create_project_check_file_response["models_ids"];
        message.innerHTML = "Upload realizado com sucesso";
        checkIfCreateProjectSubmitButtonIsAvailable();
    }


}


export async function checkIfCreateProjectIsFederated() {
    let federated_switch = document.getElementById("federated_switch");

    let uploading_element_has_more_than_one_file = document.querySelectorAll(".uploading_element_has_more_than_one_file");
    let uploading_element_message = document.querySelectorAll(".uploading_element_message");

    if (uploading_element_message.length > 1) {
        federated_switch.setAttribute("active");
    } else {
        federated_switch.setAttribute("not_active");
    }


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
        xhr.upload.addEventListener('progress', (e) => {
            let progress_element = document.getElementById("progress_" + post_data["element_index"]);
            progress_element.value = Math.round((e.loaded / e.total) * 100);
            checkIfCreateProjectSubmitButtonIsAvailable(false);
        });
        xhr.addEventListener('load', () => {
            checkUploadModelFile(post_data);
            checkIfCreateProjectIsFederated()
            resolve({
                status: xhr.status,
                body: xhr.responseText
            });
        });
        xhr.addEventListener('error', () => reject(new Error('File upload failed')));
        xhr.addEventListener('abort', () => reject(new Error('File upload aborted')));
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

    let buttons = document.querySelectorAll(".button--explore-more-options");
    let buttonsLength = buttons.length;

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

        if (buttonsLength > 0) {
            activateExploreMenuButton(event.target, buttons, buttonsLength);
        }

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
 * @param {NodeListOf HTMLButtonElement} buttons 
 * @param {int} buttonsLength 
 */
export function activateExploreMenuButton(clickTarget, buttons, buttonsLength) {
    let i = 0;
    while (i < buttonsLength) {
        let currentMenu = document.getElementById(buttons[i].getAttribute("aria-controls"));
        if (buttons[i].contains(clickTarget)) {
            if (currentMenu.classList.contains("none")) {
                currentMenu.classList.remove("none");
                buttons[i].setAttribute("aria-expanded", "true");
            } else {
                currentMenu.classList.add("none");
                buttons[i].setAttribute("aria-expanded", "false");
            }
        } else {
            currentMenu.classList.add("none");
            buttons[i].setAttribute("aria-expanded", "false");
        }
        i++;
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

document.addEventListener("DOMContentLoaded", function (event) {
    // your code here
    detectClickOutsideElement();
    activateAuginSubscriptionSelection();
    // activateExploreMenuButton();
});