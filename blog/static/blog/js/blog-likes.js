document.addEventListener("DOMContentLoaded", function () {

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    document.querySelectorAll(".react-btn").forEach(btn => {
        btn.addEventListener("click", function () {
            const url = this.dataset.url;
            const postId = this.dataset.postId;

            fetch(url, {
                method: "POST",
                credentials: "same-origin",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                    "X-Requested-With": "XMLHttpRequest",
                },
            })
            .then(res => {
                // If user is logged out, Django may redirect to login (302)
                if (res.redirected) {
                    window.location.href = res.url;
                    return null;
                }
                return res.json();
            })
            .then(data => {
                if (!data) return;

                const likesEl = document.getElementById(`likes-count-${postId}`);
                const unlikesEl = document.getElementById(`unlikes-count-${postId}`);

                if (likesEl) likesEl.innerText = data.likes_count;
                if (unlikesEl) unlikesEl.innerText = data.unlikes_count;
            })
            .catch(err => console.error("Reaction error:", err));
        });
    });

});