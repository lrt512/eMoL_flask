/**
 * Global javascript definitions and snippets
 */
$(document).ready(function()
{
    "use strict";
    // Focus the first control with initial-focus class on the page
    $('.initial-focus').first().focus();
});

/**
 * Check of the given thing is defined, where defined means
 * not null and not undefined
 *
 * @param thing Thing to check
 * @returns {boolean} True if the thing is defined
 */
function is_defined(thing)
{
    "use strict";
    return null !== thing && undefined !== thing;
}

/**
 * Check of the given thing is defined and not empty, where defined
 * is as above and length is not zero
 *
 * @param thing Thing to check
 * @returns {boolean} True if the thing is defined and not empty
 */
function is_defined_not_empty(thing)
{
    "use strict";
    if (!is_defined(thing))
    {
        return false;
    }
    return 0 !== thing.length;
}