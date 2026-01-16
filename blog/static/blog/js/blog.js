document.addEventListener("DOMContentLoaded", function () {
    console.log("blog.js loaded");

    let reactionUrl = document.querySelector('meta[name="reaction-url"]');
    reactionUrl = reactionUrl ? reactionUrl.content : null;

    if (!reactionUrl) {
        console.warn("Reaction URL not found in meta tag.");
        return;
    }

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

    $(document).on('click', '.react-btn', function (e) {
        e.preventDefault();

        const $button = $(this);
        const postId = $button.data('id');
        const action = $button.data('action');

        if (!postId || !action) {
            console.error("Missing data attributes");
            return;
        }

        $button.prop('disabled', true);

        $.ajax({
            url: reactionUrl,
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            contentType: 'application/json',
            data: JSON.stringify({
                post_id: postId,
                reaction: action
            }),
            success: function (response) {
                if (response.success) {
                    $(`#likes-${postId}`).text(response.likes);
                    $(`#unlikes-${postId}`).text(response.unlikes);

                    if (action === 'like') {
                        $(`.react-btn[data-action="like"][data-id="${postId}"] i`)
                            .addClass('fas text-danger').removeClass('far');
                        $(`.react-btn[data-action="unlike"][data-id="${postId}"] i`)
                            .removeClass('fas').addClass('far');
                    } else {
                        $(`.react-btn[data-action="unlike"][data-id="${postId}"] i`)
                            .addClass('fas').removeClass('far');
                        $(`.react-btn[data-action="like"][data-id="${postId}"] i`)
                            .removeClass('fas').addClass('far text-danger');
                    }
                } else {
                    alert(response.error || "Reaction failed");
                }
            },
            error: function (xhr) {
                console.error("AJAX error", xhr.status, xhr.responseText);
                if (xhr.status === 403) {
                    alert("Login required to react.");
                    window.location.href = "/accounts/login/?next=" + window.location.pathname;
                } else {
                    alert("Error occurred. Try again later.");
                }
            },
            complete: function () {
                $button.prop('disabled', false);
            }
        });
    });
});
