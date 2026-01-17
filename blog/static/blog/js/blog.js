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

    document.addEventListener("click", function (event) {

        const button = event.target.closest(".react-btn");
        if (!button) return;

        const postId = button.dataset.id;
        const action = button.dataset.action;

        if (!postId || !action) {
            console.error("Missing postId or action");
            return;
        }

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
