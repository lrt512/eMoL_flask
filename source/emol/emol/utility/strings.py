# -*- coding: utf-8 -*-
"""String utility functions."""


def tokenize(phrase):
    """Tokenize to substrings on spaces."""
    substrings = []
    for word in phrase.split():
        j = 1
        while True:
            for i in range(len(word) - j + 1):
                substrings.append(word[i:i + j])
            if j == len(word):
                break
            j += 1
    return substrings
