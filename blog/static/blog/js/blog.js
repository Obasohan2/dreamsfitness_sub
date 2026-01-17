document.addEventListener("DOMContentLoaded", function () {

    const reactionMeta = document.querySelector(
        'meta[name="reaction-url"]'
    );

    const csrfMeta = document.querySelector(
        'meta[name="csrf-token"]'
    );

    if (!reactionMeta || !csrfMeta) {
        console.error("Missing reaction-url or csrf-token meta tag");
        return;
    }

    const POST_REACTION_URL = reactionMeta.getAttribute("content");
    const csrftoken = csrfMeta.getAttribute("content");

    document.querySelectorAll(".react-btn").forEach((button) => {

        button.addEventListener("click", function () {

            const postId = this.dataset.id;
            const action = this.dataset.action;

            if (!postId || !action) {
                console.error("Missing post ID or action");
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
                .then((response) => {
                    if (!response.ok) {
                        throw new Error("Reaction request failed");
                    }
                    return response.json();
                })
                .then((data) => {
                    if (data.status === "ok") {

                        const likesEl = document.getElementById(
                            `likes-${postId}`
                        );

                        const unlikesEl = document.getElementById(
                            `unlikes-${postId}`
                        );

                        if (likesEl) {
                            likesEl.textContent = data.likes;
                        }

                        if (unlikesEl) {
                            unlikesEl.textContent = data.unlikes;
                        }
                    }
                })
                .catch((error) => {
                    console.error("Reaction error:", error);
                });

        });

    });

});
