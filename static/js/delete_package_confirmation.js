// Declare variables
var deletePkgConfirmationForm = document.querySelector("#delete-pkg-confirmation-form");
var deletePkgConfirmationFormConfirmation = document.querySelector(`#${deletePkgConfirmationForm.id} #confirmation-input`);
var deletePkgConfirmationFormSubmit = document.querySelector(`#${deletePkgConfirmationForm.id} button[type=submit]`);
var correctConfirmation = document.querySelector("#correct-confirmation").innerHTML;

// Validate deletePkgConfirmationFormConfirmation on DOMContentLoaded
validateConfirmationFormConfirmation();

// Validate deletePkgConfirmationFormConfirmation onkeyup
deletePkgConfirmationFormConfirmation.onkeyup = validateConfirmationFormConfirmation;

function validateConfirmationFormConfirmation() {
  // Declare variables
  var deletePkgConfirmationFormConfirmationValue = deletePkgConfirmationFormConfirmation.value;

  if (deletePkgConfirmationFormConfirmationValue == correctConfirmation) {
    deletePkgConfirmationFormSubmit.disabled = false;
  } else {
    deletePkgConfirmationFormSubmit.disabled = true;
  }
}
