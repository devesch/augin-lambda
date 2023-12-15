"use strict";



export async function showSelectedPaymentPage(index) {
    let decrease_history_page_button = document.getElementById("decrease_history_page_button");
    let increase_history_page_button = document.getElementById("increase_history_page_button");
    let payment_history_pages_count_input = document.getElementById("payment_history_pages_count_input");
    let current_button = document.getElementById("payment_history_page_button_" + index);
    let payment_history_current_page_input = document.getElementById("payment_history_current_page_input");
    let payment_history_page_buttons = document.querySelectorAll('[id^="payment_history_page_button_"]');
    let payment_history_rows = document.querySelectorAll('[class^="payment_history_row_page_"]');

    payment_history_current_page_input.value = index;

    for (let payment_history_row of payment_history_rows) {
        if (payment_history_row.classList.contains("payment_history_row_page_" + index)) {
            payment_history_row.style.display = "";
            payment_history_row.classList.remove("none");
        } else {
            payment_history_row.style.display = "none";
        }
    }

    for (let payment_history_page_button of payment_history_page_buttons) {
        payment_history_page_button.classList.remove("selected-page");
    }
    current_button.classList.add("selected-page");

    if (index == payment_history_pages_count_input.value) {
        increase_history_page_button.classList.add("disabled");
    } else {
        increase_history_page_button.classList.remove("disabled");
    }
    if (index == "1") {
        decrease_history_page_button.classList.add("disabled");
    } else {
        decrease_history_page_button.classList.remove("disabled");
    }
}
