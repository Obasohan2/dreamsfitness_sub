const btn = document.querySelector(".like-btn");
const countEl = document.querySelector(".like-count");

btn.addEventListener("click", async () => {
  if (btn.disabled) return;
  btn.disabled = true;

  const response = await fetch("/blog/reaction/", {
    method: "POST",
    headers: {
      "X-CSRFToken": csrfToken,
    },
    body: new URLSearchParams({
      post_id: btn.dataset.postId
    })
  });

  const data = await response.json();

  countEl.textContent = data.count;
  btn.classList.toggle("liked", data.liked);
  btn.textContent = data.liked ? "Unlike" : "Like";

  btn.disabled = false;
});

