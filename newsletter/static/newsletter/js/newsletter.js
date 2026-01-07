console.log('newsletter js loaded');

$(document).on('submit', '#newsletter-form', function (e) {
    e.preventDefault();

    const form = $(this);

    $.ajax({
        type: 'POST',
        url: form.attr('action'),
        data: form.serialize(),
        success: function () {
            $('#newsletterConfirmationModal').modal('show');
            form[0].reset();
        },
        error: function () {
            alert('Subscription failed. Please try again.');
        }
    });
});
