document.addEventListener("DOMContentLoaded", function () {

    /* ================= CSRF ================= */
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie) {
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

    /* ================= LIKE / UNLIKE ================= */
    document.querySelectorAll(".react-btn").forEach(button => {
        button.addEventListener("click", function () {

            const postId = this.dataset.id;
            const reaction = this.dataset.action;

            fetch(POST_REACTION_URL, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrftoken,
                },
                body: JSON.stringify({
                    post_id: postId,
                    reaction: reaction,
                }),
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    document.getElementById(`likes-${postId}`).textContent = data.likes;
                    document.getElementById(`unlikes-${postId}`).textContent = data.unlikes;
                }
            })
            .catch(err => console.error("Reaction error:", err));
        });
    });

    /* ================= EDIT POST MODAL ================= */
    $('#editPostModal').on('show.bs.modal', function (event) {
        const button = $(event.relatedTarget);
        const url = button.data('url');

        const editLink = document.getElementById('editPostLink');
        if (editLink) {
            editLink.href = url;
        }
    });

    /* ================= DELETE POST MODAL ================= */
    $('#deletePostModal').on('show.bs.modal', function (event) {
        const button = $(event.relatedTarget);
        const url = button.data('url');

        const form = document.getElementById('deletePostForm');
        if (form) {
            form.action = url;
        }
    });

    /* ================= DELETE COMMENT MODAL ================= */
    $('#deleteCommentModal').on('show.bs.modal', function (event) {
        const button = $(event.relatedTarget);
        const url = button.data('url');

        const form = document.getElementById('deleteCommentForm');
        if (form) {
            form.action = url;
        }
    });

});
