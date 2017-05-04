(function($)
{
    "use strict";

    function serialize_form()
    {
        var data = {
            encryption_key: $('#encryption_key').val(),
            global_waiver_date: $('#global-waiver-date').is(':checked'),
            global_card_date: $('#global-card-date').is(':checked'),
            admin_emails: [],
            disciplines: []
        };

        $.each($('#admin-list').find('> option'), function()
        {
            data.admin_emails.push($(this).text());
        });

        $.each($('#discipline-list').find('> option'), function()
        {
            var slug = $(this).val(),
                discData = {
                    name: $(this).text(),
                    slug: slug,
                    authorizations: {},
                    marshals: {}
                };

            $.each($('#' + slug + '-authorizations > option'), function()
            {
                discData.authorizations[$(this).val()] = $(this).text();
            });
            $.each($('#' + slug + '-marshals > option'), function()
            {
                discData.marshals[$(this).val()] = $(this).text();
            });
            data.disciplines.push(discData);
        });

        return data;
    }

    /**
     * List Thing callback for add action
     * Creates a tab for a new discipline and adds it
     * @param name
     * @param slug
     */
    function add_discipline_tab(name, slug)
    {
        var li = $('<li>')
            .attr('id', slug + 'tab-nav')
            .append($('<a>')
                .attr('href', '#' + slug + '-tab')
                .attr('data-toggle', 'tab')
                .text(name)
            ),
            tab = $('#discipline-tab-template')
                .clone()
                .attr('id', slug + '-tab')
                .removeClass('hidden');

        $('#discipline-nav').append(li);
        $('#discipline-tabs').append(tab);

        tab.find('.authorizations').find('select').attr('id', slug + '-authorizations');
        tab.find('.marshals').find('select').attr('id', slug + '-marshals');
    }

    /**
     * List Thing callback for remove action.
     * Removes the selected tab from the disciplines
     * @param name
     * @param slug
     */
    function remove_discipline_tab(name, slug)
    {
        $('#' + slug + '-tab').remove();
        $('#' + slug + 'tab-nav').remove();
    }

    $(document).ready(function()
    {
        var $form = $('#setup'),
            validator = $form.validate(),
            wizard = $('#rootwizard');

        $.validator.addMethod('hasone', function(value, element, param)
        {
            return 0 < $(element).find('option').length;
        }, 'Add at least one admin account');

        //noinspection JSLint,JSLint
        wizard.bootstrapWizard({
            onTabShow: function(tab, navigation, index)
            {
                var count = navigation.find('li').length,
                    current = index + 1,
                    rootwizard = $('#rootwizard');

                // If it's the last tab then hide the last button and show the finish instead
                if (current >= count)
                {
                    rootwizard.find('.pager .next').hide();
                    rootwizard.find('.pager .finish').show();
                    rootwizard.find('.pager .finish').removeClass('disabled');
                } else
                {
                    rootwizard.find('.pager .next').show();
                    rootwizard.find('.pager .finish').hide();
                }

                if (0 === index)
                {
                    $('.previous').hide();
                }
                else
                {
                    $('.previous').show();
                }
            },
            onTabClick: function(tab, navigation, index)
            {
                // Don't let the user click the tabs at the
                // top to change between steps
                return false;
            },
            onNext: function(tab, navigation, index)
            {
                var tab = $('.tab-pane:visible');
                var valid = true;
                $('input', tab).each(function(i, v)
                {
                    console.info(validator.element(v))
                    valid = validator.element(v) && valid;
                });

                if (!valid)
                {
                    validator.focusInvalid();
                    return false;
                }
            }
        });

        if ('False' === $('#config-test').val())
        {
            $('.next').hide();
            throw 'Not finalizing initialization of page due to config test failure';
        }

        wizard.find('.finish').click(function()
        {
            var valid = $form.valid();
            if (!valid)
            {
                validator.focusInvalid();
                return false;
            }
            $('#error-list').empty();
            $('#errors').addClass('hidden');

            $.ajax({
                method: 'POST',
                url: '/api/setup',
                data: JSON.stringify(serialize_form()),
                contentType: 'application/json;charset=utf-8',
                dataType: 'json',
                success: function()
                {
                    $('#setup').addClass('hidden');
                    $('#finished').removeClass('hidden');
                },
                error: function(xhr)
                {
                    $('#errors').removeClass('hidden');
                    $('#error-list')
                        .append($('<li>')
                        .text(xhr.responseJSON.message));
                }
            });
        });

        $('#disciplines-list-thing')
            .data('list-thing-add-callback', add_discipline_tab)
            .data('list-thing-remove-callback', remove_discipline_tab);

        $('[data-toggle="tooltip"]').tooltip();
    });
}(jQuery));
