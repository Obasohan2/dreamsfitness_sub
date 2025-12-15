/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment

    CSS from here: 
    https://stripe.com/docs/stripe-js
*/

/*
    Stripe payment flow
    https://stripe.com/docs/payments/accept-a-payment
*/

/* ----------------------------------------
   STRIPE SETUP
----------------------------------------- */
const stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
const clientSecret = $('#id_client_secret').text().slice(1, -1);

const stripe = Stripe(stripePublicKey);
const elements = stripe.elements();

const style = {
    base: {
        color: '#000',
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        '::placeholder': { color: '#aab7c4' }
    },
    invalid: {
        color: '#dc3545',
        iconColor: '#dc3545'
    }
};

const card = elements.create('card', { style });
card.mount('#card-element');

/* ----------------------------------------
   CARD VALIDATION
----------------------------------------- */
card.on('change', function (event) {
    const errorDiv = $('#card-errors');
    if (event.error) {
        errorDiv.html(`
            <span class="icon" role="alert">
                <i class="fas fa-times text-danger"></i>
            </span>
            <span>${event.error.message}</span>
        `);
    } else {
        errorDiv.text('');
    }
});

/* ----------------------------------------
   SHIPPING TOGGLE (CRITICAL FIX)
----------------------------------------- */
document.addEventListener("DOMContentLoaded", function () {
    const toggle = document.getElementById("use-different-shipping");
    const shipping = document.getElementById("shipping-fields");
    const shippingInputs = shipping.querySelectorAll("input, select");

    function toggleShippingFields() {
        if (toggle.checked) {
            shipping.classList.remove("d-none");
            shippingInputs.forEach(field => field.disabled = false);
        } else {
            shipping.classList.add("d-none");
            shippingInputs.forEach(field => field.disabled = true);
        }
    }

    toggle.addEventListener("change", toggleShippingFields);
    toggleShippingFields(); // run on page load
});

/* ----------------------------------------
   FORM SUBMISSION
----------------------------------------- */
const form = document.getElementById('payment-form');
const overlay = $('#loading-overlay');

form.addEventListener('submit', function (ev) {
    ev.preventDefault();

    /* Disable UI */
    card.update({ disabled: true });
    $('#submit-button').attr('disabled', true);
    $('#payment-form').hide();
    overlay.show();

    /* Save profile info */
    const saveInfo = $('#save-info').prop('checked');

    /* Cache checkout data */
    const csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
    const postData = {
        csrfmiddlewaretoken: csrfToken,
        client_secret: clientSecret,
        save_info: saveInfo,
    };

    $.post(cacheCheckoutUrl, postData).done(function () {

        const useDifferentShipping = $('#use-different-shipping').prop('checked');

        /* Billing details */
        const billing = {
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

        /* Shipping details */
        const shippingAddress = useDifferentShipping ? {
            line1: form.shipping_address1.value.trim(),
            line2: form.shipping_address2.value.trim(),
            city: form.shipping_city.value.trim(),
            postal_code: form.shipping_postcode.value.trim(),
            country: form.shipping_country.value.trim(),
        } : {
            line1: form.address1.value.trim(),
            line2: form.address2.value.trim(),
            city: form.city.value.trim(),
            postal_code: form.postcode.value.trim(),
            country: form.country.value.trim(),
        };

        stripe.confirmCardPayment(clientSecret, {
            payment_method: {
                card: card,
                billing_details: billing
            },
            shipping: {
                name: billing.name,
                phone: billing.phone,
                address: shippingAddress
            }
        }).then(function (result) {

            if (result.error) {
                $('#card-errors').html(`
                    <span class="icon" role="alert">
                        <i class="fas fa-times text-danger"></i>
                    </span>
                    <span>${result.error.message}</span>
                `);

                /* Re-enable UI */
                $('#payment-form').show();
                overlay.hide();
                card.update({ disabled: false });
                $('#submit-button').attr('disabled', false);

            } else if (result.paymentIntent.status === 'succeeded') {
                form.submit();
                return;
            }

        });

    }).fail(function () {
        location.reload();
    });
});



/*

var stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
var clientSecret = $('#id_client_secret').text().slice(1, -1);
var stripe = Stripe(stripePublicKey);
var elements = stripe.elements();
var style = {
    base: {
        color: '#000',
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        '::placeholder': {
            color: '#aab7c4'
        }
    },
    invalid: {
        color: '#dc3545',
        iconColor: '#dc3545'
    }
};
var card = elements.create('card', {style: style});
card.mount('#card-element');

// Handle realtime validation errors on the card element
card.addEventListener('change', function (event) {
    var errorDiv = document.getElementById('card-errors');
    if (event.error) {
        var html = `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>${event.error.message}</span>
        `;
        $(errorDiv).html(html);
    } else {
        errorDiv.textContent = '';
    }
});

// Handle form submit
var form = document.getElementById('payment-form');

form.addEventListener('submit', function(ev) {
    ev.preventDefault();
    card.update({ 'disabled': true});
    $('#submit-button').attr('disabled', true);
    $('#payment-form').fadeToggle(100);
    $('#loading-overlay').fadeToggle(100);

    var saveInfo = Boolean($('#id-save-info').attr('checked'));
    // From using {% csrf_token %} in the form
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
    var postData = {
        'csrfmiddlewaretoken': csrfToken,
        'client_secret': clientSecret,
        'save_info': saveInfo,
    };
    var url = '/checkout/cache_checkout_data/';

    $.post(url, postData).done(function () {
        stripe.confirmCardPayment(clientSecret, {
            payment_method: {
                card: card,
                billing_details: {
                    name: $.trim(form.full_name.value),
                    phone: $.trim(form.phone_number.value),
                    email: $.trim(form.email.value),
                    address:{
                        line1: $.trim(form.street_address1.value),
                        line2: $.trim(form.street_address2.value),
                        city: $.trim(form.town_or_city.value),
                        country: $.trim(form.country.value),
                    }
                }
            },
            shipping: {
                name: $.trim(form.full_name.value),
                phone: $.trim(form.phone_number.value),
                address: {
                    line1: $.trim(form.street_address1.value),
                    line2: $.trim(form.street_address2.value),
                    city: $.trim(form.town_or_city.value),
                    country: $.trim(form.country.value),
                    postal_code: $.trim(form.postcode.value),
                }
            },
        }).then(function(result) {
            if (result.error) {
                var errorDiv = document.getElementById('card-errors');
                var html = `
                    <span class="icon" role="alert">
                    <i class="fas fa-times"></i>
                    </span>
                    <span>${result.error.message}</span>`;
                $(errorDiv).html(html);
                $('#payment-form').fadeToggle(100);
                $('#loading-overlay').fadeToggle(100);
                card.update({ 'disabled': false});
                $('#submit-button').attr('disabled', false);
            } else {
                if (result.paymentIntent.status === 'succeeded') {
                    form.submit();
                }
            }
        });
    }).fail(function () {
        // just reload the page, the error will be in django messages
        location.reload();
    })
});

*/