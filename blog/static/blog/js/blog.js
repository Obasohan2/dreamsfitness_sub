document.addEventListener("DOMContentLoaded", () => {
    const buttons = document.querySelectorAll(".react-btn");

    const reactionUrlMeta = document.querySelector('meta[name="reaction-url"]');
    const csrfTokenMeta = document.querySelector('meta[name="csrf-token"]');

    if (!reactionUrlMeta || !csrfTokenMeta) {
        console.error("Missing required meta tags for CSRF or reaction URL.");
        return;
    }

    const POST_REACTION_URL = reactionUrlMeta.getAttribute("content");
    const csrfToken = csrfTokenMeta.getAttribute("content");

    buttons.forEach(button => {
        button.addEventListener("click", async () => {
            const postId = button.getAttribute("data-id");
            const action = button.getAttribute("data-action");

            if (!postId || !action) {
                console.error("Missing post ID or action.");
                return;
            }

            try {
                const response = await fetch(POST_REACTION_URL, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken,
                    },
                    body: JSON.stringify({
                        post_id: postId,
                        reaction: action,
                    }),
                });

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }

                const data = await response.json();

                if (data.success) {
                    // Update like and unlike counts in the DOM
                    const likesSpan = document.getElementById(`likes-${postId}`);
                    const unlikesSpan = document.getElementById(`unlikes-${postId}`);

                    if (likesSpan) {
                        likesSpan.textContent = data.likes;
                    }

                    if (unlikesSpan) {
                        unlikesSpan.textContent = data.unlikes;
                    }
                } else {
                    console.error("Server error:", data.error);
                }
            } catch (error) {
                console.error("Error sending reaction:", error);
            }
        });
    });
});
