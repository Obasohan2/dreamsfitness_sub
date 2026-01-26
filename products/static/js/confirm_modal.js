(function () {
    'use strict';

    $('#confirmModal').on('show.bs.modal', function (event) {
        const trigger = $(event.relatedTarget);

        const actions = {
            edit: {
                title: 'Confirm Edit',
                buttonText: 'Edit',
                buttonClass: 'btn-primary',
                messageSelector: '#editMessage',
                method: 'GET'
            },
            delete: {
                title: 'Confirm Delete',
                buttonText: 'Delete',
                buttonClass: 'btn-danger',
                messageSelector: '#deleteMessage',
                method: 'POST'
            }
        };

        const actionType = trigger.data('type');
        const actionUrl = trigger.data('action');
        const productName = trigger.data('name');
        const action = actions[actionType];

        if (!action) return;

        // Inject product name
        $('.item-name').text(productName);

        // Reset state
        $('#deleteMessage, #editMessage').addClass('d-none');

        const confirmBtn = $('#confirmActionBtn');
        const form = $('#confirmActionForm');

        confirmBtn
            .removeClass('btn-primary btn-danger')
            .addClass(action.buttonClass)
            .text(action.buttonText)
            .off('click');

        $('#confirmModalTitle').text(action.title);
        $(action.messageSelector).removeClass('d-none');

        if (action.method === 'POST') {
            // DELETE → submit form
            form.attr('action', actionUrl);
            form.attr('method', 'POST');
            confirmBtn.on('click', function () {
                form.submit();
            });
        } else {
            // EDIT → redirect (NO SUBMIT)
            form.removeAttr('action');
            confirmBtn.on('click', function () {
                window.location.href = actionUrl;
            });
        }
    });

})();
