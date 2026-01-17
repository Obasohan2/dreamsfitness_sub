document.addEventListener("DOMContentLoaded", function () {

    // Read reaction URL from meta tag
    const reactionMeta = document.querySelector('meta[name="reaction-url"]');

    if (!reactionMeta) {
        console.error("Reaction URL meta tag missing");
        return;
    }

    const POST_REACTION_URL = reactionMeta.getAttribute("content");

    // Get CSRF token
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
            const action = this.dataset.action; // ✅ MUST be "action"

            fetch(POST_REACTION_URL, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrftoken,
                    "X-Requested-With": "XMLHttpRequest"
                },
                body: JSON.stringify({
                    post_id: postId,
                    action: action
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error("Request failed");
                }
                return response.json();
            })
            .then(data => {
                if (data.status === "ok") {
                    document.getElementById(`likes-${postId}`).textContent = data.likes;
                    document.getElementById(`unlikes-${postId}`).textContent = data.unlikes;
                }
            })
            .catch(error => {
                console.error("Reaction error:", error);
            });
        });
    });

});
