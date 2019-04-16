/**
 * JavaScript for app setup pages.
 * TODO: Document this better.
 */
(function ($) {
    "use strict";

    $(document).on('change', '.btn-file :file', function () {
        var input = $(this),
            numFiles = input.get(0).files ? input.get(0).files.length : 1,
            label = input.val().replace(/\\/g, '/').replace(/.*\//, '');
        input.trigger('fileselect', [numFiles, label]);
    });

    $(document).ready(function () {
        var $form = $('#setup'),
            validator = $form.validate(),
            wizard = $('#rootwizard');

        $('.btn-file :file').on('fileselect', function (event, numFiles, label) {

            var input = $(this).parents('.input-group').find(':text'),
                log = numFiles > 1 ? numFiles + ' files selected' : label;

            if (input.length) {
                input.val(log);
            } else {
                if (log) alert(log);
            }

        });

        //noinspection JSLint,JSLint
        wizard.bootstrapWizard({
            onTabShow: function (tab, navigation, index) {
                var count = navigation.find('li').length,
                    current = index + 1,
                    rootwizard = $('#rootwizard');

                // If it's the last tab then hide the last button and show the finish instead
                if (current >= count) {
                    rootwizard.find('.pager .next').hide();
                    rootwizard.find('.pager .finish').show();
                    rootwizard.find('.pager .finish').removeClass('disabled');
                } else {
                    rootwizard.find('.pager .next').show();
                    rootwizard.find('.pager .finish').hide();
                }

                $('.previous').hide();
            },
            onTabClick: function (tab, navigation, index) {
                // Don't let the user click the tabs at the
                // top to change between steps
                return false;
            },
            onNext: function (tab, navigation, index) {
                var tab = $('.tab-pane:visible');
                var valid = true;
                $('input', tab).each(function (i, v) {
                    console.info(validator.element(v))
                    valid = validator.element(v) && valid;
                });

                if (!valid) {
                    validator.focusInvalid();
                    return false;
                }
            }
        });

        if ('False' === $('#config-test').val()) {
            $('.next').hide();
            throw 'Not finalizing initialization of page due to config test failure';
        }

        wizard.find('.finish').click(function () {
            $('#error-list').empty();
            $('#errors').addClass('hidden');

            $('#config_file').simpleUpload('/api/setup', {
                success: function (data) {
                    $('#setup').addClass('hidden');
                    $('#finished').removeClass('hidden');
                },
                error: function (error) {
                    $('#errors').removeClass('hidden');
                    $('#error-list')
                        .append($('<li>')
                            .text(error.xhr.responseJSON.message));
                }
            });
        });

        $('#disciplines-list-thing')
            .data('list-thing-add-callback', add_discipline_tab)
            .data('list-thing-remove-callback', remove_discipline_tab);

        $('[data-toggle="tooltip"]').tooltip();
    });
}(jQuery));
