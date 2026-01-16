$(function () {
    const POST_REACTION_URL = $('meta[name="reaction-url"]').attr('content');

    if (!POST_REACTION_URL) {
        console.warn('Reaction URL missing');
        return;
    }

    // Simple CSRF getter
    function getCookie(name) {
        const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
        return match ? decodeURIComponent(match[2]) : null;
    }

    const csrftoken = getCookie('csrftoken');

    if (!csrftoken) {
        console.warn('CSRF token not found');
    }

    // Use delegated event (important!)
    $(document).on('click', '.react-btn', function (e) {
        e.preventDefault();

        const $btn = $(this);

        // prevent double clicks
        if ($btn.data('loading')) return;
        $btn.data('loading', true);

        const postId = $btn.data('id');
        const action = $btn.data('action');

        console.log('React:', postId, action);

        $.ajax({
            url: POST_REACTION_URL,
            type: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            contentType: 'application/json',
            data: JSON.stringify({
                post_id: postId,
                reaction: action
            }),
            success: function (data) {
                if (data.success) {
                    $('#likes-' + postId).text(data.likes);
                    $('#unlikes-' + postId).text(data.unlikes);
                }
            },
            error: function (xhr) {
                console.error('Reaction failed:', xhr.status);

                // Heroku / Django login redirect
                if (xhr.status === 302 || xhr.status === 401) {
                    alert('Please log in to like or unlike.');
                }

                // CSRF rejection
                if (xhr.status === 403) {
                    alert('Security check failed. Refresh the page.');
                }
            },
            complete: function () {
                $btn.data('loading', false);
            }
        });
    });
});
