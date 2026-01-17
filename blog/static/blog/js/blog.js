document.addEventListener("DOMContentLoaded", function () {

    // ===============================
    // Get reaction URL from meta tag
    // ===============================
    const reactionMeta = document.querySelector('meta[name="reaction-url"]');

    if (!reactionMeta) {
        console.error("reaction-url meta tag missing");
        return;
    }

    const POST_REACTION_URL = reactionMeta.getAttribute("content");

    // ===============================
    // Get CSRF token from cookies
    // ===============================
    function getCookie(name) {
        let cookieValue = null;

        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");

            for (let cookie of cookies) {
                cookie = cookie.trim();

                if (cookie.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(
                        cookie.substring(name.length + 1)
                    );
                    break;
                }
            }
        }

        return cookieValue;
    }

    const csrftoken = getCookie("csrftoken");

    // ===============================
    // Handle reaction clicks
    // ===============================
    document.querySelectorAll(".react-btn").forEach(button => {

        button.addEventListener("click", function () {

            const postId = this.dataset.id;
            const action = this.dataset.action;

            if (!postId || !action) {
                console.error("Missing postId or action");
                return;
            }

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
                    throw new Error(`Request failed: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {

                if (data.status !== "ok") {
                    console.error("❌ Reaction failed:", data);
                    return;
                }

                // ===============================
                // Safely update counts (if present)
                // ===============================
                const likesEl = document.getElementById(`likes-${postId}`);
                const unlikesEl = document.getElementById(`unlikes-${postId}`);

                if (likesEl) {
                    likesEl.textContent = data.likes;
                }

                if (unlikesEl) {
                    unlikesEl.textContent = data.unlikes;
                }

            })
            .catch(error => {
                console.error("❌ Reaction error:", error);
            });

        });

    });

});
