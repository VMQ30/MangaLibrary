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
