document.addEventListener("DOMContentLoaded", function () {
    const metaTag = document.querySelector('meta[name="reaction-url"]');
    let reactionUrl = metaTag ? metaTag.content : window.location.origin + '/blog/post-reaction/';
    const csrftoken = document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];

    if (!csrftoken) {
        console.error("CSRF token not found.");
        return;
    }

    document.querySelectorAll('.react-btn').forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();

            const postId = this.dataset.id;
            const action = this.dataset.action;

            if (!postId || !action) {
                console.warn("Missing post ID or action");
                return;
            }

            fetch(reactionUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    post_id: postId,
                    reaction: action
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update counts
                    const likeCount = document.querySelector(`#likes-${postId}`);
                    const unlikeCount = document.querySelector(`#unlikes-${postId}`);

                    if (likeCount) likeCount.textContent = data.likes;
                    if (unlikeCount) unlikeCount.textContent = data.unlikes;
                } else {
                    alert(data.error || "Something went wrong.");
                }
            })
            .catch(error => {
                console.error("Fetch error:", error);
                alert("Error: Could not update reaction. Please try again.");
            });
        });
    });
});
