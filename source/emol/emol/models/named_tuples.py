# standard library imports
from collections import namedtuple


# Named tuple for the common name/slug pattern throughout the application
NameSlugTuple = namedtuple('NameSlugTuple', ['name', 'slug'])

# Named tuple for a role
RoleTuple = namedtuple('NameSlugTuple', ['name', 'slug', 'is_global'])
