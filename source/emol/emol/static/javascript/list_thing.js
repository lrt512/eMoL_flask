/**
 * JavaScript backing for list thing.
 *
 * If you don't have Bootstrap,
 *      .hidden {display: none;}
 * would be a good thing to have in your CSS
 *
 * In Jinja2:
 *
 *  With arrange buttons:
 *  <div id="admin-email-list-thing" class="list-thing">
 *      {% with list_thing_id="admin-list" %}
 *          {% include 'widgets/list_thing.html' %}
 *      {% endwith %}
 *  </div>
 *
 *  With no arrange buttons:
 *  <div id="admin-email-list-thing" class="list-thing">
 *      {% with list_thing_id="admin-list", arrange_buttons="hidden" %}
 *          {% include 'widgets/list_thing.html' %}
 *      {% endwith %}
 *  </div>
 *
 */
(function($)
{
    /**
     * Set the enable/disable state of the list thing
     * remove and arrange buttons.
     */
    var enable_buttons = function($container)
    {
        "use strict";

        // The selection
        var $selected = $container.find('option:selected');

        // No selection, no remove.
        if ($selected.length === 0)
        {
            $container.find('.btn-list-thing-remove').addClass('disabled')
        }
        else
        {
            $container.find('.btn-list-thing-remove').removeClass('disabled')
        }

        // Enable the down button if appropriate
        if ($container.find('option').length > 1
            && $selected.length > 0
            && !$selected.is($container.find('option:last')))
        {
            $container.find('.btn-list-thing-down').removeClass('disabled')
        }
        else
        {
            $container.find('.btn-list-thing-down').addClass('disabled')
        }

        // Enable the up button if appropriate
        if ($container.find('option').length > 1
            && $selected.length > 0
            && !$selected.is($container.find('option:first')))
        {
            $container.find('.btn-list-thing-up').removeClass('disabled')
        }
        else
        {
            $container.find('.btn-list-thing-up').addClass('disabled')
        }
    }

    /**
     * Add a new entry into the List Thing enclosing the
     * add button that was clicked
     */
    $(document).on('click', '.btn-list-thing-add', function(event)
    {
        "use strict";

        var $container = $(event.target).parents('.list-thing'),
            $input = $container.find('.list-thing-input'),
            $list = $container.find('.list-thing-list'),
            text = $input.val(),
            slug = text.slugify(),
            exists = false,
            callback;

        if (text.length === 0)
        {
            return;
        }

        $.each($list.find('option'), function()
        {
            if (text === $(this).text())
            {
                exists = true;
            }
        });

        if (exists === true)
        {
            return;
        }

        // See if there's an add callback for this instance
        callback = $container.data('list-thing-add-callback');
        if (callback !== null && callback !== void 0)
        {
            callback(text, slug);
        }

        $list.append($('<option>')
            .text(text)
            .val(slug));

        $input.val('').focus();
    });

    /**
     * Remove the currently selected entry from the List Thing
     * enclosing the remove button that was clicked
     */
    $(document).on('click', '.btn-list-thing-remove', function(event)
    {
        "use strict";

        var $container = $(event.target).parents('.list-thing'),
            $selected = $container.find('option:selected'),
            $next = $selected.next().length === 0 ? $selected.prev() : $selected.next(),
            callback;

        if ($selected.length === 0)
        {
            return;
        }

        // See if there's a remove callback for this instance
        callback = $container.data('list-thing-remove-callback');
        if (callback !== null && callback !== void 0)
        {
            callback($selected.text(), $selected.val());
        }

        $selected.remove();

        if ($container.find('option').length > 0)
        {
            // Still at least one sibling remaining
            $next.prop('selected', true);
        }
        else
        {
            // If our select is empty, who knows what $next is pointing at,
            // so just focus the input again
            $container.find('.list-thing-input').focus();
        }

        enable_buttons($container);
    });

    /**
     * Move the currently selected entry up
     */
    $(document).on('click', '.btn-list-thing-up', function(event)
    {
        "use strict";

        var $container = $(event.target).parents('.list-thing'),
            $selected = $container.find('option:selected');

        if ($selected.length === 0)
        {
            return;
        }

        $selected.insertBefore($selected.prev());
        enable_buttons($container);
    });

    /**
     * Move the currently selected entry down
     */
    $(document).on('click', '.btn-list-thing-down', function(event)
    {
        "use strict";

        var $container = $(event.target).parents('.list-thing'),
            $selected = $container.find('option:selected');

        if ($selected.length === 0)
        {
            return;
        }

        $selected.insertAfter($selected.next());
        enable_buttons($container);
    });

    // Set button states when the list selection changes
    $(document).on('change', '.list-thing-list', function(event)
    {
        var $container = $(event.target).parents('.list-thing');
        enable_buttons($container);
    });

}(jQuery));