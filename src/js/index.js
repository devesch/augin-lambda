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



// export async function uploadProjectFileToS3(project_target_index, project_target_type) {

// }


export async function uploadModel(input) {
    const process_to_bucket = "upload.augin.app";
    const process_to_bucket_url = "https://upload.augin.app";


    var file_name_array = input.files[0]["name"].split(".")
    var file_name_extension = file_name_array[file_name_array.length - 1];

    let panel_get_aws_upload_keys_response = await apiCaller("panel_get_aws_upload_keys", {
        "create_model": "create_model",
        "key_extension": file_name_extension,
        "bucket": process_to_bucket
    });


    let onProgress = progress => {
        console.log(Math.round(progress * 100) + "%");
    }

    let post_data = {
        "key": panel_get_aws_upload_keys_response["success"]['key'],
        "AWSAccessKeyId": panel_get_aws_upload_keys_response["success"]['AWSAccessKeyId'],
        "policy": panel_get_aws_upload_keys_response["success"]['policy'],
        "signature": panel_get_aws_upload_keys_response["success"]['signature'],
        "file": input.files[0]
    }

    await uploadWithProgressBar(panel_get_aws_upload_keys_response["success"]['url'], post_data, onProgress);




}


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

const uploadWithProgressBar = (url, post_data, onProgress) =>
    new Promise((resolve, reject) => {
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