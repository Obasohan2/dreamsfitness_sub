document.addEventListener("DOMContentLoaded", function () {

    const reactionUrl = document.querySelector('meta[name="reaction-url"]').content;
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

    document.querySelectorAll(".react-btn").forEach(button => {
        button.addEventListener("click", function () {

            const postId = this.dataset.id;
            const action = this.dataset.action;

            fetch(reactionUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken,
                    "X-Requested-With": "XMLHttpRequest"
                },
                body: JSON.stringify({
                    post_id: postId,
                    action: action
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === "ok") {
                    document.getElementById(`likes-${postId}`).textContent = data.likes;
                    document.getElementById(`unlikes-${postId}`).textContent = data.unlikes;
                }
            })
            .catch(error => console.error("Reaction error:", error));
        });
    });
});
