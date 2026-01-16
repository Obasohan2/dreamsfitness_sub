document.addEventListener("DOMContentLoaded", function () {

    const reactionMeta = document.querySelector('meta[name="reaction-url"]');
    const csrfMeta = document.querySelector('meta[name="csrf-token"]');

    if (!reactionMeta || !csrfMeta) {
        console.error("Reaction meta tags missing");
        return;
    }

    const reactionUrl = reactionMeta.getAttribute("content");
    const csrftoken = csrfMeta.getAttribute("content");

    document.querySelectorAll(".react-btn").forEach(button => {

        button.addEventListener("click", function () {

            const postId = this.dataset.id;
            const action = this.dataset.action;

            fetch(reactionUrl, {
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
                    return response.text().then(text => {
                        throw new Error(text);
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.status === "ok") {
                    document.getElementById(`likes-${postId}`).innerText = data.likes;
                    document.getElementById(`unlikes-${postId}`).innerText = data.unlikes;
                }
            })
            .catch(error => {
                console.error("Reaction error:", error.message);
            });
        });
    });
});
