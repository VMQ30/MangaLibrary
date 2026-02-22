function updateStatus(statusId, comicId) {
  fetch(`/change_reading_status/${comicId}`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: `reading_status_id=${statusId}`,
  }).then((response) => {
    if (response.ok) {
      console.log("Status updated!");
    }
  });
}

const stars = document.querySelectorAll(".ratings-button");

stars.forEach((star, index) => {
  star.addEventListener("click", () => {
    const rating = star.getAttribute("data-value");

    stars.forEach((s) => s.classList.remove("active"));
    updateStarDisplay(rating);

    // Optional: Send to Flask via fetch
    // saveRating(rating);
  });
});

function updateStarDisplay(rating) {
  stars.forEach((star) => {
    if (star.getAttribute("data-value") <= rating) {
      star.classList.add("active");
    } else {
      star.classList.remove("active");
    }
  });
}
