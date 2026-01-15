$(document).ready(function () {

    /* ================= SAFETY CHECK ================= */
    if (typeof POST_REACTION_URL === "undefined") {
        console.warn("POST_REACTION_URL is not defined. Reactions disabled.");
        return;
    }

    /* ================= CSRF ================= */
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie) {
            document.cookie.split(";").forEach(function (cookie) {
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
    $(".react-btn").on("click", function () {

        const postId = $(this).data("id");
        const reaction = $(this).data("action");

        $.ajax({
            url: POST_REACTION_URL,
            type: "POST",
            contentType: "application/json",
            headers: {
                "X-CSRFToken": csrftoken,
            },
            data: JSON.stringify({
                post_id: postId,
                reaction: reaction,
            }),
            success: function (data) {
                if (data.success) {
                    $("#likes-" + postId).text(data.likes);
                    $("#unlikes-" + postId).text(data.unlikes);
                }
            },
            error: function (xhr) {
                console.error("Reaction error:", xhr.responseText);
            }
        });

    });

});
