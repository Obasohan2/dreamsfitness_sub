document.addEventListener("DOMContentLoaded", function () {
    // Get the URL from meta tag
    const metaTag = document.querySelector('meta[name="reaction-url"]');
    const reactionUrl = metaTag ? metaTag.getAttribute("content") : null;

    if (!reactionUrl) {
        console.error("Reaction URL not found in meta tag.");
        return;
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');

    document.querySelectorAll(".react-btn").forEach(function (btn) {
        btn.addEventListener("click", function (e) {
            e.preventDefault();

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
                    reaction: action
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById(`likes-${postId}`).textContent = data.likes;
                    document.getElementById(`unlikes-${postId}`).textContent = data.unlikes;
                } else {
                    console.error("Server responded with error:", data.error);
                }
            })
            .catch(error => {
                console.error("Error sending request:", error);
            });
        });
    });
});
