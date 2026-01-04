document.addEventListener("DOMContentLoaded", function () {

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + "=")) {
                    cookieValue = decodeURIComponent(
                        cookie.substring(name.length + 1)
                    );
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie("csrftoken");

    document.querySelectorAll(".react-btn").forEach(button => {
        button.addEventListener("click", function () {

            const postId = this.dataset.id;
            const action = this.dataset.action;

            fetch(POST_REACTION_URL, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrftoken
                },
                body: JSON.stringify({
                    post_id: postId,
                    reaction: action
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error("Network response was not ok");
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    document.getElementById(`likes-${postId}`).innerText = data.likes;
                    document.getElementById(`unlikes-${postId}`).innerText = data.unlikes;
                }
            })
            .catch(error => {
                console.error("Reaction error:", error);
            });
        });
    });

});
