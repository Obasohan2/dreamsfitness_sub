document.addEventListener("DOMContentLoaded", function () {

    const reactionMeta = document.querySelector(
        'meta[name="reaction-url"]'
    );

    if (!reactionMeta) {
        console.error("❌ reaction-url meta tag missing");
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

    document.addEventListener("click", function (event) {

        const button = event.target.closest(".react-btn");
        if (!button) return;

        event.preventDefault();

        const postId = button.getAttribute("data-id");
        const action = button.getAttribute("data-action");

        if (!postId || !action) {
            console.error("❌ Missing post_id or action", { postId, action });
            return;
        }

        button.disabled = true;

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
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === "ok") {
                document.getElementById(`likes-${postId}`).textContent = data.likes;
                document.getElementById(`unlikes-${postId}`).textContent = data.unlikes;
            } else {
                console.error("❌ Server rejected:", data);
            }
        })
        .catch(error => {
            console.error("❌ Reaction failed:", error);
        })
        .finally(() => {
            button.disabled = false;
        });
    });

});
