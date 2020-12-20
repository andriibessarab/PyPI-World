// Define variables
let pkgName = document.querySelector("input[type=hidden][name=pkg_name]").value;
let setupName = document.querySelector("input[type=hidden][name=setup_name]").value;

let connectGitHubRepoForm = document.querySelector("#connectGitHubRepoForm");

SetFormEvents(connectGitHubRepoForm, `/pkg/${pkgName}/connect_github`, false, "reload", null);

let setupOpenButton = $("#setupOpenButton");
let setupModal = $("#setupModal");
let setupForm = document.querySelector("#setupForm");
let setupFormInputs = document.querySelectorAll(`#${setupForm.id} input`);

setupOpenButton.click(function(){
  setupModal.modal('show');
});

SetFormEvents(setupForm, `/pkg/${pkgName}/generate_setup`, false, "reload", null);

let publishButton = document.querySelector("button#publish-button")
publishButton.onclick = () => {
  // Disable publishButton
  publishButton.disabled = true;

  // Declare variables
  let xhttp = new XMLHttpRequest()

  // Show processing alert
  showAlert(
    `<div class="spinner-border text-warning" role="status">
      <span class="sr-only">Proccessing...</span>
    </div>`,
    "Proccessing your request. Don't leave the page.",
    "warning",
  );
  window.location.href = "#";

  // Open request
  xhttp.open("POST", `/pkg/${pkgName}/publish`);
  xhttp.onload = () => {
    // Declare variables
    response = JSON.parse(xhttp.responseText);

    // Display feedback
    if (response["successful-publication"]) {
      showAlert("Success!", "You will be redirected to PyPI.org shortly!", "success");
      window.open(`https://pypi.org/project/${setupName}/`, "_blank");
    } else if (response["successful-run"]) {
      for (cmd of response["commands"]) {
        if (cmd["return-code"] !== 0) {
          showAlert(
            "Error!",
            `Error while running &nbsp;
            <span class="text-monospace">${cmd["command"]}</span>
            <hr />
            <span class="text-monospace">${cmd["error"]}</span>`,
            "warning",
          );
        }
      }
    } else if (response["error"]) {
      showAlert("Error!", response["error"], "warning");
    } else if (response["unexpected-error"]) {
      showAlert("Oops!", "Unexpected error occured during the publication process. Please try again.", "danger");
    }

    // Enable publishButton
    publishButton.disabled = false;
  }
  xhttp.send()
}
