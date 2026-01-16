$(document).ready(function () {
    
    // Try multiple ways to get the URL
    let reactionUrl = $('meta[name="reaction-url"]').attr("content");
    
    if (!reactionUrl) {
        // Fallback: construct URL manually
        reactionUrl = window.location.origin + '/blog/post-reaction/';
        console.log("Using fallback URL:", reactionUrl);
    } else {
        console.log("Using meta URL:", reactionUrl);
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
    console.log("CSRF token available:", !!csrftoken);

    // Like / Unlike AJAX
    $(document).on("click", ".react-btn", function (e) {
        e.preventDefault();
        console.log("Reaction button clicked");
        
        const postId = $(this).data("id");
        const action = $(this).data("action");
        
        console.log("Post ID:", postId, "Action:", action);
        
        if (!postId || !action) {
            console.error("Missing data attributes");
            return;
        }

        // Show loading state
        const $button = $(this);
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
                console.log("AJAX Success:", response);
                
                // Restore button
                $button.html(originalHTML).prop('disabled', false);
                
                if (response.success) {
                    // Update counts
                    $(`#likes-${postId}`).text(response.likes);
                    $(`#unlikes-${postId}`).text(response.unlikes);
                    
                    // Visual feedback
                    if (action === 'like') {
                        $button.find('i').removeClass('far text-secondary').addClass('fas text-danger');
                        $(`.react-btn[data-action="unlike"][data-id="${postId}"]`)
                            .find('i').removeClass('fas text-secondary').addClass('far text-secondary');
                    } else if (action === 'unlike') {
                        $button.find('i').removeClass('far text-danger').addClass('fas text-secondary');
                        $(`.react-btn[data-action="like"][data-id="${postId}"]`)
                            .find('i').removeClass('fas text-danger').addClass('far text-danger');
                    }
                    
                    // Show success message briefly
                    const originalText = $button.find('span').text();
                    $button.find('span').text('✓');
                    setTimeout(() => {
                        $button.find('span').text(originalText);
                    }, 500);
                } else {
                    console.warn("Server returned success: false", response);
                    if (response.error) {
                        alert("Error: " + response.error);
                    }
                }
            },
            error: function (xhr, status, error) {
                console.error("AJAX Error:", {
                    status: xhr.status,
                    statusText: xhr.statusText,
                    responseText: xhr.responseText,
                    error: error
                });
                
                // Restore button
                $button.html(originalHTML).prop('disabled', false);
                
                if (xhr.status === 403) {
                    alert("Please login to react to posts.");
                    window.location.href = '/accounts/login/?next=' + window.location.pathname;
                } else if (xhr.status === 404) {
                    alert("Post not found or reaction URL incorrect.");
                } else if (xhr.status === 500) {
                    alert("Server error. Please try again later.");
                } else {
                    alert("Error: " + error);
                }
            }
        });
    });
    
    console.log("Reaction handler registered");
});