/**
 *  jQuery plugin to populate a list of messages into an element
 *  Once loaded, dynamically set the message text from the given
 *  array of messages.
 *
 *  element can be a jQuery or DOM element
 *
 *  @param {string[]} messages Array of messages
 */
$.fn.show_messages = function(messages)
{
    "use strict";
    $(this).empty().load('/embed-message', function()
    {
        var $message_text = $('#message-text'),
            list = $('<ul style="list-style: none;">');

        $message_text.empty();
        $.each(messages, function(index, message)
        {
            try
            {
                var $message = $(message);
                if (0 === $message.length)
                {
                    list.append($('<li>').text(message));
                }
                else
                {
                    list.append($('<li>').append($message));
                }
            }
            catch(err)
            {
                // Sometimes $(message) throws an exception
                // on strings with punctuation
                list.append($('<li>').text(message));
            }
        });
        $message_text.append(list);
    });
};
