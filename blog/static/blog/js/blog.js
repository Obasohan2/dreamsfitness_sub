$(document).ready(function () {
    let reactionUrl = $('meta[name="reaction-url"]').attr("content");
    if (!reactionUrl) {
        reactionUrl = window.location.origin + '/blog/post-reaction/';
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

    $(document).on("click", ".react-btn", function (e) {
        e.preventDefault();

        const $button = $(this);
        const postId = $button.data("id");
        const action = $button.data("action");

        if (!postId || !action) {
            console.error("Missing data attributes");
            return;
        }

        // Add loading class
        $button.addClass("loading").prop("disabled", true);

        $.ajax({
            url: reactionUrl,
            method: "POST",
            headers: {
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            data: JSON.stringify({
                post_id: postId,
                reaction: action
            }),
            success: function (response) {
                $button.removeClass("loading").prop("disabled", false);

                if (response.success) {
                    // Update like/unlike counts
                    $(`#likes-${postId}`).text(response.likes);
                    $(`#unlikes-${postId}`).text(response.unlikes);

                    // Update icons
                    if (action === "like") {
                        $(`.react-btn[data-action="like"][data-id="${postId}"] i`)
                            .removeClass("far text-secondary").addClass("fas text-danger");
                        $(`.react-btn[data-action="unlike"][data-id="${postId}"] i`)
                            .removeClass("fas text-secondary").addClass("far text-secondary");
                    } else if (action === "unlike") {
                        $(`.react-btn[data-action="unlike"][data-id="${postId}"] i`)
                            .removeClass("far text-danger").addClass("fas text-secondary");
                        $(`.react-btn[data-action="like"][data-id="${postId}"] i`)
                            .removeClass("fas text-danger").addClass("far text-danger");
                    }

                    // Show success tick briefly (change span text)
                    const $span = $button.find('.btn-text');
                    const originalText = $span.text();
                    $span.text('✓');
                    setTimeout(() => {
                        $span.text(originalText);
                    }, 600);
                } else {
                    alert("Error: " + (response.error || "Something went wrong."));
                }
            },
            error: function (xhr) {
                $button.removeClass("loading").prop("disabled", false);

                if (xhr.status === 403) {
                    alert("Please login to react to posts.");
                    window.location.href = '/accounts/login/?next=' + window.location.pathname;
                } else if (xhr.status === 404) {
                    alert("Post not found or reaction URL incorrect.");
                } else {
                    alert("Server error. Please try again later.");
                }
            }
        });
    });
});
