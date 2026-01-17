document.addEventListener("DOMContentLoaded", function () {

    const reactionMeta = document.querySelector('meta[name="reaction-url"]');

    if (!reactionMeta) {
        console.error("Reaction URL meta tag missing");
        return;
    }

    const POST_REACTION_URL = reactionMeta.getAttribute("content");

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            document.cookie.split(";").forEach(cookie => {
                cookie = cookie.trim();
                if (cookie.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(
                        cookie.substring(name.length + 1)
                    );
                }
            });
        }
        return cookieValue;
    }

    const csrftoken = getCookie("csrftoken");

    document.querySelectorAll(".react-btn").forEach(button => {

        button.addEventListener("click", function () {

            const postId = this.dataset.id;
            let action = this.dataset.action;

            fetch(POST_REACTION_URL, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrftoken,
                    "X-Requested-With": "XMLHttpRequest",
                },
                body: JSON.stringify({
                    post_id: postId,
                    action: action,
                }),
            })
            .then(response => response.json())
            .then(data => {

                if (data.status !== "ok") {
                    console.error("Reaction failed");
                    return;
                }

                // Update counts
                document.getElementById(`likes-${postId}`).textContent = data.likes;
                document.getElementById(`unlikes-${postId}`).textContent = data.unlikes;

                // Toggle action + UI
                if (action === "like") {
                    this.dataset.action = "unlike";
                    this.classList.add("active");
                } else {
                    this.dataset.action = "like";
                    this.classList.remove("active");
                }
            })
            .catch(error => {
                console.error("Reaction error:", error);
            });
        });
    });
});
