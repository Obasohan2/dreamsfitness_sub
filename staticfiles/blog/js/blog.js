$(document).ready(function () {
    console.log("blog.js loaded");

    // Get reaction endpoint from meta tag or fallback
    let reactionUrl = $('meta[name="reaction-url"]').attr("content");
    if (!reactionUrl) {
        reactionUrl = `${window.location.origin}/blog/post-reaction/`;
        console.warn("Meta tag missing. Using fallback reaction URL:", reactionUrl);
    } else {
        console.log("Using meta tag reaction URL:", reactionUrl);
    }

    // CSRF token retrieval
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');
    console.log("CSRF token retrieved:", !!csrftoken);

    // AJAX handler for Like/Unlike
    $(document).on("click", ".react-btn", function (e) {
        e.preventDefault();
        console.log("Reaction button clicked");

        const $button = $(this);
        const postId = $button.data("id");
        const action = $button.data("action");

        if (!postId || !action) {
            console.error("Missing post ID or action");
            return;
        }

        const originalHTML = $button.html();
        $button.html('<i class="fas fa-spinner fa-spin"></i>').prop('disabled', true);

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
                console.log("AJAX success:", response);
                $button.html(originalHTML).prop('disabled', false);

                if (response.success) {
                    // Update like/unlike counters
                    $(`#likes-${postId}`).text(response.likes);
                    $(`#unlikes-${postId}`).text(response.unlikes);

                    // Toggle icons visually
                    if (action === 'like') {
                        $button.find('i').removeClass('far text-secondary').addClass('fas text-danger');
                        $(`.react-btn[data-action="unlike"][data-id="${postId}"] i`)
                            .removeClass('fas text-secondary').addClass('far text-secondary');
                    } else {
                        $button.find('i').removeClass('far text-danger').addClass('fas text-secondary');
                        $(`.react-btn[data-action="like"][data-id="${postId}"] i`)
                            .removeClass('fas text-danger').addClass('far text-danger');
                    }

                    // Flash check mark ✓ briefly
                    const $countSpan = $button.find('span');
                    const originalText = $countSpan.text();
                    $countSpan.text('✓');
                    setTimeout(() => {
                        $countSpan.text(originalText);
                    }, 500);
                } else {
                    console.warn("Server returned success: false", response);
                    if (response.error) {
                        alert("Error: " + response.error);
                    }
                }
            },
            error: function (xhr, status, error) {
                console.error("AJAX error:", xhr.status, error);
                $button.html(originalHTML).prop('disabled', false);

                if (xhr.status === 403) {
                    alert("Login required to react.");
                    window.location.href = '/accounts/login/?next=' + window.location.pathname;
                } else if (xhr.status === 404) {
                    alert("Reaction failed: Post not found.");
                } else if (xhr.status === 500) {
                    alert("Server error. Please try again later.");
                } else {
                    alert("Unexpected error: " + error);
                }
            }
        });
    });

    console.log("Reaction handler registered");
});
