(function () {
    'use strict';

    $('#confirmModal').on('show.bs.modal', function (event) {
        const trigger = $(event.relatedTarget);

        const actions = {
            edit: {
                title: 'Confirm Edit',
                buttonText: 'Edit',
                buttonClass: 'btn-primary',
                messageSelector: '#editMessage'
            },
            delete: {
                title: 'Confirm Delete',
                buttonText: 'Delete',
                buttonClass: 'btn-danger',
                messageSelector: '#deleteMessage'
            }
        };

        const actionType = trigger.data('type');
        const actionUrl = trigger.data('action');
        const productName = trigger.data('name');
        const action = actions[actionType];

        if (!action) return;

        $('#confirmActionForm').attr('action', actionUrl);
        $('.item-name').text(productName);

        $('#deleteMessage, #editMessage').addClass('d-none');

        $('#confirmActionBtn')
            .removeClass('btn-primary btn-danger')
            .addClass(action.buttonClass)
            .text(action.buttonText);

        $('#confirmModalTitle').text(action.title);
        $(action.messageSelector).removeClass('d-none');
    });

})();
