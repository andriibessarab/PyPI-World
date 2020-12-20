// GLOBALS
let currentUserUsername = document.querySelector("input[type=hidden][name=username]").value;
let inputsInfo = JSON.parse(document.querySelector("input[type=hidden][name=inputs_info]").value);
let setupArgsInfo = JSON.parse(document.querySelector("input[type=hidden][name=setup_args_info]").value);

// INITIALIZE POPOVERS
$(function () {
  $('[data-toggle="popover"]').popover()
})
$("[data-toggle=popover]")
.popover({html:true})

// CUSTOM ALERT
let customAlert = document.querySelector("#alert");
let customAlertHeader = document.querySelector(`#${customAlert.id}>strong`);
let customAlertBody = document.querySelector(`#${customAlert.id}>span`);

// Alert functions
function showAlert(header, body, color) {

  // Remove color
  customAlert.classList.remove("alert-success", "alert-warning", "alert-danger", "d-block", "d-none");

  // Insert heading, body, set color & show alert
  customAlertHeader.innerHTML = header;
  customAlertBody.innerHTML = body;
  customAlert.classList.add(`alert-${color}`, "d-block");
}

// FORMS VALIDATION/SUBMISSION
/*
  FORM RULES
    $ Run SetFormEvents function for each form
    $ All editable inputs must have attributes "id" "name"(equivalent to one in inputsInfo) "autocomplete"(set to off) "data-input" "data-required" & classes "form-control"
      ^ Attributes "type", "id" "placeholder" "maxlength" should be set
    $ All editable inputs must have div with attributes "data-for"(set to input's id) & classes "invalid-feedback"
    $ All required inputs must have attribute "data-required"
    $ Submit button must have attributes "data-form"(sett to form's id)
*/

function SetFormEvents(form, requestURL, hasInvalidFeedback, successAction, successValue) {

  // Validate form onkeyup
  form.onkeyup = function() {
    ValidateForm(form, hasInvalidFeedback);
  }

  // Validate Form onchange
  form.onchange = function() {
    ValidateForm(form, hasInvalidFeedback);
  }

  // Submit Form onsubmit
  document.querySelector(`button[type=submit][data-form=${form.id}]`).onclick = function() {
    SubmitForm(form, requestURL, hasInvalidFeedback, successAction, successValue);
    return false;
  }
}

function ValidateForm(form, hasInvalidFeedback) {
  let formInputs = [];
  let formSubmitButton = document.querySelector(`button[type=submit][data-form=${form.id}]`);
  let hasInvalidInput = false;

  // Add all inputs to formInputs & submit button to formSubmitButton
  for (i of form) {
    if (i.hasAttribute("data-input")) {
      formInputs.push(i)
    }
  }

  // Validate all inputs
  for (i of formInputs) {
    // Declare variables
    let input = i;
    let inputID = input.id;
    let inputName = i.name;
    let inputValue = i.value;
    let inputLength = inputValue.length;
    let inputIsRequired = i.hasAttribute("data-required");
    let inputInvalidFeedback = document.querySelector(`div.invalid-feedback[data-for=${inputID}]`);
    let inputRegex = new RegExp(inputsInfo[inputName]["regex"]);
    let inputRegexNote = inputsInfo[inputName]["regex-note"];
    let inputMinLength = inputsInfo[inputName]["min-length"];
    let inputMaxLength = inputsInfo[inputName]["max-length"];

    // Clear validation classes
    input.classList.remove("is-valid", "is-invalid");

    //Clear the inputInvalidFeedback
    if (hasInvalidFeedback) {
      inputInvalidFeedback.innerHTML = "";
    }

    // Check if input hav value
    if (inputValue.split(" ").join("") === "") {
      // If input is required, add "is-invalid" class & show feedback & set hasInvalidInput to true
      if (inputIsRequired) {
        input.classList.add("is-invalid");

        hasInvalidInput = true;
      }

      // Skip to the next input
      continue;
    }

    // Check if input is valid using regex
    if (!inputRegex.test(inputValue)) {
      // Add "is-invalid" class
      input.classList.add("is-invalid");

      // Show feedback
      if (hasInvalidFeedback) {
        inputInvalidFeedback.innerHTML = inputRegexNote;
      }

      // Set hasInvalidInput to true
      hasInvalidInput = true;

      // Skip to the next input
      continue;
    }

    // Check if input's len is over input's max length
    if (inputLength > inputMaxLength || inputLength < inputMinLength) {
      // Add "is-invalid" class
      input.classList.add("is-invalid");

      // Show feedback
      if (hasInvalidFeedback) {
        inputInvalidFeedback.innerHTML = `Invalid length(${inputMinLength} - ${inputMaxLength} char.)`;
      }

      // Set hasInvalidInput to true
      hasInvalidInput = true;

      // Skip to the next input
      continue;
    }

    // Add "is-valid" class
    input.classList.add("is-valid");
  }

  // Enable/disabled button
  if (hasInvalidInput) {
    formSubmitButton.disabled = true;
  } else {
    formSubmitButton.disabled = false;
  }
}

function SubmitForm(form, requestURL, hasInvalidFeedback, successAction, successValue) {
  let formInputs = [];
  let formSubmitButton = document.querySelector(`button[type=submit][data-form=${form.id}]`);
  let hasInvalidInput = false;

  // Add all inputs to formInputs & submit button to formSubmitButton
  for (i of form) {
    if (i.hasAttribute("data-input")) {
      formInputs.push(i)
    }
    if (i.type === "submit") {
      formSubmitButton = i;
    }
  }

  // Open new XMLHttpRequest
  let xhttp = new XMLHttpRequest();
  let formData = new FormData(form);

  xhttp.open("POST", requestURL);
  xhttp.onload = () => {
    // Declare variables
    let response = JSON.parse(xhttp.responseText);

    // Display response
    if (response["success"]) { // Success
      // Do if successAction is redirect
      if (successAction === "redirect") {
        window.location.href = successValue;
      }

      // Do if successAction is reload
      if (successAction === "reload") {
        formSubmitButton.disabled = true;
        window.location.reload();
      }

      // Do if successAction is alert
      if (successAction === "alert") {
        // Alert the success
        showAlert("Success!", successValue, "success");

        // Clear all inputs
        for (i of formInputs) {
          i.value = "";
        }

        // Diables form's submit button
        formSubmitButton.disabled = true;
      }

    } else if (response["unexpected-error"]) { // Unexpected error
      // Alert unexpected error
      showAlert("Oops!", "Unexpected error occurred. Please try again.", "danger");
    } else if (response["error"]) { // Error
      // Declare variables
      let formError = response["error"]["form-error"];
      let inputsErrors = response["error"]["inputs-errors"];

      // Display alert with form error
      if (formError) {
        showAlert("Oops!", formError, "warning")
      }

      // Display inputs' errors
      if (inputsErrors) {
        for (i of formInputs) {
          // Declare variables
          let input = i;
          let inputID = input.id;
          let inputName = i.name;
          let inputInvalidFeedback = document.querySelector(`div.invalid-feedback[data-for=${inputID}]`);

          // Check if  input has error
          if (inputsErrors[inputName]) {
            // Set "is-invalid" class
            input.classList.remove("is-valid", "is-invalid");
            input.classList.add("is-invalid");

            // Display feedback
            if (hasInvalidFeedback) {
              inputInvalidFeedback.innerHTML = inputsErrors[inputName];
            }
          }
        }
      }
    }

    // Redirect user to top of page
    window.location.href = "#";
  }
  xhttp.send(formData);
}
