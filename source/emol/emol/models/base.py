# -*- coding: utf-8 -*-
"""Base database model."""

# stdlib imports
from datetime import datetime, date


# app imports


class BaseMixin(object):
    """Base model class where we can place common properties and methods."""

    ######################################################################
    # Updating attrbutes - the following special attributes control
    # behaviour of the create() and update() methods.  Typically, any
    # attribute that is not a defined column (or settable property, see
    # __update_props__, below) will raise an AttributeError by these
    # methods.  When listing attribute names, you do NOT have to list
    # columns or props that begin with a leading underscore: these
    # attributes are ignored by create() and update(). Also, the "id"
    # attribute is handled specially and should not be referenced
    # here. Most of these attributes must be sets and the following
    # property must be true:
    #
    #  False == bool(__update_never__
    #                & __update_on_create__
    #                & __update_ignore__)
    #
    ###################################

    # a set of attributes that should never be updated via the update()
    # or create() methods, raising AttributeError if attempting to set
    # them.
    __update_never__ = set()

    # like __update_never__, but allow these attributes to be set with
    # create(), rendering them read-only thereafter.
    __update_on_create__ = set()

    # set of attribute names which will be ignored, as if they were not
    # passed to create() or update(). A convenience to allow attributes
    # to be passed in that you never want updated.  E.g, the
    # modification timestamp on most models is a good candidate here.
    __update_ignore__ = {'timestamp'}


    ######################################################################
    # JSON control attributes.  To control serialization of a model
    # instance you can specify what Column attributes to include or
    # exclude.  Additionally, you can specify any arbitrary attribute
    # or callable output as extra data to be included in the
    # serialization.  If the following attributes are empty sets for an
    # instance, the default serialization is every Column attribute and
    # hybrid_property whose name is not prefixed with an underscore.
    #
    # Includes/excludes for json serialization: __json_includes__
    # specifies what to include (default: all, if empty),
    # __json_excludes__ specifies what to exclude (default: none, if
    # empty).  The intersection of includes/excludes must be empty.
    # These MUST BE sets that include names of attributes that are
    # Columns.  Note: columns that are prefixed with an underscore are
    # automatically excluded and do not need to be added to
    # __json_excludes__.
    __json_includes__ = set()
    __json_excludes__ = set()
    # Extras: __json_extras__ defines properties/attributes that are
    # not Columns to be included in the serialization output.  MUST BE
    # a set.  The set may include a tuple, (alias, attr), where attr is
    # one of: 1) the property/attribute name to be serialized under key
    # alias, or 2) a callable to be called with a single parameter, the
    # model instance being serialized, the return value of which will
    # be stored under alias.
    __json_extras__ = set()

    #
    ######################################################################


    @property
    def columns(self):
        '''The set of all column names.

        This property will return a set(), including the names of all
        ORM columns (the attribute names, not the table column names),
        including hybrid properties.

        This will NOT return names that begin with an underscore.
        '''

        mapper = inspect(self).mapper
        columns = set([name for name in mapper.all_orm_descriptors.keys()
                       if (not name.startswith('_')
                           and (name in mapper.column_attrs
                                or type(
                mapper.all_orm_descriptors[name]) == hybrid_property))])
        return columns

    @property
    def schema(self):
        '''Return OAI (swagger) schema for the instance.

        Returns - dict, which can be converted to json.
        '''

        cls = self.__class__
        properties = {}
        mapper = inspect(self).mapper

        # iterate over all known columns and hybrid properties
        for name in self.columns:

            try:
                try:
                    col = getattr(mapper.columns, name)
                    schema = Schema.column_to_schema(col)
                    if schema is None:
                        raise exceptions.IncompleteSchemaDef(name)
                except AttributeError:
                    # not a Column, then must be a property with "_schema" attribute
                    schema = getattr(cls, name)._schema
            except AttributeError:
                raise exceptions.IncompleteSchemaDef(name)

            properties[name] = schema

        return dict(type="object", properties=properties)

    def __json__(self, req):
        '''custom jsonification

        see: http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/renderers.html#using-a-custom-json-method
        '''

        return self.serialize(includes=self.__json_includes__,
                              excludes=self.__json_excludes__,
                              extras=self.__json_extras__)

    def _serialize_attr(self, attrname):
        'Lookup value under attrname and return a JSON-friendly representation'

        val = getattr(self, attrname)

        # special consideration for types should be handled
        # here...

        if isinstance(val, datetime):
            # datetime: milliseconds since the epoch
            val = int((val - EPOCH).total_seconds() * 1000)
        elif isinstance(val, date):
            # Dec 31, 1899 is a value used in some data to represent null (or zero)
            if val == DEC31_1899:
                val = None
            else:
                # date: string, YYYYMMDD
                val = val.strftime('%Y%m%d')
        elif isinstance(val, set):
            # set => list
            val = list(val)
        elif isinstance(val, str):
            # LOTS of columns are CHAR(N), returning fixed-length, padded strings.  Ugh!
            val = val.strip()

        return val

    def set_serialization(self, merge=False, **kw):
        '''set custom serialization

        See comments above for __json_*__ attributes for setting default
        serialization for a Model.  This method will set each of these
        __json_*__ variables for the instance.  The keyword arguments
        must be one or more of "includes", "excludes", or "extras".

        If merge is True, values will be merged via the set union
        operator, eg, with:

            obj.set_serialization(merge=True, includes=someset)

        then the resulting value of obj.__json_includes__ will be:

            obj.__json_includes__ | includes

        '''

        for k, v in kw.items():

            # will raise an Attribute error if not one of the known,
            # defined __json_*__ "control" attributes
            attrname = '__json_{}__'.format(k)
            s = getattr(self, attrname).copy()

            if not merge:
                s.clear()

            s |= v

            # set the new set on the instance
            setattr(self, attrname, s)

        return self

    def serialize(self, includes=None, excludes=None, extras=None):
        '''custom serialization, converting instance to dict for JSON

        See comments above for __json_*__ attributes for setting default
        serialization for a Model for use with __json__().
        '''

        includes = includes or set()
        excludes = excludes or set()
        extras = extras or set()

        assert not (includes & excludes), \
            'Programming Error: __json_includes__ and __json_excludes must not interset'

        obj = {}
        mapper = inspect(self).mapper
        # all columns and hybrid properties
        for name in self.columns:

            # consider includes
            if not includes or name in includes:
                # consider excludes
                if not excludes or name not in excludes:
                    obj[name] = self._serialize_attr(name)

        for attr in extras:
            # alias given?
            if isinstance(attr, tuple):
                name, attr = attr
            else:
                name = attr

            obj[name] = attr(self) if callable(attr) else self._serialize_attr(
                attr)

        return obj

    @classmethod
    def count(cls, *filters, cols=None, select_from=None):
        '''Return the count of intstances for this class.

        Args -

           *filters -    filters to apply as with Query.filter() (see SQLA docs)
           cols -        if not None, a column or tuple of columns to use in
                         func.count(), default is cls.id
           select_from - if not None, a valid from-clause as with
                         Query.select_from (see SQLA docs)

        Returns - integer count

        '''

        cols = func.count(cols or cls.id)
        query = cls.query(cols)
        if filters:
            query = query.filter(*filters)
        if select_from:
            query = query.select_from(select_from)

        return query.scalar()

    @classmethod
    def create_table(cls, *args, **kwargs):
        '''Issue CREATE TABLE, delegating to Table.create()
        '''

        return cls.__table__.create(*args, **kwargs)

    @classmethod
    def drop_table(cls, *args, **kwargs):
        '''Issue DROP TABLE, delegating to Table.drop()
        '''

        return cls.__table__.drop(*args, **kwargs)

    @classmethod
    def query(cls, *entities):
        '''Return Query for the class.

        Args -

           entities - entities or columns to be used in the query
                      constructor: query(*entities).  If no entities are
                      specified, cls will be used.

        Returns - SQLA Query
        '''

        if not entities:
            entities = (cls,)

        return dbsession.query(*entities)

    @classmethod
    def get(cls, pk):
        '''Return instance with primary key, pk.

        Returns None if no instance found.
        '''

        return dbsession.query(cls).get(pk)

    @classmethod
    def exists(cls, *filters):
        '''Return a boolean indicating an instance exists

        Args -

           *filters -    filters to apply as with Query.filter() (see SQLA docs)

        Returns - True | False

        '''

        query = cls.query(cls.id)
        if filters:
            query = query.filter(*filters)

        return dbsession.query(query.exists()).scalar()

    @classmethod
    def create(cls, **attrs):
        'Create a new instance, setting the attrs and flushing to db'

        # create new instance and add to session
        entity = cls()
        dbsession.add(entity)
        # the update does the flush
        return entity.update(_create_=True, **attrs)

    @classmethod
    def create_no_flush(cls, **attrs):
        'Create a new instance, setting the attrs but NOT flushing to db'

        return cls.create(_flush_=False, **attrs)

    @classmethod
    def list(cls, query=None, sort=None, offset=None, limit=None):
        '''Fetch a list of entities of the class

        Args -

           query - a Query to be used to fetch instances of this class.
                   If None, cls.Query() will be used.

           sort - fieldname, suitable value for order_by().  May also be
                  a tuple of fieldnames to specify multi-field sorting.
                  If fieldname begins with "-", the order will be
                  descending.

           offset, limit - if both specified, slice() will be called on
                           the query; if only limit, limit() will be
                           called on the query.

        Returns - list of entities of class.

        '''

        # if no query passed in, get default query.
        if query is None:
            query = cls.query()

        # if sort is not specified, initialize to empty tuple
        if not sort:
            sort = ()
        elif isinstance(sort, str):
            # convert to sequence
            sort = (sort,)

        # collect all the fields to order by
        ob = []
        for field in sort:
            desc = field.startswith('-')
            if desc:
                field = field[1:]
            field = getattr(cls, field)
            if desc:
                field = - field
            ob.append(field)

        # put them all together, eg., "foo desc, bar"
        if ob:
            query = query.order_by(*ob)

        if offset is not None and limit is not None:
            # slice if both are specified
            query = query.slice(offset, offset + limit)
        elif limit is not None:
            # else just limit?
            query = query.limit(limit)

        # return all entities
        return query.all()

    def update(self, _create_=False, _flush_=True, **attrs):
        'Update the instance with the given attributes and flush the db session'

        # NOTE: _create_ is an internal flag indicating this update is
        # happening during creation of an instance, i.e, from within a
        # call to create()

        # NOTE: _flush_ is an internal flag indicating whether or not
        # the update should flush the session after updating attributes.
        # Default: True, do the flush

        # handle the "id" attribute specially
        if hasattr(self, 'id'):
            if ((
                        _create_ and 'id' in attrs and not self.__update_create_id_ok__)
                or (not _create_ and 'id' in attrs and attrs['id'] != self.id)):
                raise exceptions.AttrError("Cannot set or update id")
            # set it first
            if 'id' in attrs:
                self.id = attrs.pop('id')

        if not _create_ and not self.__update_after_create__:
            raise exceptions.AttrError('{} is read-only after creation'.format(
                self.__class__.__name__))

        # ignored attributes
        for attr in self.__update_ignore__.intersection(attrs.keys()):
            del attrs[attr]

        # known column names, including hybrid properties
        columns = self.columns

        # for each attr, set it on the instance
        for colname, value in attrs.items():
            if colname in self.__update_never__:
                raise exceptions.AttrError('Cannot update {}'.format(colname))
            elif colname in self.__update_on_create__ and not _create_:
                raise exceptions.AttrError(
                    'Cannot update {} after creattion'.format(colname))
            elif colname not in columns and colname not in self.__update_props__:
                raise exceptions.AttrError(
                    'Unknown column or property: {}'.format(colname))
            try:
                setattr(self, colname, value)
            except AttributeError as exc:
                raise exceptions.AttrError(
                    'Cannot set attribute {}: {}'.format(colname, exc))
            except ValueError as exc:
                raise exceptions.ValError(
                    'Cannot set attribute {}: {}'.format(colname, exc))

        # flush to db
        if _flush_:
            dbsession.flush()

        return self

    def update_no_flush(self, **attrs):
        'Update the instance with the given attributes, but do NOT flush the session'

        return self.update(_flush_=False, **attrs)

    def delete(self, flush=True):
        '''Delete the instance.

        Note: while not committed, the operation is flushed to the db if flush is True (the default)
        '''

        dbsession.delete(self)
        if flush:
            dbsession.flush()

    def delete_no_flush(self):
        '''Delete the instance without flushing to the database.  Same as delete(flush=False).
        '''

        self.delete(flush=False)
