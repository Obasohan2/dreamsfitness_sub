/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment

    CSS from here: 
    https://stripe.com/docs/stripe-js
*/

var stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
var clientSecret = $('#id_client_secret').text().slice(1, -1);

var stripe = Stripe(stripePublicKey);
var elements = stripe.elements();

var style = {
    base: {
        color: '#000',
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSize: '16px',
        '::placeholder': { color: '#aab7c4' }
    },
    invalid: {
        color: '#dc3545',
        iconColor: '#dc3545'
    }
};

var card = elements.create('card', { style: style });
card.mount('#card-element');

/* ----------------------------
   CARD VALIDATION ERRORS
----------------------------- */
card.on('change', function (event) {
    var errorDiv = $('#card-errors');
    if (event.error) {
        errorDiv.html(`
            <span class="icon" role="alert"><i class="fas fa-times text-danger"></i></span>
            <span>${event.error.message}</span>
        `);
    } else {
        errorDiv.text('');
    }
});

/* ----------------------------
   FORM SUBMISSION
----------------------------- */
var form = document.getElementById('payment-form');

form.addEventListener('submit', function (ev) {
    ev.preventDefault();

    /* Disable UI */
    card.update({ disabled: true });
    $('#submit-button').attr('disabled', true);
    $('#payment-form').fadeToggle(100);
    $('#loading-overlay').fadeToggle(100);

    /* Save Info */
    var saveInfo = $('#save-info').prop('checked');

    /* Meta data post */
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
    var postData = {
        csrfmiddlewaretoken: csrfToken,
        client_secret: clientSecret,
        save_info: saveInfo,
    };

    $.post('/checkout/cache_checkout_data/', postData).done(function () {

        /* ----------------------------
           SHIPPING vs BILLING LOGIC
        ----------------------------- */

        var useDifferentShipping = $('#use-different-shipping').prop('checked');

        // BILLING ADDRESS
        var billing = {
            name: form.full_name.value.trim(),
            phone: form.phone_number.value.trim(),
            email: form.email.value.trim(),
            address: {
                line1: form.address1.value.trim(),
                line2: form.address2.value.trim(),
                city: form.city.value.trim(),
                postal_code: form.postcode.value.trim(),
                country: form.country.value.trim(),
            }
        };

        // SHIPPING ADDRESS (Fallback to billing if not selected)
        var shipping = {
            name: form.full_name.value.trim(),
            phone: form.phone_number.value.trim(),
            address: {
                line1: useDifferentShipping ? form.shipping_address1.value.trim() : form.address1.value.trim(),
                line2: useDifferentShipping ? form.shipping_address2.value.trim() : form.address2.value.trim(),
                city: useDifferentShipping ? form.shipping_city.value.trim() : form.city.value.trim(),
                postal_code: useDifferentShipping ? form.shipping_postcode.value.trim() : form.postcode.value.trim(),
                country: useDifferentShipping ? form.shipping_country.value.trim() : form.country.value.trim(),
            }
        };

        /* ----------------------------
           STRIPE PAYMENT CONFIRMATION
        ----------------------------- */
        stripe.confirmCardPayment(clientSecret, {
            payment_method: {
                card: card,
                billing_details: billing
            },
            shipping: shipping
        }).then(function (result) {

            if (result.error) {
                /* Show error */
                $('#card-errors').html(`
                    <span class="icon" role="alert"><i class="fas fa-times text-danger"></i></span>
                    <span>${result.error.message}</span>
                `);

                /* Re-enable UI */
                $('#payment-form').fadeToggle(100);
                $('#loading-overlay').fadeToggle(100);
                card.update({ disabled: false });
                $('#submit-button').attr('disabled', false);

            } else {
                if (result.paymentIntent.status === 'succeeded') {
                    form.submit();
                }
            }

        });

    }).fail(function () {
        location.reload(); // fallback; errors appear via Django messages
    });

});
