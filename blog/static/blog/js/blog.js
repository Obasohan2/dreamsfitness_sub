$(document).ready(function () {

    console.log("blog.js loaded");

    const reactionUrl = $('meta[name="reaction-url"]').attr("content");

    if (!reactionUrl) {
        console.warn("Reaction URL not found.");
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

    // Like / Unlike AJAX
    $(document).on("click", ".react-btn", function () {
        const postId = $(this).data("id");
        const action = $(this).data("action");

        $.ajax({
            url: reactionUrl,
            method: "POST",
            headers: {
                'X-CSRFToken': csrftoken
            },
            contentType: "application/json",
            data: JSON.stringify({
                post_id: postId,
                reaction: action
            }),
            success: function (response) {
                if (response.success) {
                    $(`#likes-${postId}`).text(response.likes);
                    $(`#unlikes-${postId}`).text(response.unlikes);
                } else {
                    console.warn("Server responded with failure:", response);
                }
            },
            error: function (xhr) {
                if (xhr.status === 403) {
                    alert("Login required to react.");
                } else {
                    console.error("AJAX error:", xhr.status, xhr.responseText);
                }
            }
        });
    });
});
