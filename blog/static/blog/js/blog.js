document.addEventListener("DOMContentLoaded", function () {

    /* ====================================================
       GET REACTION URL FROM META TAG
    ==================================================== */
    const reactionMeta = document.querySelector(
        'meta[name="reaction-url"]'
    );

    if (!reactionMeta) {
        console.error("❌ reaction-url meta tag missing");
        return;
    }

    const POST_REACTION_URL = reactionMeta.getAttribute("content");

    /* ====================================================
       CSRF TOKEN HELPER (DJANGO SAFE)
    ==================================================== */
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

    if (!csrftoken) {
        console.error("❌ CSRF token not found");
        return;
    }

    /* ====================================================
       LIKE / UNLIKE BUTTON HANDLER
    ==================================================== */
    document.querySelectorAll(".react-btn").forEach(button => {

        button.addEventListener("click", function (event) {
            event.preventDefault();

            const postId = this.dataset.id;
            const action = this.dataset.action; // "like" or "unlike"

            if (!postId || !action) {
                console.error("❌ Missing post ID or action");
                return;
            }

            // Prevent double clicks
            this.disabled = true;

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
                    throw new Error(`HTTP ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.status === "ok") {
                    const likesEl = document.getElementById(`likes-${postId}`);
                    const unlikesEl = document.getElementById(`unlikes-${postId}`);

                    if (likesEl) likesEl.textContent = data.likes;
                    if (unlikesEl) unlikesEl.textContent = data.unlikes;
                } else {
                    console.error("❌ Server error:", data);
                }
            })
            .catch(error => {
                console.error("❌ Reaction error:", error);
            })
            .finally(() => {
                this.disabled = false;
            });
        });

    });

});
