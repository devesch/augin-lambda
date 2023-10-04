"use strict";

import "../style/style.scss";
import {
    ProjectData
} from './classes/ProjectData.js';
import {
    apiCaller,
    request
} from "./api.js";





export async function showSelectedPaymentPage(index) {
    let decrease_history_page_button = document.getElementById("decrease_history_page_button");
    let increase_history_page_button = document.getElementById("increase_history_page_button");
    let payment_history_pages_count_input = document.getElementById("payment_history_pages_count_input");


    let current_button = document.getElementById("payment_history_page_button_" + index);
    let payment_history_rows = document.getElementById("payment_history_rows");
    let payment_history_current_page_input = document.getElementById("payment_history_current_page_input");
    let payment_history_page_buttons = document.querySelectorAll('[id^="payment_history_page_button_"]');
    payment_history_current_page_input.value = index;

    let pagination_queries_response = await apiCaller("pagination_queries", {
        "query": "query_paginated_user_orders",
        "page": index
    })

    payment_history_rows.innerHTML = pagination_queries_response["success"];

    for (let payment_history_page_button of payment_history_page_buttons) {
        payment_history_page_button.classList.remove("selected-page")
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



export async function processStripeSubscriptionPayment(stripe_token, payment_type, plan_id, plan_recurrency) {
    const stripe = Stripe(stripe_token);
    console.log("const stripe ", stripe);
    let continue_button = document.getElementById("submit");
    let box_payment_loader = document.getElementById("box_payment_loader");
    let elements = '';
    let emailAddress = '';
    let orderId = '';
    initialize()
    console.log("running initialize");
    checkStatus(orderId);
    console.log("running checkStatus");
    document.querySelector("#payment-form").addEventListener("submit", handleSubmit);

    async function initialize() {
        let checkout_stripe_generate_payload = await apiCaller("checkout_stripe_generate_payload", {
            "plan_id": plan_id,
            "plan_recurrency": plan_recurrency,
            "payment_type": payment_type
        });
        const clientSecret = checkout_stripe_generate_payload["success"]["client_secret"]
        orderId = checkout_stripe_generate_payload["success"]["order_id"]
        console.log("clientSecret ", clientSecret)
        console.log("orderId ", orderId)
        const appearance = {
            theme: 'stripe',
        };
        elements = stripe.elements({
            appearance,
            clientSecret
        });
        const linkAuthenticationElement = elements.create("linkAuthentication");
        linkAuthenticationElement.mount("#link-authentication-element");
        linkAuthenticationElement.on('change', (event) => {
            emailAddress = event.value.email;
        });
        const paymentElementOptions = {
            layout: "tabs",
        };
        const paymentElement = elements.create("payment", paymentElementOptions);
        paymentElement.mount("#payment-element");
        await sleep(200);
        box_payment_loader.style.display = "none";
        continue_button.style.display = "";
    }
    async function handleSubmit(e) {
        e.preventDefault();
        setLoading(true);
        const {
            error
        } = await stripe.confirmPayment({
            elements,
            confirmParams: {
                return_url: ProjectData.props.domainNameUrlVal + "/checkout_payment_success/?order_id=" + orderId,
                receipt_email: emailAddress,
            },
        });
        if (error.type === "card_error" || error.type === "validation_error") {
            showMessage(error.message);
        } else {
            showMessage("An unexpected error occurred.");
        }
        setLoading(false);
    }
    async function checkStatus() {
        const clientSecret = new URLSearchParams(window.location.search).get(
            "payment_intent_client_secret"
        );
        if (!clientSecret) {
            return;
        }
        const {
            paymentIntent
        } = await stripe.retrievePaymentIntent(clientSecret);
        switch (paymentIntent.status) {
            case "succeeded":
                showMessage("Payment succeeded!");
                break;
            case "processing":
                showMessage("Your payment is processing.");
                break;
            case "requires_payment_method":
                showMessage("Your payment was not successful, please try again.");
                break;
            default:
                showMessage("Something went wrong.");
                break;
        }
    }

    function showMessage(messageText) {
        const messageContainer = document.querySelector("#payment-message");
        messageContainer.classList.remove("hidden");
        messageContainer.textContent = messageText;
        setTimeout(function () {
            messageContainer.classList.add("hidden");
            messageText.textContent = "";
        }, 4000);
    }

    function setLoading(isLoading) {
        if (isLoading) {
            document.querySelector("#submit").disabled = true;
            document.querySelector("#spinner").classList.remove("hidden");
            document.querySelector("#button-text").classList.add("hidden");
        } else {
            document.querySelector("#submit").disabled = false;
            document.querySelector("#spinner").classList.add("hidden");
            document.querySelector("#button-text").classList.remove("hidden");
        }
    }
}


export async function checkIfUserCanUpgradePlan(plan_id, recurrency, trial = false) {
    let user_selected_plan_id_input = document.getElementById("user_selected_plan_id_input");
    let user_selected_plan_recurrency_input = document.getElementById("user_selected_plan_recurrency_input");
    let user_selected_plan_is_trial_input = document.getElementById("user_selected_plan_is_trial_input");

    user_selected_plan_id_input.value = plan_id
    user_selected_plan_recurrency_input.value = recurrency
    user_selected_plan_is_trial_input.value = trial

    let update_user_response = await apiCaller("update_user", {
        "command": "check_if_user_can_upgrade_his_plan",
        "plan_id": plan_id
    })

    if ("error" in update_user_response) {
        showCheckoutPanelUserDataForm(update_user_response["user_client_type"]);
    } else {
        if (user_selected_plan_is_trial_input.value == "true") {
            window.location.replace(ProjectData.props.domainNameUrlVal + "/checkout_stripe_subscription/?plan_id=" + user_selected_plan_id_input.value + "&plan_recurrency=" + user_selected_plan_recurrency_input.value + "&plan_trial=True")
        } else {
            window.location.replace(ProjectData.props.domainNameUrlVal + "/checkout_stripe_subscription/?plan_id=" + user_selected_plan_id_input.value + "&plan_recurrency=" + user_selected_plan_recurrency_input.value)
        }
    }
}

export async function showCheckoutPanelUserDataForm(userClientType) {
    let user_country = "";
    if (document.getElementById("user_country")) {
        user_country = document.getElementById("user_country").value;
    }
    let panel_user_data_form_div = document.getElementById("panel_user_data_form_div");
    let panel_user_data_page_response = await request(ProjectData.props.domainNameUrlVal + "/panel_user_data/?error_msg=É necessário atualizar os seus dados para processeguir na compra&render_props=False&user_client_type=" + userClientType + "&selected_country=" + user_country, "GET", {
        "Content-Type": "text/html; charset=utf-8",
    }, {}, false);
    panel_user_data_form_div.innerHTML = panel_user_data_page_response;
    openModal('#panel_user_data_modal');
    // await floatingLabel("#panel_user_data_form_div form"); TODO FIX LABELS POSITIONS IF SOME FIELD ALREADY HAS INFO
}

export async function checkout_check_if_order_is_paid(order_id) {
    let checkout_check_if_order_is_paid_response = await apiCaller("checkout_check_if_order_is_paid", {
        "order_id": order_id
    });
    if ("success" in checkout_check_if_order_is_paid_response) {
        return true;
    }
}

export async function userRegisterGenerateCountryInput() {
    let user_country_select = document.getElementById("user_country");
    console.log("user_country_select ", user_country_select);
    let user_phone_div = document.getElementById("user_phone_div");
    console.log("user_phone_div ", user_phone_div);
    let user_country_phone_response = await apiCaller("user_register_country_phone", {
        "selected_country": user_country_select.value
    })
    user_phone_div.innerHTML = user_country_phone_response.success;
}

export async function panelUserDataChangeCountryForm(user_client_type) {
    console.log("Running panelUserDataChangeCountryForm");
    let user_country_select = document.getElementById("user_country");
    console.log("user_country_select ", user_country_select);
    let panel_user_data_change_country_response = await apiCaller("panel_user_data_change_country", {
        "selected_country": user_country_select.value,
        "user_client_type": user_client_type
    });
    if ("success" in panel_user_data_change_country_response) {
        if (window.location.href.includes(ProjectData.props.domainNameUrlVal + "/panel_user_data")) {
            window.location.href = panel_user_data_change_country_response["success"];
        }
        if (window.location.href.includes(ProjectData.props.domainNameUrlVal + "/checkout_upgrade_your_plan")) {
            if (panel_user_data_change_country_response["success"].includes("physical")) {
                showCheckoutPanelUserDataForm("physical")
            }
            if (panel_user_data_change_country_response["success"].includes("international")) {
                showCheckoutPanelUserDataForm("international")
            }
        }
    };
    if ("error" in panel_user_data_change_country_response) {
        userRegisterGenerateCountryInput();
    };
}

export async function postCheckoutPanelUserDataForm(userClientType) {
    console.log("Running postCheckoutPanelUserDataForm");
    console.log("userClientType ", userClientType)
    let panel_user_data_form_div = document.getElementById("panel_user_data_form_div");

    let user_email = document.getElementById("user_email").value
    console.log("user_email ", user_email)
    let user_name = document.getElementById("user_name").value
    console.log("user_name ", user_name)
    let user_phone = document.getElementById("user_phone").value
    console.log("user_phone ", user_phone)
    let user_cpf = document.getElementById("user_cpf").value
    console.log("user_cpf ", user_cpf)
    let user_cnpj = document.getElementById("user_cnpj").value
    console.log("user_cnpj ", user_cnpj)
    let user_country = document.getElementById("user_country").value
    console.log("user_country ", user_country)
    let user_zip_code = document.getElementById("user_zip_code").value
    console.log("user_zip_code ", user_zip_code)
    let user_state = document.getElementById("user_state").value
    console.log("user_state ", user_state)
    let user_city = document.getElementById("user_city").value
    console.log("user_city ", user_city)
    let user_city_code = document.getElementById("user_city_code").value
    console.log("user_city_code ", user_city_code)
    let user_neighborhood = document.getElementById("user_neighborhood").value
    console.log("user_neighborhood ", user_neighborhood)
    let user_street = document.getElementById("user_street").value
    console.log("user_street ", user_street)
    let user_street_number = document.getElementById("user_street_number").value
    console.log("user_street_number ", user_street_number)
    let user_complement = document.getElementById("user_complement").value
    console.log("user_complement ", user_complement)
    sleep(5000)
    let panel_user_data_page_response = await request(ProjectData.props.domainNameUrlVal + "/panel_user_data/?render_props=False&user_client_type=" + userClientType, "POST", {
        "Content-Type": "application/x-www-form-urlencoded",
    }, {
        "user_email": user_email,
        "user_name": user_name,
        "user_phone": user_phone,
        "user_cpf": user_cpf,
        "user_cnpj": user_cnpj,
        "user_country": user_country,
        "user_zip_code": user_zip_code,
        "user_state": user_state,
        "user_city": user_city,
        "user_city_code": user_city_code,
        "user_neighborhood": user_neighborhood,
        "user_street": user_street,
        "user_street_number": user_street_number,
        "user_complement": user_complement
    }, false);
    console.log("panel_user_data_page_response ", panel_user_data_page_response);
    panel_user_data_form_div.innerHTML = panel_user_data_page_response;
    if (panel_user_data_page_response.toLowerCase().includes("suc") && panel_user_data_page_response.includes("ess")) {
        let user_selected_plan_id_input = document.getElementById("user_selected_plan_id_input")
        let user_selected_plan_recurrency_input = document.getElementById("user_selected_plan_recurrency_input");
        let user_selected_plan_is_trial_input = document.getElementById("user_selected_plan_is_trial_input");
        if (user_selected_plan_is_trial_input.value == "true") {
            window.location.replace(ProjectData.props.domainNameUrlVal + "/checkout_stripe_subscription/?plan_id=" + user_selected_plan_id_input.value + "&plan_recurrency=" + user_selected_plan_recurrency_input.value + "&plan_trial=True")
        } else {
            window.location.replace(ProjectData.props.domainNameUrlVal + "/checkout_stripe_subscription/?plan_id=" + user_selected_plan_id_input.value + "&plan_recurrency=" + user_selected_plan_recurrency_input.value)
        }
    }
}


export async function openCookiesContainer() {
    document.querySelector(".footer-cookies").classList.add("active");
}


export async function openCookiesConfiguration() {
    document.querySelector(".footer-cookies-container").classList.remove("open");
    document.querySelector(".footer-cookies-configuration-container").classList.add("open");
}

export async function showUserPhysicalAddressData() {
    console.log("Running showUserPhysicalAddressData")
    let error_msg = document.getElementById("error_msg");
    let user_zip_code = document.getElementById("user_zip_code");
    let user_state = document.getElementById("user_state");
    let user_city = document.getElementById("user_city");
    let user_city_code = document.getElementById("user_city_code");
    let user_neighborhood = document.getElementById("user_neighborhood");
    let user_street = document.getElementById("user_street");
    let box_inputs = document.querySelector(".page-user__box-user-data__box-inputs__box-adress");
    await maskToZipCode(user_zip_code)

    if (user_zip_code.value.length == 9) {
        openModal('.modal.modal-loader-spinner')
        let api_response = await apiCaller("panel_get_address_data_with_zip", {
            'user_zip_code': user_zip_code.value.replace(".", "").replace("-", "")
        });
        console.log("api_response " + api_response)
        closeModal('.modal.modal-loader-spinner')
        if ("success" in api_response) {
            user_state.value = api_response.success.state
            user_city.value = api_response.success.city
            user_city_code.value = api_response.success.city_code
            user_neighborhood.value = api_response.success.neighborhood
            user_street.value = api_response.success.street
            box_inputs.style = ""
            error_msg.innerHTML = ""
            error_msg.style = "display: none;"
            return
        }
        if ("error" in api_response) {
            error_msg.innerHTML = api_response.error
            error_msg.style = "color:#FF0000;"
            return
        }
    }
    user_state.value = ""
    user_city.value = ""
    user_city_code.value = ""
    user_neighborhood.value = ""
    user_street.value = ""
    user_street_number.value = ""
    user_complement.value = ""
    box_inputs.style = "display: none;"
}


export async function showUserCompanyAddressData() {
    console.log("Running showUserCompanyAddressData")
    let error_msg = document.getElementById("error_msg");
    let user_cnpj = document.getElementById("user_cnpj");
    let user_name = document.getElementById("user_name");
    let user_zip_code = document.getElementById("user_zip_code");
    let user_state = document.getElementById("user_state");
    let user_city = document.getElementById("user_city");
    let user_city_code = document.getElementById("user_city_code");
    let user_neighborhood = document.getElementById("user_neighborhood");
    let user_street = document.getElementById("user_street");
    let user_street_number = document.getElementById("user_street_number");
    let user_complement = document.getElementById("user_complement");

    await maskToCNPJ(user_cnpj)
    let box_inputs = document.querySelector(".page-user__box-user-data__box-inputs__box-adress");
    if (user_cnpj.value.length == 18) {
        openModal('.modal.modal-loader-spinner')
        let api_response = await apiCaller("panel_get_company_data_with_cnpj", {
            'user_cnpj': user_cnpj.value.replace(".", "").replace(".", "").replace("-", "").replace("/", "")
        });
        closeModal('.modal.modal-loader-spinner')
        if ("success" in api_response) {
            user_name.value = api_response.success.name
            user_zip_code.value = api_response.success.zip_code
            user_state.value = api_response.success.state
            user_city.value = api_response.success.city
            user_city_code.value = api_response.success.city_code
            user_neighborhood.value = api_response.success.neighborhood
            user_street.value = api_response.success.street
            user_street_number.value = api_response.success.street_number
            if ("complement" in api_response.success) {
                user_complement.value = api_response.success.complement
            }
            box_inputs.style = ""
            error_msg.innerHTML = ""
            error_msg.style = "display: none;"
            return
        }
        if ("error" in api_response) {
            error_msg.innerHTML = api_response.error
            error_msg.style = "color:#FF0000;"
            return
        }
    }
    user_name.value = ""
    user_zip_code.value = ""
    user_state.value = ""
    user_city.value = ""
    user_city_code.value = ""
    user_neighborhood.value = ""
    user_street.value = ""
    user_street_number.value = ""
    user_complement.value = ""
    box_inputs.style = "display: none;"
}

export function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

export function maskToNumber(input) {
    input.value = input.value.replace(/\D/g, "");
}

export function maskToLetter(input) {
    input.value = input.value.replace(/[0-9]/g, '');;
}

export async function maskToZipCode(input) {
    input.value = input.value.replace(/\D/g, "");
    input.value = input.value.replace(/^(\d{5})(\d)/, "$1-$2");
}

export function maskToCPF(input) {
    input.value = input.value.replace(/\D/g, "");
    input.value = input.value.replace(/(\d{3})(\d)/, "$1.$2");
    input.value = input.value.replace(/(\d{3})(\d)/, "$1.$2");
    input.value = input.value.replace(/(\d{3})(\d{1,2})$/, "$1-$2");
}
export function maskToCNPJ(input) {
    input.value = input.value.replace(/\D/g, "");
    input.value = input.value.replace(/(\d{2})(\d)/, "$1.$2");
    input.value = input.value.replace(/(\d{3})(\d)/, "$1.$2");
    input.value = input.value.replace(/(\d{3})(\d)/, "$1/$2");
    input.value = input.value.replace(/(\d{4})(\d)/, "$1-$2");
}

export function maskToPhone(input) {
    input.value = input.value.replace(/\D/g, "");
    input.value = input.value.replace(/^(\d{2})(\d)/g, "($1) $2");
    input.value = input.value.replace(/(\d)(\d{4})$/, "$1-$2");
}


export async function toogleDiv(checkbox_input, div_id) {
    var div = document.getElementById(div_id);
    if (checkbox_input.checked) {
        div.style.display = "";
    } else {
        div.style.display = "none";
    }
}

export async function formatToPercentage(input) {
    input.value = input.value.replace(/\D/g, "");
    if (input.value < 1) {
        input.value = '';
    } else if (input.value > 99) {
        input.value = '99';
    }
}


export async function formatToMoney(input) {
    input.value = input.value.replace(/\D/g, "");
    if (input.value.length > 2) {
        input.value = input.value.replace(/^0+/, "");
    }
    input.value = input.value.padStart(3, '0');
    input.value = input.value.replace(/(\d{2})$/, ',$1');
    let length = input.value.length;
    if (length > 6 && length <= 9) {
        input.value = input.value.replace(/(\d{1,3})(\d{3},\d{2})$/, '$1.$2');
    }
    if (length > 9) {
        input.value = input.value.replace(/(\d{1,3})(\d{3})(\d{3},\d{2})$/, '$1.$2.$3');
    }
}

export async function formatToNumbers(input) {
    input.value = input.value.replace(/\D/g, '');
    input.value = input.value.replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1.');
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
    let models_in_process_ul = document.getElementById("models_in_process_ul");
    let models_in_processing_section = document.getElementById("models_in_processing_section");
    let amount_of_models_in_processing_before_update = models_in_process_ul.getElementsByTagName("li").length;

    let panel_explore_projects_models_in_processing_html_response = await apiCaller("panel_explore_projects_models_in_processing_html", {});
    models_in_process_ul.innerHTML = panel_explore_projects_models_in_processing_html_response["success"];

    if (panel_explore_projects_models_in_processing_html_response["success"]) {
        models_in_processing_section.style.display = "";
    } else {
        models_in_processing_section.style.display = "none";
    }

    let amount_of_models_in_processing_after_update = models_in_process_ul.getElementsByTagName("li").length;
    if (amount_of_models_in_processing_before_update != amount_of_models_in_processing_after_update) {
        await showUserDicts();
    }
}

const uploadedFilesNames = [];
export async function uploadModel(input) {
    // if (uploadedFilesNames.length == 0) {
    //     let federated_name_div = document.getElementById("federated_name_div");
    //     let federated_name_input = document.getElementById("federated_name_input");
    //     let create_federated_project_with_processed_files_checkbox = document.getElementById("create_federated_project_with_processed_files");

    //     create_federated_project_with_processed_files_checkbox.checked = false;
    //     federated_name_div.style.display = "none";
    //     federated_name_input.removeAttribute('required', '');
    // }

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
            "original_name": file["name"],
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

    var panel_create_project_check_file_response = await apiCaller("panel_create_project_check_file", {
        "key": post_data["key"],
        "original_name": post_data["original_name"]
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
        model_id.value = panel_create_project_check_file_response["success"]["models_ids"];
        has_more_than_one_file.value = panel_create_project_check_file_response["success"]["has_more_than_one_file"];

        let has_fbx = document.getElementById("has_fbx_" + post_data["element_index"]);
        if (panel_create_project_check_file_response["success"]["has_fbx"]) {
            has_fbx.value = "True";
        } else {
            has_fbx.value = "False";
        }

        let message = document.getElementById("message_" + post_data["element_index"]);
        message.innerHTML = panel_create_project_check_file_response["success"]["message"] + " " + panel_create_project_check_file_response["success"]["model_already_exists_name"];
        let has_error = document.getElementById("has_error_" + post_data["element_index"]);
        has_error.value = "False";
        let file_formats_div = document.getElementById("file_formats_div_" + post_data["element_index"]);
        file_formats_div.innerHTML = panel_create_project_check_file_response["success"]["file_formats_html"]

        checkIfCreateProjectSubmitButtonIsAvailable();
        checkIfCreateProjectIsFederated(false);
    }
}







export function checkIfCreateProjectIsFederated(checkbox = true) {
    let federated_switch_div = document.getElementById("federated_switch_div");
    let federated_name_div = document.getElementById("federated_name_div");
    let federated_name_input = document.getElementById("federated_name_input");
    let create_federated_project_with_processed_files_checkbox = document.getElementById("create_federated_project_with_processed_files");
    let uploading_element_has_more_than_one_file = document.querySelectorAll('[id^="has_more_than_one_file_"]');
    let has_fbxs = document.querySelectorAll('[id^="has_fbx_"]');
    let uploading_element_message = document.querySelectorAll(".uploading_element_message");
    let federated_tooltip_div = federated_switch_div.querySelector(".tooltip-content--click");

    federated_tooltip_div.classList.remove("block");
    let tooltip_timer = "";

    for (let has_fbx of has_fbxs) {
        console.log("has_fbx.value", has_fbx.value);
        if (has_fbx.value === "True") {
            create_federated_project_with_processed_files_checkbox.checked = false;
            if (checkbox) {
                console.log("TODO SHOW TOOLTIP ERROR MSG");
                clearTimeout(tooltip_timer);
                federated_tooltip_div.classList.add("block");
                tooltip_timer = setTimeout(function () {
                    federated_tooltip_div.classList.remove("block");
                }, 5000);
            }
        }
    }

    if (uploadedFilesNames.length === 0) {
        create_federated_project_with_processed_files_checkbox.checked = false;
        if (checkbox) {
            console.log("TODO SHOW TOOLTIP ERROR MSG");
            clearTimeout(tooltip_timer);
            federated_tooltip_div.classList.add("block");
            tooltip_timer = setTimeout(function () {
                federated_tooltip_div.classList.remove("block");
            }, 5000);
        }
    }

    if (uploading_element_message.length === 1) {
        for (let has_more_than_one_file_input of uploading_element_has_more_than_one_file) {
            console.log("has_more_than_one_file_input.value", has_more_than_one_file_input.value);
            if (has_more_than_one_file_input.value != "true") {
                create_federated_project_with_processed_files_checkbox.checked = false;
                if (checkbox) {
                    console.log("TODO SHOW TOOLTIP ERROR MSG");
                    clearTimeout(tooltip_timer);
                    federated_tooltip_div.classList.add("block");
                    tooltip_timer = setTimeout(function () {
                        federated_tooltip_div.classList.remove("block");
                    }, 5000);
                }
            }
        }
    }

    if (create_federated_project_with_processed_files_checkbox.checked) {
        federated_name_div.style.display = "";
        federated_name_input.required = true;
    } else {
        federated_name_div.style.display = "none";
        federated_name_input.required = false;
    }
}

export async function checkIfCreateProjectSubmitButtonIsAvailable(is_submitable = true) {
    let submit_form_button = document.getElementById("submit_form_button");
    let has_errors = document.querySelectorAll('[id^="has_error_"]');
    let create_project_error_span = document.getElementById('create_project_error_span');

    for (let has_error of has_errors) {
        console.log(has_error)
        if (has_error.value === "True") {
            submit_form_button.setAttribute("disabled", "disabled");

            let translate_response = await apiCaller("translate", {
                "key": "Um ou mais de seus arquivos possui um erro, por favor exclua os arquivos com erro para realizar o processamento"
            });
            create_project_error_span.innerHTML = translate_response["success"];
            create_project_error_span.style.display = "";
            return
        }
    }

    if (is_submitable) {
        if (has_errors.length > 0) {
            submit_form_button.removeAttribute("disabled");
            create_project_error_span.innerHTML = "";
            create_project_error_span.style.display = "none";
            return
        }
    }
    submit_form_button.setAttribute("disabled", "disabled");
}

export async function deleteUploadingElement(index) {
    let model_filename_input = document.getElementById("model_filename_" + index);
    let model_id_input = document.getElementById("model_id_" + index);
    if (uploadedFilesNames.includes(model_filename_input.value)) {
        let filename_index_in_list = uploadedFilesNames.indexOf(model_filename_input.value);
        uploadedFilesNames.splice(filename_index_in_list, 1);
        console.log("uploadedFilesNames", uploadedFilesNames);
    }
    let uploading_element = document.getElementById("uploading_element_" + index);
    uploading_element.remove();
    checkIfCreateProjectSubmitButtonIsAvailable();
    checkIfCreateProjectIsFederated(false)

    let update_model_response = await apiCaller("update_model", {
        "command": "delete_model",
        "model_id": model_id_input.value
    });
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
            checkUploadModelFile(post_data);
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

const uploadWithoutProgressBar = (url, post_data) =>
    new Promise((resolve, reject) => {
        let xhr = new XMLHttpRequest();
        let current_progress;
        xhr.upload.addEventListener('progress', (e) => {
            current_progress = Math.round((e.loaded / e.total) * 100);
            console.log(current_progress);
        });
        xhr.addEventListener('load', () => {
            resolve({
                status: xhr.status,
                body: xhr.responseText
            });
        });
        xhr.addEventListener('error', () => {
            reject(new Error('File upload failed'))
        });
        xhr.addEventListener('abort', () => {
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
            if (!exploreCreateButton) {
                return;
            };

            if (!exploreCreateButton.getAttribute("aria-controls")) {
                return;
            };

            let currentMenu = document.getElementById(exploreCreateButton.getAttribute("aria-controls"));
            if (currentMenu) {
                activateExploreCreateMenu(event.target, exploreCreateButton, currentMenu);
            }

        }

    });
}


export async function togglePasswordVisibility(button) {
    let image = button.querySelector("img");
    let input = document.getElementById(button.getAttribute("aria-controls"));
    if (image.src.includes("visibility_off")) {
        image.src = image.src.replace("visibility_off", "visibility");
        input.setAttribute("type", "text");

        let translate_response = await apiCaller("translate", {
            key: "Ocultar senha"
        })

        button.setAttribute("aria-label", translate_response["success"]);
        button.setAttribute("title", translate_response["success"]);
    } else {
        image.src = image.src.replace("visibility", "visibility_off");
        input.setAttribute("type", "password");

        let translate_response = await apiCaller("translate", {
            key: "Exibir senha"
        })

        button.setAttribute("aria-label", translate_response["success"]);
        button.setAttribute("title", translate_response["success"]);
    }
}


export function hideHtmlElement(element) {
    element.classList.add("none");
    element.setAttribute("aria-hidden", "true");
    element.setAttribute("hidden", "hidden");
}


export function showHtmlElement(element) {
    element.classList.remove("none");
    element.setAttribute("aria-hidden", "false");
    element.removeAttribute("hidden");
}

export function showPlansThumbs(recurrency) {
    let monthly_subscription_container = document.getElementById("monthly_subscription_container");
    let yearly_subscription_container = document.getElementById("yearly_subscription_container");
    let monthly_augin_plan_input = document.getElementById("monthly_augin_plan_input");
    let yearly_augin_plan_input = document.getElementById("yearly_augin_plan_input");
    if (recurrency == "monthly") {
        monthly_augin_plan_input.checked = true;
        yearly_augin_plan_input.checked = false;
        monthly_subscription_container.style.display = ""
        yearly_subscription_container.style.display = "none"
    }
    if (recurrency == "annually") {
        monthly_augin_plan_input.checked = false;
        yearly_augin_plan_input.checked = true;
        monthly_subscription_container.style.display = "none"
        yearly_subscription_container.style.display = ""
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

        if (notDraggingItems.length > 0) {
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

export async function openModalShareProject(model_id, model_name, model_visualization_count, model_share_link, model_share_link_qrcode, model_is_password_protected, model_password, model_is_acessible) {
    let share_project_name_span = document.getElementById("share_project_name_span");
    let copy_project_share_link_button = document.getElementById("copy_project_share_link_button");
    let update_model_id_input = document.getElementById("update_model_id_input");
    let copy_project_share_link_input = document.getElementById("copy_project_share_link_input");
    let project_share_link_qrcode_img = document.getElementById("project_share_link_qrcode_img");
    let project_is_password_protected_input = document.getElementById("project_is_password_protected_input");
    let project_password_div = document.getElementById("project_password_div");
    let project_password_input = document.getElementById("project_password_input");
    let model_visualization_count_span = document.getElementById("model_visualization_count_span");
    let project_password_error_span = document.getElementById("project_password_error_span");
    let project_is_accessible_input = document.getElementById("project_is_accessible_input");

    if (model_is_acessible == "True") {
        project_is_accessible_input.checked = "checked";
    } else {
        project_is_accessible_input.checked = "";
    }


    if (model_is_password_protected == "True") {
        project_is_password_protected_input.checked = "checked";
        project_password_div.style.display = "block";
        project_password_div.classList.add("open");
    } else {
        project_is_password_protected_input.checked = "";
        project_password_div.style.display = "none";
        project_password_div.classList.remove("open");
    }

    project_password_error_span.innerHTML = "";
    model_visualization_count_span.innerHTML = model_visualization_count;
    project_password_input.value = model_password;
    update_model_id_input.value = model_id;
    share_project_name_span.innerText = model_name;
    copy_project_share_link_button.value = model_share_link;
    copy_project_share_link_input.value = model_share_link;
    project_share_link_qrcode_img.src = model_share_link_qrcode;
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

export async function FavoriteProject(model_id, model_is_favorite) {
    let update_user_response = await apiCaller("update_user", {
        "command": "add_model_to_user_favorites",
        "model_id": model_id,
        "model_is_favorite": model_is_favorite
    });
    await showUserDicts();
}


export async function showUserDicts() {
    var user_folder_rows_tbody = document.getElementById("user_folder_rows_tbody");
    var sort_attribute_input = document.getElementById("sort_attribute_input");
    var sort_reverse_input = document.getElementById("sort_reverse_input");
    var folder_path_span = document.getElementById("folder_path_span");
    var folder_path_input = document.getElementById("folder_path_input");

    var folder_id_input = document.getElementById("folder_id_input");
    var explore_filter = document.getElementById("explore_filter");
    var explore_input_search = document.getElementById("explore_input_search");

    var user_dicts_return_to_root_span = document.getElementById("user_dicts_return_to_root_span");

    let match = location.href.match(/\/([^\/]+)\/?(\?|$)/);
    let page = match ? match[1] : null;

    let panel_explore_project_user_dicts_html_response = await apiCaller("panel_explore_project_user_dicts_html", {
        "sort_attribute": sort_attribute_input.value,
        "sort_reverse": sort_reverse_input.value,
        "folder_id": folder_id_input.value,
        "explore_filter": explore_filter.value,
        "explore_input_search": explore_input_search.value,
        "page": page
    });

    user_folder_rows_tbody.innerHTML = panel_explore_project_user_dicts_html_response["success"];
    folder_path_span.innerHTML = folder_path_input.value;

    if (location.href.includes("view_folder")) {
        var shared_folder_id_input = document.getElementById("shared_folder_id_input");
        if (shared_folder_id_input.value == folder_id_input.value) {
            user_dicts_return_to_root_span.style.display = "none";
            return
        }
    }

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
    await showUserDicts()
    closeModal('.modal.rename-modal');
}

export async function updateModelPassword() {
    var model_id = document.getElementById("update_model_id_input");
    var project_is_password_protected_input = document.getElementById("project_is_password_protected_input");
    var project_password_input = document.getElementById("project_password_input");
    var project_is_accessible_input = document.getElementById("project_is_accessible_input");
    var project_password_error_span = document.getElementById("project_password_error_span");

    let update_model_response = await apiCaller("update_model", {
        "command": "update_password",
        "model_id": model_id.value,
        "model_password": project_password_input.value,
        "model_is_password_protected": project_is_password_protected_input.checked,
        "model_is_accessible": project_is_accessible_input.checked
    });

    if ("error" in update_model_response) {
        project_password_error_span.innerHTML = update_model_response["error"]
        return
    }
    await showUserDicts()
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
    await showUserDicts();
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

    await showUserDicts();
    closeModal(".modal.select-category-modal");
}



document.addEventListener("DOMContentLoaded", function (event) {
    detectClickOutsideElement();
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
        "model_html": "update",
        "model_id_to_be_updated": model_id
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


// export async function openModalDeleteProject(model_id) {
//     openModal(".modal.delete-file-modal");
// }


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
        await showUserDicts();
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
        await showUserDicts();
        closeModal(".modal.create-folder-modal");
    }
}

export async function openFolder(folder_id, folder_path, return_folder_path = false) {
    var folder_id_input = document.getElementById("folder_id_input");
    var folder_path_input = document.getElementById("folder_path_input");
    folder_id_input.value = folder_id;

    if (!return_folder_path) {
        if (folder_path) {
            folder_path_input.value = folder_path;
        } else {
            folder_path_input.value = ""
        }
    } else {
        folder_path_input.value = folder_path_input.value.split(folder_path)[0];
        folder_path_input.value += folder_path;
    }
    await showUserDicts();
}


export async function openReturnFolder() {
    var folder_id_input = document.getElementById("folder_id_input");
    var update_user_response = await apiCaller("update_user", {
        "command": "get_root_folder",
        "folder_id": folder_id_input.value
    });
    if (update_user_response["success"]["folder_path"] != "") {
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


export async function openModalRenameFolder(folder_id, folder_name) {
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
        closeModal(".modal.rename-folder-modal");
        folder_rename_input.value = "";
        await showUserDicts();
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
        delete_folder_error_span.innerHTML = "";
        delete_folder_name_span.innerHTML = "";
        await showUserDicts();
        closeModal('.modal.delete-folder-modal')
    }
}

export async function FavoriteFolder(folder_id, folder_is_favorite) {
    let update_user = await apiCaller("update_user", {
        "command": "add_folder_to_user_favorites",
        "folder_id": folder_id,
        "folder_is_favorite": folder_is_favorite
    });
    await showUserDicts();
}


export async function refreshUpdateModal(folder_id) {
    var model_id_update_model_input = document.getElementById("model_id_update_model_input");
    var update_modal_folder_id = document.getElementById("update_modal_folder_id");
    var update_model_user_folder_rows_tbody = document.getElementById("update_model_user_folder_rows_tbody");
    var update_modal_folder_path_span = document.getElementById("update_modal_folder_path_span");
    var update_modal_return_folder_span = document.getElementById("update_modal_return_folder_span");

    var panel_explore_project_user_dicts_html_response = await apiCaller("panel_explore_project_user_dicts_html", {
        "folder_id": folder_id,
        "model_html": "update",
        "model_id_to_be_updated": model_id_update_model_input.value
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
    if (update_user_response["success"]["folder_path"] != "") {
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
    if (update_user_response["success"]["folder_path"] != "") {
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

    await showUserDicts();
    closeModal(".modal.move-folder-modal");
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
    if (update_user_response["success"]["folder_path"] != "") {
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

    await showUserDicts();
    closeModal(".modal.move-modal");
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
    var create_federated_modal_return_folder_span = document.getElementById("create_federated_modal_return_folder_span");
    var panel_explore_project_user_dicts_html_response = await apiCaller("panel_explore_project_user_dicts_html", {
        "model_html": "create_federated"
    })
    federated_required_ids_list = [];
    create_federated_model_user_folder_rows_tbody.innerHTML = panel_explore_project_user_dicts_html_response["success"];
    create_federated_modal_return_folder_span.style.display = "none";
    closeModal(".modal.create-federated-modal");
    openModal(".modal.create-federated-select-models-modal");

    if ("error" in update_model_response) {

    } else {

    }

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
        await showUserDicts();
        closeModal(".modal.create-federated-select-models-modal");
    }
}

export async function openReturnFolderModalCreateFederated() {
    var create_federated_modal_folder_id = document.getElementById("create_federated_modal_folder_id");
    var update_user_response = await apiCaller("update_user", {
        "command": "get_root_folder",
        "folder_id": create_federated_modal_folder_id.value
    });
    if (update_user_response["success"]["folder_path"] != "") {
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

var federated_required_ids_list = [];

export async function addOrRemoveModelFromCreateFederatedList(input) {
    console.log("input.checked", input.checked);

    if (federated_required_ids_list.includes(input.value) && !input.checked) {
        federated_required_ids_list.splice(federated_required_ids_list.indexOf(input.value), 1);
    } else if (!federated_required_ids_list.includes(input.value) && input.checked) {
        federated_required_ids_list.push(input.value);
    }

    console.log("federated_required_ids_list", federated_required_ids_list);
}



export async function openModalAddSharedProject() {
    var shared_asset_password_error_span = document.getElementById("shared_asset_password_error_span");
    shared_asset_password_error_span.innerHTML = "";
    closeModal(".password-shared-project-modal");
    openModal(".add-shared-project-modal");
}

export async function saveAddSharedProject() {
    var shared_asset_link_input = document.getElementById("shared_asset_link_input");
    var add_shared_asset_error_span = document.getElementById("add_shared_asset_error_span");
    var shared_asset_password_input = document.getElementById("shared_asset_password_input");
    shared_asset_password_input.value = "";

    var update_user_response = await apiCaller("update_user", {
        "command": "add_shared",
        "shared_link": shared_asset_link_input.value,
    })


    if ("command" in update_user_response) {
        closeModal(".add-shared-project-modal");
        openModal(".password-shared-project-modal");
    }
    if ("error" in update_user_response) {
        add_shared_asset_error_span.innerHTML = update_user_response["error"];
    }
    if ("success" in update_user_response) {
        await showUserDicts();
        closeModal(".add-shared-project-modal");
    }
}


export async function saveAddPasswordSharedProject() {
    var shared_asset_link_input = document.getElementById("shared_asset_link_input");
    var shared_asset_password_input = document.getElementById("shared_asset_password_input");
    var shared_asset_password_error_span = document.getElementById("shared_asset_password_error_span");

    var update_user_response = await apiCaller("update_user", {
        "command": "add_shared",
        "shared_link": shared_asset_link_input.value,
        "shared_password": shared_asset_password_input.value,
    })

    if ("success" in update_user_response) {
        if (location.href.includes("view_folder") && update_user_response["has_user"] == true) {
            location.href = ProjectData.props.domainNameUrlVal + "/panel_shared_project/?folder_id=" + update_user_response["folder_id"];
            return
        }
        await showUserDicts();
        closeModal(".password-shared-project-modal");
    }
    if ("error" in update_user_response) {
        shared_asset_password_error_span.innerHTML = update_user_response["error"];
    }
}



export async function openModalShareFolder(folder_id, folder_name, folder_visualization_count, folder_share_link, folder_share_link_qrcode, folder_is_password_protected, folder_password, folder_is_acessible) {
    let share_folder_name_span = document.getElementById("share_folder_name_span");
    let copy_folder_share_link_button = document.getElementById("copy_folder_share_link_button");
    let update_folder_id_input = document.getElementById("update_folder_id_input");
    let copy_folder_share_link_input = document.getElementById("copy_folder_share_link_input");
    let folder_share_link_qrcode_img = document.getElementById("folder_share_link_qrcode_img");
    let folder_is_password_protected_input = document.getElementById("folder_is_password_protected_input");
    let folder_password_div = document.getElementById("folder_password_div");
    let folder_password_input = document.getElementById("folder_password_input");
    let folder_visualization_count_span = document.getElementById("folder_visualization_count_span");
    let folder_password_error_span = document.getElementById("folder_password_error_span");
    let folder_is_accessible_input = document.getElementById("folder_is_accessible_input");

    if (folder_is_acessible == "True") {
        folder_is_accessible_input.checked = "checked";
    } else {
        folder_is_accessible_input.checked = "";
    }

    if (folder_is_password_protected == "True") {
        folder_is_password_protected_input.checked = "checked";
        folder_password_div.style.display = "block";
        folder_password_div.classList.add("open");
    } else {
        folder_is_password_protected_input.checked = "";
        folder_password_div.style.display = "none";
        folder_password_div.classList.remove("open");
    }

    folder_password_error_span.innerHTML = "";
    folder_visualization_count_span.innerHTML = folder_visualization_count;
    folder_password_input.value = folder_password;
    update_folder_id_input.value = folder_id;
    share_folder_name_span.innerText = folder_name;
    copy_folder_share_link_button.value = folder_share_link;
    copy_folder_share_link_input.value = folder_share_link;
    folder_share_link_qrcode_img.src = folder_share_link_qrcode;
    openModal('.modal.share-folder-modal');
}
export async function updateFolderPassword() {
    var folder_id_input = document.getElementById("update_folder_id_input");
    var folder_is_password_protected_input = document.getElementById("folder_is_password_protected_input");
    var folder_password_input = document.getElementById("folder_password_input");
    var folder_is_accessible_input = document.getElementById("folder_is_accessible_input");
    var folder_password_error_span = document.getElementById("folder_password_error_span");

    let update_user_response = await apiCaller("update_user", {
        "command": "update_folder_password",
        "folder_id": folder_id_input.value,
        "folder_password": folder_password_input.value,
        "folder_is_password_protected": folder_is_password_protected_input.checked,
        "folder_is_accessible": folder_is_accessible_input.checked
    });

    if ("error" in update_user_response) {
        folder_password_error_span.innerHTML = update_user_response["error"]
        return
    }
    await showUserDicts()
    closeModal('.modal.share-folder-modal');
}



export async function openModalRemoveFolder(folder_id, folder_name) {
    var remove_folder_name_span = document.getElementById("remove_folder_name_span");
    var folder_id_remove_input = document.getElementById("folder_id_remove_input");
    var folder_remove_error_span = document.getElementById("folder_remove_error_span");

    remove_folder_name_span.innerText = folder_name;
    folder_id_remove_input.value = folder_id;
    folder_remove_error_span.innerHTML = "";
    openModal(".modal.remove-folder-modal");
}

export async function removeFolderFromShared() {
    var folder_id_remove_input = document.getElementById("folder_id_remove_input");
    var folder_remove_error_span = document.getElementById("folder_remove_error_span");

    let update_user_response = await apiCaller("update_user", {
        "command": "remove_folder_from_shared",
        "folder_id": folder_id_remove_input.value
    });

    if ("error" in update_user_response) {
        folder_remove_error_span.innerHTML = update_user_response["error"]
    }

    await js.index.showUserDicts();
    closeModal(".modal.remove-folder-modal");
}


export async function openModalRemoveProject(model_id, model_name) {
    var remove_model_name_span = document.getElementById("remove_model_name_span");
    var model_id_remove_input = document.getElementById("model_id_remove_input");
    var model_remove_error_span = document.getElementById("model_remove_error_span");

    remove_model_name_span.innerText = model_name;
    model_id_remove_input.value = model_id;
    model_remove_error_span.innerHTML = "";
    openModal(".modal.remove-modal");
}

export async function removeModelFromShared() {
    var model_id_remove_input = document.getElementById("model_id_remove_input");
    var model_remove_error_span = document.getElementById("model_remove_error_span");

    let update_user_response = await apiCaller("update_user", {
        "command": "remove_model_from_shared",
        "model_id": model_id_remove_input.value
    });

    if ("error" in update_user_response) {
        model_remove_error_span.innerHTML = update_user_response["error"]
    }

    await js.index.showUserDicts();
    closeModal(".modal.remove-modal");
}

export async function openModalCancelSubscription() {
    openModal(".modal.cancel-subscription-modal");
}


export async function saveCancelSubscription() {
    let cancel_subscription_error_span = document.getElementById("cancel_subscription_error_span");

    let update_user_response = await apiCaller("update_user", {
        "command": "cancel_user_current_subscription"
    });

    if ("erro" in update_user_response) {
        cancel_subscription_error_span.innerHTML = update_user_response["error"];
    } else {
        location.reload();
    }
}

export async function openModalAddPaymentMethod() {
    stripe_token_input = document.getElementById("stripe_token_input");

    const stripe = Stripe(stripe_token_input.value);
    const elements = stripe.elements();
    const card = elements.create('card');
    card.mount('#card-element');
    card.addEventListener('change', function (event) {
        const displayError = document.getElementById('card-errors');
        if (event.error) {
            displayError.textContent = event.error.message;
        } else {
            displayError.textContent = '';
        }
    });
    const form = document.getElementById('payment-form');
    form.addEventListener('submit', function (event) {
        event.preventDefault();

        stripe.createPaymentMethod({
            type: 'card',
            card: card
        }).then(function (result) {
            if (result.error) {
                // Inform the user if there was an error.
                const errorElement = document.getElementById('card-errors');
                errorElement.textContent = result.error.message;
            } else {
                // Send the PaymentMethod ID to your server for further processing.
                // For this step, you'd typically make an AJAX call to your backend.
                saveAddPaymentMethod(result.paymentMethod.id);
            }
        });
    });

    openModal(".modal.add-payment-method-modal");
}

export async function saveAddPaymentMethod(new_payment_method_id) {
    let update_user_response = await apiCaller("update_user", {
        "command": "create_payment_method",
        "payment_method_id": new_payment_method_id
    });

    location.reload();
}


export async function updatePaginationProgressBar() {
    let pagination_actual_itens_count_span = document.getElementById("pagination_actual_itens_count_span");
    let pagination_total_itens_count_span = document.getElementById("pagination_total_itens_count_span");
    let progress_bar = document.getElementById("progress_upload_bar_div");
    progress_bar.style = 'width:' + parseInt((parseInt(pagination_actual_itens_count_span.innerHTML) / parseInt(pagination_total_itens_count_span.innerHTML)) * 100) + "%; color:transparent";
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
    let loadingPaginationMessage = document.getElementById("pagination_loading_more_message_p");
    let countPagination = document.getElementById("pagination_itens_count_p");
    countPagination.style.display = "none";
    loadingPaginationMessage.style.display = "block";

    let query_filter_input = document.getElementById("query_filter");
    let query_filter_value = ""
    if (query_filter_input) {
        query_filter_value = query_filter_input.value
    }
    let last_evaluated_key_input = document.getElementById("last_evaluated_key");
    let query_input = document.getElementById("query");
    let pagination_queries_response = await apiCaller("pagination_queries", {
        "query": query_input.value,
        "last_evaluated_key": last_evaluated_key_input.value,
        "query_filter": query_filter_value
    });

    if ("error" in pagination_queries_response) {
        return
    }
    let pagination_component = document.getElementById("pagination_component");
    pagination_component.innerHTML += pagination_queries_response["success"];
    let pagination_actual_itens_count_span = document.getElementById("pagination_actual_itens_count_span");
    let pagination_total_itens_count_span = document.getElementById("pagination_total_itens_count_span");
    let showing_total_count_input = document.getElementById("showing_total_count");
    let progress_bar = document.getElementById("progress_upload_bar_div");

    console.log("updating last_evaluated_key with ", pagination_queries_response["last_evaluated_key"]);
    last_evaluated_key_input.value = JSON.stringify(pagination_queries_response["last_evaluated_key"]);
    pagination_actual_itens_count_span.innerHTML = parseInt(pagination_actual_itens_count_span.innerHTML) + parseInt(pagination_queries_response["new_itens_count"])
    progress_bar.style = 'width:' + parseInt((parseInt(pagination_actual_itens_count_span.innerHTML) / parseInt(pagination_total_itens_count_span.innerHTML)) * 100) + "%; color:transparent";
    showing_total_count_input.value = pagination_actual_itens_count_span.innerHTML;

    if (parseInt(pagination_actual_itens_count_span.innerHTML) == parseInt(pagination_total_itens_count_span.innerHTML)) {
        let load_more_pagination_button = document.getElementById("load_more_pagination_button");
        load_more_pagination_button.style.display = "none";
    }

    countPagination.style.display = "block";
    loadingPaginationMessage.style.display = "none";

}


export async function updateBackofficeOrders() {
    let search_orders_by_user_input = document.getElementById("search_orders_by_user_input");
    let search_orders_by_status_select = document.getElementById("search_orders_by_status_select");
    let pagination_component = document.getElementById("pagination_component");

    let last_evaluated_key = document.getElementById("last_evaluated_key");
    let query = document.getElementById("query");
    let query_filter = document.getElementById("query_filter");
    let showing_total_count = document.getElementById("showing_total_count");

    let backoffice_orders_html_response = await apiCaller("backoffice_orders_html", {
        "search_user": search_orders_by_user_input.value,
        "search_order_status": search_orders_by_status_select.value
    });

    pagination_component.innerHTML = backoffice_orders_html_response["success"];
    last_evaluated_key.value = backoffice_orders_html_response["last_evaluated_key"];
    query.value = backoffice_orders_html_response["query"];
    query_filter.value = backoffice_orders_html_response["query_filter"];
    showing_total_count.value = backoffice_orders_html_response["showing_total_count"];
}

export async function updateBackofficeModels() {
    let search_models_by_user_input = document.getElementById("search_models_by_user_input");
    let search_models_by_state_select = document.getElementById("search_models_by_state_select");
    let search_models_by_filesize_bracket_select = document.getElementById("search_models_by_filesize_bracket_select");
    let pagination_component = document.getElementById("pagination_component");

    let last_evaluated_key = document.getElementById("last_evaluated_key");
    let query = document.getElementById("query");
    let query_filter = document.getElementById("query_filter");
    let showing_total_count = document.getElementById("showing_total_count");

    let backoffice_models_html_response = await apiCaller("backoffice_models_html", {
        "search_user": search_models_by_user_input.value,
        "search_model_state": search_models_by_state_select.value,
        "search_model_filesize_bracket": search_models_by_filesize_bracket_select.value
    });

    pagination_component.innerHTML = backoffice_models_html_response["success"];
    last_evaluated_key.value = backoffice_models_html_response["last_evaluated_key"];
    query.value = backoffice_models_html_response["query"];
    query_filter.value = backoffice_models_html_response["query_filter"];
    showing_total_count.value = backoffice_models_html_response["showing_total_count"];
}



export async function submitBackofficeForm(order_id, command) {
    var backoffice_form = document.getElementById("backoffice_form");
    var order_id_input = document.getElementById("order_id");
    var command_input = document.getElementById("command");

    order_id_input.value = order_id;
    command_input.value = command;
    backoffice_form.submit();
}

export async function updateUserPaginationCount(select_input) {
    let update_user_response = await apiCaller('update_user', {
        "command": "update_user_pagination_count",
        "user_pagination_count": select_input.value
    });
    location.reload();
}
export async function openModalDeletePaymentMethod(payment_method_id) {
    let delete_payment_method_input = document.getElementById("delete_payment_method_input");
    let delete_payment_method_error_span = document.getElementById("delete_payment_method_error_span");
    delete_payment_method_error_span.innerHTML = "";
    delete_payment_method_input.value = payment_method_id;
    openModal('.modal.delete-payment-method-modal')
}

export async function saveDeletePaymentMethod() {
    let delete_payment_method_input = document.getElementById("delete_payment_method_input");
    let delete_payment_method_error_span = document.getElementById("delete_payment_method_error_span");

    let update_user_response = await apiCaller('update_user', {
        "command": "delete_payment_method",
        "payment_method_id": delete_payment_method_input.value
    });

    if ("error" in update_user_response) {
        delete_payment_method_error_span.innerHTML = update_user_response["error"];
    } else {
        location.reload()
    }
}


export async function saveMakeDefaultPaymentMethod(payment_method_id) {
    let payment_method_error_msg_span = document.getElementById("payment_method_error_msg_span");
    payment_method_error_msg_span.innerHTML = ""
    let update_user_response = await apiCaller('update_user', {
        "command": "make_default_payment_method",
        "payment_method_id": payment_method_id
    });
    if ("error" in update_user_response) {
        payment_method_error_msg_span.innerHTML = update_user_response["error"];
    } else {
        location.reload()
    }

}

export async function changePaymentHistoryPage(signal) {
    let payment_history_current_page_input = document.getElementById("payment_history_current_page_input");
    let payment_history_pages_count_input = document.getElementById("payment_history_pages_count_input");

    if (signal == "increase") {
        if (parseInt(payment_history_current_page_input.value) < parseInt(payment_history_pages_count_input.value)) {
            payment_history_current_page_input.value = parseInt(payment_history_current_page_input.value) + 1
        }
    } else if (signal == "decrease") {
        if (parseInt(payment_history_current_page_input.value) > 1) {
            payment_history_current_page_input.value = parseInt(payment_history_current_page_input.value) - 1
        }
    }
    showSelectedPaymentPage(payment_history_current_page_input.value)
}

export async function showCouponDiscountFields() {
    let coupon_discount_type_select = document.getElementById("coupon_discount_type_select");
    let total_discount_div = document.getElementById("total_discount_div");
    let percentage_discount_div = document.getElementById("percentage_discount_div");

    let coupon_brl_discount_input = document.getElementById("coupon_brl_discount_input");
    let coupon_usd_discount_input = document.getElementById("coupon_usd_discount_input");
    let coupon_percentage_discount_input = document.getElementById("coupon_percentage_discount_input");

    if (coupon_discount_type_select.value == "percentage") {
        total_discount_div.style.display = "none";
        percentage_discount_div.style.display = "";

        coupon_brl_discount_input.removeAttribute("required");
        coupon_usd_discount_input.removeAttribute("required");
        coupon_percentage_discount_input.setAttribute("required", "required");

    } else if (coupon_discount_type_select.value == "total") {
        total_discount_div.style.display = "";
        percentage_discount_div.style.display = "none";

        coupon_brl_discount_input.setAttribute("required", "required");
        coupon_usd_discount_input.setAttribute("required", "required");
        coupon_percentage_discount_input.removeAttribute("required");
    }
}

export async function addCouponToUser() {
    let coupon_code_input = document.getElementById("coupon_code_input");
    let plan_id_input = document.getElementById("plan_id_input");
    let plan_recurrency_input = document.getElementById("plan_recurrency_input");
    let coupon_error_msg_span = document.getElementById("coupon_error_msg_span");

    let update_user_response = await apiCaller('update_user', {
        "command": "add_coupon_to_user",
        "coupon_code": coupon_code_input.value,
        "plan_id": plan_id_input.value,
        "plan_recurrency": plan_recurrency_input.value,
    });

    if ("error" in update_user_response) {
        coupon_error_msg_span.innerHTML = update_user_response["error"]
    } else {
        location.reload()
    }
}


export async function openModalEditFederatedProject(federated_model_id) {
    let federated_required_ids = document.getElementById("federated_required_ids_" + federated_model_id);
    console.log("federated_required_ids", federated_required_ids);
    console.log("federated_required_ids.value", federated_required_ids.value);

    federated_required_ids_list = federated_required_ids.value.split(',');

    let edit_federated_model_id_input = document.getElementById("edit_federated_model_id_input");
    let edit_federated_model_rows_tbody = document.getElementById("edit_federated_model_rows_tbody");
    let edit_federated_model_error_span = document.getElementById("edit_federated_model_error_span");


    edit_federated_model_id_input.value = federated_model_id;
    edit_federated_model_error_span.innerHTML = "";

    let panel_explore_projects_modal_edit_federated_model_html_response = await apiCaller('panel_explore_projects_modal_edit_federated_model_html', {
        "federated_model_id": federated_model_id
    });

    edit_federated_model_rows_tbody.innerHTML = panel_explore_projects_modal_edit_federated_model_html_response["success"];
    openModal('.modal.edit-federated-model-modal');
}


export async function openModalAddModelToFederatedProject(folder_id) {
    let edit_federated_model_id_input = document.getElementById("edit_federated_model_id_input");
    var folder_id_add_model_to_federated_modal_input = document.getElementById("folder_id_add_model_to_federated_modal_input");
    var add_model_to_federated_modal_error_span = document.getElementById("add_model_to_federated_modal_error_span");
    var add_model_to_federated_model_user_folder_rows_tbody = document.getElementById("add_model_to_federated_model_user_folder_rows_tbody");
    var add_model_to_federated_modal_return_folder_span = document.getElementById("add_model_to_federated_modal_return_folder_span");
    var add_model_to_federated_modal_folder_path_span = document.getElementById("add_model_to_federated_modal_folder_path_span");
    var add_model_to_federated_modal_folder_id = document.getElementById("add_model_to_federated_modal_folder_id");

    add_model_to_federated_modal_return_folder_span.style.display = "none";
    add_model_to_federated_modal_folder_path_span.style.display = "none";

    var panel_explore_project_user_dicts_html_response = await apiCaller("panel_explore_project_user_dicts_html", {
        "model_html": "add_project_to_federated",
        "federated_model_id": edit_federated_model_id_input.value
    })

    folder_id_add_model_to_federated_modal_input.value = folder_id;
    add_model_to_federated_modal_error_span.innerHTML = "";
    add_model_to_federated_modal_folder_id.value = "";
    add_model_to_federated_model_user_folder_rows_tbody.innerHTML = panel_explore_project_user_dicts_html_response["success"];

    var federated_required_id_inputs = document.querySelectorAll('[id$="_federated_required_id_input"]');
    for (let federated_required_id_input of federated_required_id_inputs) {
        if (federated_required_ids_list.includes(federated_required_id_input.value)) {
            federated_required_id_input.checked = true;
        } else {
            federated_required_id_input.checked = false;
        }
    }
    openModal(".add-model-to-federated-modal");
}


export async function saveAddProjectsToFederatedProject() {
    let edit_federated_model_id_input = document.getElementById("edit_federated_model_id_input");
    let add_model_to_federated_modal_error_span = document.getElementById("add_model_to_federated_modal_error_span");
    let federated_required_ids = document.getElementById("federated_required_ids_" + edit_federated_model_id_input.value);

    var update_model = await apiCaller("update_model", {
        "command": "update_federated_model_required_ids",
        "model_id": edit_federated_model_id_input.value,
        "federated_required_ids": federated_required_ids_list
    })

    if ("error" in update_model) {
        add_model_to_federated_modal_error_span.innerHTML = update_model["error"];
    } else {
        federated_required_ids.value = update_model["federated_required_ids"];
        returnToModalEditFederatedProject();
        showUserDicts();
    }
}

export async function returnToModalEditFederatedProject() {
    let edit_federated_model_id_input = document.getElementById("edit_federated_model_id_input");
    closeModal(".modal.add-model-to-federated-modal")
    openModalEditFederatedProject(edit_federated_model_id_input.value)
}

export async function refreshEditFederatedProjectModal(folder_id) {
    let edit_federated_model_id_input = document.getElementById("edit_federated_model_id_input");
    var folder_id_add_model_to_federated_modal_input = document.getElementById("folder_id_add_model_to_federated_modal_input");
    var add_model_to_federated_model_user_folder_rows_tbody = document.getElementById("add_model_to_federated_model_user_folder_rows_tbody");
    var add_model_to_federated_modal_return_folder_span = document.getElementById("add_model_to_federated_modal_return_folder_span");
    var add_model_to_federated_modal_folder_path_span = document.getElementById("add_model_to_federated_modal_folder_path_span");

    var panel_explore_project_user_dicts_html_response = await apiCaller("panel_explore_project_user_dicts_html", {
        "folder_id": folder_id,
        "model_html": "add_project_to_federated",
        "federated_model_id": edit_federated_model_id_input.value
    })

    if (folder_id) {
        var update_user_response = await apiCaller("update_user", {
            "command": "get_folder",
            "folder_id": folder_id
        });
        add_model_to_federated_modal_return_folder_span.style.display = "";
        add_model_to_federated_modal_folder_path_span.innerHTML = update_user_response["success"]["folder_path"];
        add_model_to_federated_modal_folder_path_span.style.display = "";
    } else {
        add_model_to_federated_modal_return_folder_span.style.display = "none";
        add_model_to_federated_modal_folder_path_span.style.display = "none";
    }

    folder_id_add_model_to_federated_modal_input.value = folder_id;
    add_model_to_federated_model_user_folder_rows_tbody.innerHTML = panel_explore_project_user_dicts_html_response["success"];

    var federated_required_id_inputs = document.querySelectorAll('[id$="_federated_required_id_input"]');
    for (let federated_required_id_input of federated_required_id_inputs) {
        if (federated_required_ids_list.includes(federated_required_id_input.value)) {
            federated_required_id_input.checked = true;
        } else {
            federated_required_id_input.checked = false;
        }
    }
}

export async function openReturnFolderModalAddModelToFederated() {
    var folder_id_add_model_to_federated_modal_input = document.getElementById("folder_id_add_model_to_federated_modal_input");
    var update_user_response = await apiCaller("update_user", {
        "command": "get_root_folder",
        "folder_id": folder_id_add_model_to_federated_modal_input.value
    });
    if (update_user_response["success"]["folder_path"] != "") {
        refreshEditFederatedProjectModal(update_user_response["success"]["folder_id"]);
    } else {
        refreshEditFederatedProjectModal("");
    }
}



export async function removeModelFromFederatedProject(model_id_to_be_removed) {
    let edit_federated_model_id_input = document.getElementById("edit_federated_model_id_input");
    let edit_federated_model_rows_tbody = document.getElementById("edit_federated_model_rows_tbody");

    var update_model = await apiCaller("update_model", {
        "command": "remove_model_id_from_federated_model",
        "model_id": edit_federated_model_id_input.value,
        "model_id_to_be_removed": model_id_to_be_removed
    })

    let panel_explore_projects_modal_edit_federated_model_html_response = await apiCaller('panel_explore_projects_modal_edit_federated_model_html', {
        "federated_model_id": edit_federated_model_id_input.value
    });

    edit_federated_model_rows_tbody.innerHTML = panel_explore_projects_modal_edit_federated_model_html_response["success"];

    showUserDicts();
}

export async function changeSearchIcon(input) {
    const inputLength = input.value.length;
    const searchIcon = document.querySelector(".search-icon");
    const closeIcon = document.querySelector(".close-icon");
    if (inputLength > 0) {
        searchIcon.classList.add("none");
        closeIcon.classList.remove("none");
    } else {
        searchIcon.classList.remove("none");
        closeIcon.classList.add("none");
    }
}

export async function clearSearchInput(clearIcon, inputId) {
    const input = document.getElementById(inputId);
    input.value = "";
    clearIcon.classList.add("none");
    // document.querySelector(".search-icon").remove("none");
    changeSearchIcon(input);
    showUserDicts();
}



export async function checkIfCouponIsStillValid() {
    let coupon_code_input = document.getElementById("coupon_code_input");
    let plan_id_input = document.getElementById("plan_id_input");
    let plan_recurrency_input = document.getElementById("plan_recurrency_input");

    let update_user_response = await apiCaller('update_user', {
        "command": "add_coupon_to_user",
        "coupon_code": coupon_code_input.value,
        "plan_id": plan_id_input.value,
        "plan_recurrency": plan_recurrency_input.value,
    });

    if ("error" in update_user_response) {
        location.reload()
    }
}

export async function callBackofficeApi(order_id, command) {
    let backoffice_orders_error_span = document.getElementById("backoffice_orders_error_span");
    backoffice_orders_error_span.innerHTML = ""

    let update_backoffice_response = await apiCaller('update_backoffice', {
        "command": command,
        "order_id": order_id
    });

    if ("error" in update_backoffice_response) {
        backoffice_orders_error_span.innerHTML = update_backoffice_response["error"]
    } else {
        backoffice_orders_error_span.innerHTML = update_backoffice_response["success"]
    }
    backoffice_orders_error_span.style.display = "";
    updateBackofficeOrders()
}






export async function updateBackofficeUsers() {
    let backoffice_search_users_by_email_or_id_input = document.getElementById("backoffice_search_users_by_email_or_id_input");
    let search_users_by_subscription_select = document.getElementById("search_users_by_subscription_select");
    let pagination_component = document.getElementById("pagination_component");

    let last_evaluated_key = document.getElementById("last_evaluated_key");
    let query = document.getElementById("query");
    let query_filter = document.getElementById("query_filter");
    let showing_total_count = document.getElementById("showing_total_count");

    let backoffice_users_html_response = await apiCaller("backoffice_users_html", {
        "search_user": backoffice_search_users_by_email_or_id_input.value,
        "search_users_subscription": search_users_by_subscription_select.value
    });

    pagination_component.innerHTML = backoffice_users_html_response["success"];
    last_evaluated_key.value = backoffice_users_html_response["last_evaluated_key"];
    query.value = backoffice_users_html_response["query"];
    query_filter.value = backoffice_users_html_response["query_filter"];
    showing_total_count.value = backoffice_users_html_response["showing_total_count"];
}

export async function reprocessModel(pressed_button, model_id) {
    let translate_response = await apiCaller("translate", {
        "key": "Reprocessando..."
    });
    pressed_button.innerHTML = translate_response["success"];


    let update_backoffice_response = await apiCaller('update_backoffice', {
        "command": "reprocess_model",
        "model_id": model_id
    });

    await sleep(2000);
    translate_response = await apiCaller("translate", {
        "key": "Reprocessar"
    });
    pressed_button.innerHTML = translate_response["success"];

}

export async function updateBackofficeCoupons() {
    let search_coupons_by_name_or_code_input = document.getElementById("search_coupons_by_name_or_code_input");
    let pagination_component = document.getElementById("pagination_component");

    let last_evaluated_key = document.getElementById("last_evaluated_key");
    let query = document.getElementById("query");
    let query_filter = document.getElementById("query_filter");
    let showing_total_count = document.getElementById("showing_total_count");

    let backoffice_coupons_html_response = await apiCaller("backoffice_coupons_html", {
        "search_coupon": search_coupons_by_name_or_code_input.value
    });

    pagination_component.innerHTML = backoffice_coupons_html_response["success"];
    last_evaluated_key.value = backoffice_coupons_html_response["last_evaluated_key"];
    query.value = backoffice_coupons_html_response["query"];
    query_filter.value = backoffice_coupons_html_response["query_filter"];
    showing_total_count.value = backoffice_coupons_html_response["showing_total_count"];
}

export async function checkIfShareFolderIsAvailable() {
    let folder_is_password_protected = document.getElementById("folder_is_password_protected");
    let folder_is_accessible_input = document.getElementById("folder_is_accessible_input");

    if (folder_is_accessible_input.value == "False") {
        openModal(".not-acessible-folder-modal");
    } else if (folder_is_password_protected.value == "True") {
        openModal(".password-shared-project-modal");
    } else {
        showUserDicts();
    }
}


export async function uploadUserThumb(input) {
    var user_thumb_img = document.getElementById("user_thumb_img");
    var update_user_thumb_error_msg_span = document.getElementById("update_user_thumb_error_msg_span");
    var panel_menu_user_thumb_img = document.getElementById("panel_menu_user_thumb_img");

    update_user_thumb_error_msg_span.innerHTML = "";

    var files = input.files;
    var process_to_bucket = "upload.augin.app";
    var file = files[0];

    let file_name_array = file["name"].split(".");
    let file_name_extension = file_name_array[file_name_array.length - 1];

    let panel_get_aws_upload_keys_response = await apiCaller("panel_get_aws_upload_keys", {
        "key_extension": file_name_extension,
        "bucket": process_to_bucket
    });

    let post_data = {
        "key": panel_get_aws_upload_keys_response["success"]['key'],
        "AWSAccessKeyId": panel_get_aws_upload_keys_response["success"]['AWSAccessKeyId'],
        "policy": panel_get_aws_upload_keys_response["success"]['policy'],
        "signature": panel_get_aws_upload_keys_response["success"]['signature'],
        "file": file,
        "original_name": file["name"],
    };

    await uploadWithoutProgressBar(panel_get_aws_upload_keys_response["success"]['url'], post_data);

    let update_user_response = await apiCaller('update_user', {
        "command": "update_user_thumb",
        "thumb_key": panel_get_aws_upload_keys_response["success"]['key']
    });

    if ("error" in update_user_response) {
        update_user_thumb_error_msg_span.innerHTML = update_user_response["error"];
    } else {
        console.log("updating user_thumb image in src");
        let new_source_for_image = "https://processed.augin.app/" + update_user_response["user_thumb"];
        panel_menu_user_thumb_img.src = new_source_for_image;
        user_thumb_img.src = new_source_for_image;
    }
}



export async function addRandomDeviceToUser() {
    let update_user_response = await apiCaller("update_user", {
        "command": "add_random_device"
    });
    location.reload();
}


export async function openModalDisconnectDevice(device_id) {
    let disconnect_device_id_input = document.getElementById("disconnect_device_id_input");
    let disconnect_device_error_span = document.getElementById("disconnect_device_error_span");
    disconnect_device_id_input.value = device_id;
    disconnect_device_error_span.innerHTML = "";
    openModal('.modal.disconnect-device-modal');
}

export async function saveDisconnectDevice() {
    let disconnect_device_id_input = document.getElementById("disconnect_device_id_input");
    let disconnect_device_error_span = document.getElementById("disconnect_device_error_span");
    let update_user_response = await apiCaller("update_user", {
        "command": "disconnect_device",
        "device_id": disconnect_device_id_input.value
    });

    if ("error" in update_user_response) {
        disconnect_device_error_span.innerHTML = update_user_response["error"]
    } else {
        location.reload();
    }
}

export async function checkAllOptionalCookies(checkbox) {
    let tawkto_optional_cookie_consent = document.getElementById("tawkto_optional_cookie_consent");
    let mouseflow_optional_cookie_consent = document.getElementById("mouseflow_optional_cookie_consent");
    if (checkbox.checked) {
        tawkto_optional_cookie_consent.checked = true;
        mouseflow_optional_cookie_consent.checked = true;
    } else {
        tawkto_optional_cookie_consent.checked = false;
        mouseflow_optional_cookie_consent.checked = false;
    }
}