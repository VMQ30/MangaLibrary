const filterForm = document.getElementById("filter-form");

filterForm.addEventListener("change", function () {
  const formData = new FormData(filterForm);

  fetch("/browse", {
    method: "POST",
    body: formData,
    headers: {
      "X-Requested-With": "XMLHttpRequest",
    },
  })
    .then((response) => response.text())
    .then((html) => {
      document.getElementById("comic-container").innerHTML = html;
    })
    .catch((error) => console.error("Error:", error));
});
