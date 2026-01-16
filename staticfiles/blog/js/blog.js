$(document).ready(function () {
    const POST_REACTION_URL = $('meta[name="reaction-url"]').attr("content");

    if (!POST_REACTION_URL) {
        console.warn("POST_REACTION_URL not found.");
        return;
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie) {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie("csrftoken");

    // AJAX handler
    $(document).on("click", ".react-btn", function () {
        const postId = $(this).data("id");
        const action = $(this).data("action");

        // Debug log
        console.log("Reaction clicked:", { postId, action });

        $.ajax({
            url: POST_REACTION_URL,
            method: "POST",
            headers: {
                "X-CSRFToken": csrftoken,
            },
            contentType: "application/json",
            data: JSON.stringify({
                post_id: postId,
                reaction: action,
            }),
            success: function (response) {
                if (response.success) {
                    $("#likes-" + postId).text(response.likes);
                    $("#unlikes-" + postId).text(response.unlikes);
                } else {
                    console.warn("Reaction failed:", response);
                }
            },
            error: function (xhr) {
                console.error("Reaction AJAX error:", xhr.status, xhr.responseText);
                if (xhr.status === 403 || xhr.status === 401) {
                    alert("You must be logged in to react.");
                }
            }
        });
    });
});
