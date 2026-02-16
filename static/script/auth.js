(function () {
  checkTextBox();
  movePanel();
})();

function checkTextBox() {
  document.querySelectorAll(".textbox").forEach((input) => {
    input.addEventListener("input", () => {
      input.parentElement.classList.toggle(
        "has-text",
        input.value.trim() !== "",
      );
    });
  });
}

function movePanel() {
  const panel = document.querySelector(".slider");
  const signIn = document.querySelector(".change-sign-in");
  const signUp = document.querySelector(".change-sign-up");

  const signUpPanel = document.querySelector(".sign-up-panel");
  const signInPanel = document.querySelector(".sign-in-panel");

  signUp.addEventListener("click", () => {
    panel.classList.add("change-panel");
    signUpPanel.classList.add("move-left");
    signUpPanel.style.opacity = "0";
    signInPanel.style.opacity = "1";
    signInPanel.classList.add("move-left");
  });

  signIn.addEventListener("click", () => {
    panel.classList.remove("change-panel");
    signUpPanel.classList.remove("move-left");
    signInPanel.classList.remove("move-left");
    signUpPanel.style.opacity = "1";
    signInPanel.style.opacity = "0";
  });
}
