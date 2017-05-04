var officerListSelector = '#officer-list',
    officerDetailFormSelector = '#officer-detail-form',
    officerDetailSelector = '#officer-detail';

$(document).ready(function ()
{
    "use strict";

    var submitOfficerForm,
        dataTable = null;
    
    /*
     * Submit the form via AJAX and invoke a callback function on success
     * @param method {string} The HTTP method to use
     * @param callback {function} The callback function to call
     */
    submitOfficerForm = function (method, callback)
    {
        if (false === $(officerDetailFormSelector).valid())
        {
            return;
        }

        $.ajax({
            url: '/api/officer',
            method: method,
            data: $(officerDetailFormSelector).serialize(),
            success: function ()
            {
                callback();
            }
        });
    };

    /**
     * DataTables button definition for new officer
     */
    $.fn.dataTable.ext.buttons.new_officer = {
        text: 'New',
        action: function (e, dt, node, config)
        {
            $('#edit-form').load('/officer-detail/new', function()
            {
                $(officerDetailSelector).find('.btn-save').click(function ()
                {
                    submitOfficerForm('POST', function ()
                    {
                        $(officerDetailSelector).modal('hide');
                        dataTable.ajax.reload(false);
                    });
                });

                $(officerDetailSelector).find('.btn-cancel').click(function ()
                {
                    $(officerDetailSelector).modal('hide');
                });
                $(officerDetailSelector).one('hidden.bs.modal', function (event)
                {
                    $(officerDetailSelector).remove();
                    dt.ajax.reload(false);
                });
                $(officerDetailSelector).modal('show');
            });
        }
    };

    $(officerListSelector).on('click', '.btn-edit', function (evnt)
    {
        var tr = evnt.target.closest('tr'),
            row = dataTable.row(tr),
            key = row.data().key;

        $('#edit-form').load('/officer-detail/' + key, function ()
        {
            $(officerDetailSelector).find('.btn-save').click(function ()
            {
                submitOfficerForm('PUT', function ()
                {
                    $(officerDetailSelector).modal('hide');
                    dataTable.ajax.reload(false);
                });
            });

            $(officerDetailSelector).find('.btn-cancel').click(function ()
            {
                $(officerDetailSelector).modal('hide');
            });
            $(officerDetailSelector).one('hidden.bs.modal', function (event)
            {
                $(officerDetailSelector).remove();
                dataTable.ajax.reload(false);
            });
            $(officerDetailSelector).modal('show');
        });
    });

    dataTable = $(officerListSelector).DataTable({
        dom: 'Bfrtip',
        ajax: '/api/officer-list-datatable',
        columns: [
            {
                defaultContent: '<button type="button" class="btn btn-xs btn-ealdormere btn-edit">Edit</button>',
                orderable: false
            },
            {data: "title"},
            {data: "email"},
            {data: "name"},
            {data: "key", visible: false}
        ],
        responsive: false,
        buttons: ['new_officer']
    });
});
