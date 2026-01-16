document.addEventListener("DOMContentLoaded", function () {
    console.log("blog.js loaded");

    let reactionUrl = document.querySelector('meta[name="reaction-url"]')?.content;
    
    if (!reactionUrl) {
        reactionUrl = window.location.origin + '/blog/post-reaction/';
        console.warn("Fallback to reaction URL:", reactionUrl);
    }

    // Get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');

    // Handle Like/Unlike
    document.querySelectorAll(".react-btn").forEach(button => {
        button.addEventListener("click", function (e) {
            e.preventDefault();

            const postId = this.dataset.id;
            const action = this.dataset.action;

            if (!postId || !action) {
                console.error("Missing post ID or action.");
                return;
            }

            // Add disabled class
            this.classList.add("disabled");

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
                console.log("Reaction Response:", data);

                this.classList.remove("disabled");

                if (data.success) {
                    document.getElementById(`likes-${postId}`).textContent = data.likes;
                    document.getElementById(`unlikes-${postId}`).textContent = data.unlikes;

                    // Update icon classes (optional CSP-safe feedback)
                    const likeBtn = document.querySelector(`.react-btn[data-id="${postId}"][data-action="like"]`);
                    const unlikeBtn = document.querySelector(`.react-btn[data-id="${postId}"][data-action="unlike"]`);

                    if (action === "like") {
                        likeBtn.querySelector("i").classList.replace("far", "fas");
                        unlikeBtn.querySelector("i").classList.replace("fas", "far");
                    } else if (action === "unlike") {
                        unlikeBtn.querySelector("i").classList.replace("far", "fas");
                        likeBtn.querySelector("i").classList.replace("fas", "far");
                    }

                } else {
                    alert(data.error || "An error occurred.");
                }
            })
            .catch(error => {
                console.error("AJAX Error:", error);
                alert("An error occurred. Please try again.");
                this.classList.remove("disabled");
            });
        });
    });
});
