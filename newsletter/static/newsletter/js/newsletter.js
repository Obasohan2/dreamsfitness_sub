document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("newsletterForm");
  if (!form) return;

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    fetch(form.action, {
      method: "POST",
      body: new FormData(form),
      headers: {
        "X-Requested-With": "XMLHttpRequest"
      }
    })
    .then(response => response.json())
    .then(data => {
      const msg = document.getElementById("newsletterModalMessage");
      msg.textContent = data.message;

      $('#newsletterSuccessModal').modal('show');

      if (data.status === "success") {
        form.reset();
      }
    })
    .catch(() => {
      document.getElementById("newsletterModalMessage").textContent =
        "Something went wrong. Please try again.";
      $('#newsletterSuccessModal').modal('show');
    });
  });
});
