/*
 Turn text into a slug.
 Shout out for saving me a bit of time:
 http://gist.github.com/mathewbyrne/1280286
 */

String.prototype.slugify = function()
{
    "use strict";

    return this.toString().toLowerCase()
        .replace(/\s+/g, '-')                   // Replace spaces with -
        .replace(/[\-+&@#\/%?=~|$!:,.;]+/g, '') // Remove all non-alpha chars
        .replace(/\-\-+/g, '-')                 // Replace multiple - with single -
        .replace(/^-+/, '')                     // Trim - from start of text
        .replace(/-+$/, '');                    // Trim - from end of text
};