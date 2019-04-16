var userListSelector = '#user-list',
    userDetailFormSelector = '#user-detail-form',
    userDetailSelector = '#user-detail';

$(document).ready(function ()
{
    "use strict";

    var submitUserForm,
        dataTable = null;
    /*
     * Submit the form via AJAX and invoke a callback function on success
     * @param method {string} The HTTP method to use
     * @param callback {function} The callback function to call
     */
    submitUserForm = function (method, callback)
    {
        if (false === $(userDetailFormSelector).valid())
        {
            return;
        }
        console.info($(userDetailFormSelector).serialize())
        $.ajax({
            url: '/api/user',
            method: method,
            data: $(userDetailFormSelector).serialize(),
            success: function ()
            {
                callback();
            }
        });
    };

    /**
     * DataTables button definition for new user
     */
    $.fn.dataTable.ext.buttons.new_user = {
        text: 'New',
        action: function (e, dt, node, config)
        {
            $('#edit-form').load('/user-detail/new', function()
            {
                $(userDetailSelector).find('.btn-save').click(function ()
                {
                    submitUserForm('POST', function ()
                    {
                        $(userDetailSelector).modal('hide');
                        dataTable.ajax.reload(false);
                    });
                });

                $(userDetailSelector).find('.btn-cancel').click(function ()
                {
                    $(userDetailSelector).modal('hide');
                });
                $(userDetailSelector).one('hidden.bs.modal', function (event)
                {
                    $(userDetailSelector).remove();
                    dt.ajax.reload(false);
                });
                $(userDetailSelector).modal('show');
            });
        }
    };

    /**
     * Clicked edit for a user, load the modal.
     */
    $(userListSelector).on('click', '.btn-edit', function (evnt)
    {
        var tr = evnt.target.closest('tr'),
            row = dataTable.row(tr),
            key = row.data().key;

        $('#edit-form').load('/user-detail/' + key, function ()
        {
            $(userDetailSelector).find('.btn-save').click(function ()
            {
                submitUserForm('PUT', function ()
                {
                    $(userDetailSelector).modal('hide');
                    dataTable.ajax.reload(false);
                });
            });

            $(userDetailSelector).find('.btn-cancel').click(function ()
            {
                $(userDetailSelector).modal('hide');
            });
            $(userDetailSelector).one('hidden.bs.modal', function (event)
            {
                $(userDetailSelector).remove();
                dataTable.ajax.reload(false);
            });
            $(userDetailSelector).modal('show');
        });
    });

    /**
     * DataTable definition for the user list
     */
    dataTable = $(userListSelector).DataTable({
        dom: 'Bfrtip',
        ajax: '/api/user-list-datatable',
        columns: [
            {
                defaultContent: '<button type="button" class="btn btn-xs btn-ealdormere btn-edit">Edit</button>',
                orderable: false
            },
            {data: "email"},
            {data: "key", visible: false}
        ],
        responsive: false,
        buttons: ['new_user']
    });
});
