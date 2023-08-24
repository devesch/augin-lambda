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