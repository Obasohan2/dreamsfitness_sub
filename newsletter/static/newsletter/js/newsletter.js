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
      .then(res => res.json())
      .then(data => {
        document.getElementById("newsletterModalMessage").innerText = data.message;
        $('#newsletterSuccessModal').modal('show');
        if (data.status === "success") form.reset();
      })
      .catch(() => {
        document.getElementById("newsletterModalMessage").innerText =
          "Something went wrong. Please try again.";
        $('#newsletterSuccessModal').modal('show');
      });
  });
});
