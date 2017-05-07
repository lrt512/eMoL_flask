(function ($) {
    "use strict";

    function save_button() {
        var uuid = $('#uuid').val();

        if (undefined === uuid || null === uuid || uuid.length == 0) {
            $('li.discipline-tab').addClass('hidden')
        }
        else {
            $('li.discipline-tab').removeClass('hidden')
            $('.btn-save').toggleClass('hidden', !$('#info-tab').hasClass('active'));
        }
    }

    $(document).ready(function () {
        var dataTable = null,
            combatant_list = $('#combatant-list');

        /**
         * Serialize the combatant detail form into a JavaScript object
         * instead of the nonsense jQuery's serialize/serializeArray gives
         */
        function serialize_form() {
            var form = $('#edit-combatant-form'),
                data = {};

            form.find('input').each(function (index, input) {
                data[$(input).attr('name')] = $(input).val();
            });

            return JSON.stringify(data);
        }

        /**
         * Submit the form via AJAX and invoke a callback function on success
         * @param method {string} The HTTP method to use
         * @param callback {function} The callback function to call
         */
        function submit_combatant(method, callback) {
            var form = $('#edit-combatant-form'),
                validation_error = $('#validation-error-notice');

            validation_error.hide();
            if (false === form.valid()) {
                validation_error.show();
                return;
            }

            var url = '/api/combatant/';
            if (method === 'PUT')
            {
                url += $('#uuid').val();
            }

            $.ajax({
                url: url,
                method: method,
                data: serialize_form(),
                dataType: 'json',
                contentType: 'application/json; charset=UTF-8',
                success: function (response, status, xhr) {
                    $('#uuid').val(xhr.responseJSON.uuid);
                    callback();
                }
            });
        }

        function selection_changed($option, selected) {
            var uuid = $('#uuid').val();

            if (undefined === uuid || null === uuid || uuid.length == 0) {
                return;
            }

            var type = $option.hasClass('combatant-auth') ? 'authorization' : 'warrant';

            var data = {
                discipline: $option.data('discipline'),
                slug: $option.val(),
                selected: selected
            }

            $.ajax({
                method: selected ? 'POST' : 'DELETE',
                url: '/api/combatant/' + uuid + '/' + type,
                dataType: 'json',
                contentType: 'application/json; charset=UTF-8',
                data: JSON.stringify(data),
                success: function (response) {

                }
            })
        }

        /**
         * DataTables button definition for new combatant
         */
        $.fn.dataTable.ext.buttons.new_combatant = {
            text: 'New',
            action: function (e, dt, node, config) {
                $('#edit-form').load('/combatant-detail/new', function () {
                    var combatant_detail = $('#combatant-detail');

                    combatant_detail.find('.btn-save').click(function () {
                        submit_combatant('POST', function () {
                            save_button();
                            dataTable.ajax.reload(false);
                        });
                    });

                    combatant_detail.find('.btn-close').click(function () {
                        combatant_detail.modal('hide');
                    });
                    combatant_detail.one('hidden.bs.modal', function (event) {
                        combatant_detail.remove();
                    });

                    $('#edit-combatant-form').validate({ignore: ''});
                    $('.picklist').bootstrapDualListbox({
                        moveOnSelect: true,
                        showFilterInputs: false,
                        infoText: false,
                        selectCallback: selection_changed
                    });
                    combatant_detail.modal('show');
                    save_button();
                });
            }
        };

        combatant_list.on('click', '.btn-edit', function (evnt) {
            var tr = evnt.target.closest('tr'),
                row = dataTable.row(tr),
                uuid = row.data().uuid;

            $('#edit-form').load('/combatant-detail/' + uuid, function () {
                var combatant_detail = $('#combatant-detail');

                combatant_detail.find('.btn-save').click(function () {
                    submit_combatant('PUT', function () {
                        save_button();
                        dataTable.ajax.reload(false);
                    });
                });

                combatant_detail.find('.btn-close').click(function () {
                    combatant_detail.modal('hide');
                });
                combatant_detail.one('hidden.bs.modal', function (event) {
                    combatant_detail.remove();
                });

                $('#edit-combatant-form').validate({ignore: ''});
                $('.picklist').bootstrapDualListbox({
                    moveOnSelect: true,
                    showFilterInputs: false,
                    infoText: false,
                    selectCallback: selection_changed
                });
                combatant_detail.modal('show');
                save_button();
            });
        });

        combatant_list.on('click', '.btn-delete', function (evnt) {
            var tr = evnt.target.closest('tr'),
                row = dataTable.row(tr),
                uuid = row.data().uuid,
                name = row.data().sca_name || row.data().legal_name;

            var confirm = window.confirm('Confirm delete: ' + name);
            if (confirm === false)
            {
                return;
            }

            $.ajax({
                url: '/api/combatant/' + uuid,
                method: 'DELETE',
                success: function()
                {
                    dataTable.ajax.reload(false);
                }
            });
        });

        dataTable = combatant_list.DataTable({
            dom: 'Bfrt',
            ajax: '/api/combatant-list-datatable',
            order: [1, 'asc'],
            scrollY: "300px",
            scrollX: false,
            scrollCollapse: true,
            paging: false,
            columns: [
                {
                    defaultContent: '<button type="button" title="Edit" class="btn btn-xs btn-primary btn-edit"><i style="margin-left:2px;" class="fa fa-pencil-square-o" aria-hidden="true"></i></button>',
                    orderable: false
                },
                {data: "sca_name"},
                {data: "legal_name"},
                {
                    data: "card_id",
                    render: function (data, type, full, meta) {
                        if (data) {
                            return data + '&nbsp;<button type="button" title="View card" class="btn btn-xs btn-primary btn-view-card"><i class="fa fa-eye" aria-hidden="true"></i></button>';
                        }
                        return '';
                    }
                },
                {
                    data: "accepted_privacy_policy",
                    width: "75px",
                    render: function (data, type, full, meta) {
                        if (true === data) {
                            return '<i class="fa fa-check fa-lg fg-green"></i>';
                        }
                        return '<i class="fa fa-close fa-lg fg-red"></i> <button type="button" title="Resend privacy policy" class="btn btn-xs btn-primary btn-resend-privacy"><i class="fa fa-repeat" aria-hidden="true"></i></button>';
                    }
                },
                {
                    defaultContent: '<button type="button" title="Delete" class="btn btn-xs btn-primary btn-delete"><i class="fa fa-trash-o" aria-hidden="true"></i></button>',
                    orderable: false
                },
                {data: "uuid", visible: false}
            ],
            responsive: false,
            buttons: ['new_combatant']
        });
    });

    $(document).on('change', '.picklist', function (event) {
        console.info($(this).attr('name'));
    });

    $(document).on('click', '.btn-resend-privacy', function () {
        var row = $(this).parents('tr'),
            data = $('#combatant-list').DataTable().row(row).data();

        $.ajax({
            method: 'POST',
            url: '/api/resend_privacy/' + data.uuid,
            type: 'json',
            success: function (response) {
                console.info(response);
            }
        });
    });

    $(document).on('click', '.btn-view-card', function () {
        var row = $(this).parents('tr'),
            data = $('#combatant-list').DataTable().row(row).data();

        var win = window.open('/card/' + data.card_id, '_blank');
        if (win) {
            win.focus();
        } else {
            //Browser has blocked it
            alert('Please allow popups for this website');
        }
    });

    $(document).on('shown.bs.tab', function () {
        save_button();
    });
}(jQuery));