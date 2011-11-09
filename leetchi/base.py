from .fields import PrimaryKeyField, Field
from .query import UpdateQuery, InsertQuery, SelectQuery


class DoesNotExist(Exception):
    pass


class BaseModelOptions(object):
    def __init__(self, model_class, options=None):
        self.rel_fields = {}
        self.fields = {}
        self.options = options or {}
        self.reverse_relations = {}

        for k, v in self.options.items():
            setattr(self, k, v)

        self.model_class = model_class

    def get_sorted_fields(self):
        return sorted(self.fields.items(), key=lambda (k,v): (k == self.pk_name and 1 or 2, v._order))

    def get_field_names(self):
        return [f[0] for f in self.get_sorted_fields()]

    def get_fields(self):
        return [f[1] for f in self.get_sorted_fields()]

    def get_field_by_name(self, name):
        if name in self.fields:
            return self.fields[name]
        raise AttributeError('Field named %s not found' % name)


class ApiObjectBase(type):
    def __new__(cls, name, bases, attrs):
        cls = type.__new__(cls, name, bases, attrs)

        meta = attrs.pop('Meta', None)

        attr_dict = {}

        if meta:
            attr_dict = meta.__dict__

        _meta = BaseModelOptions(cls, attr_dict)

        setattr(cls, '_meta', _meta)

        for name, attr in cls.__dict__.items():
            if isinstance(attr, Field):
                attr.add_to_class(cls, name)
                _meta.fields[attr.name] = attr
                if isinstance(attr, PrimaryKeyField):
                    _meta.pk_name = attr.name

        _meta.model_name = cls.__name__

        if hasattr(cls, '__unicode__'):
            setattr(cls, '__repr__', lambda self: '<%s: %s>' % (
                _meta.model_name, self.__unicode__()))

        exception_class = type('%sDoesNotExist' % _meta.model_name, (DoesNotExist,), {})

        cls.DoesNotExist = exception_class

        return cls


class BaseApiModel(object):
    __metaclass__ = ApiObjectBase

    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __eq__(self, other):
        return other.__class__ == self.__class__ and \
               self.get_pk() and \
               other.get_pk() == self.get_pk()

    def save(self, handler):
        field_dict = self.get_field_dict()

        field_dict.pop(self._meta.pk_name)

        if self.get_pk():
            update = self.update(
                self.get_pk(),
                **field_dict
            )
            result = update.execute(handler)
        else:
            insert = self.insert(**field_dict)
            result = insert.execute(handler)

        for key, value in result.items():
            setattr(self, key, value)

        return result

    @classmethod
    def select(cls, *args, **kwargs):
        return SelectQuery(cls, *args, **kwargs)

    @classmethod
    def create(cls, **query):
        handler = query.pop('handler')
        inst = cls(**query)
        inst.save(handler)
        return inst

    @classmethod
    def update(cls, reference, **query):
        return UpdateQuery(cls, reference, **query)

    @classmethod
    def insert(cls, **query):
        return InsertQuery(cls, **query)

    @classmethod
    def get(cls, *args, **kwargs):
        return cls.select().get(*args, **kwargs)

    def list(self, resource_model):
        return resource_model.select().list(self.get_pk(),
                                            self.__class__,
                                            handler=self.handler)

    def get_pk(self):
        return getattr(self, self._meta.pk_name, None)

    def get_pk_field(self):
        return self._meta.fields[self._meta.pk_name]

    def get_field_dict(self):
        def get_field_val(field):
            field_value = getattr(self, field.name)
            if not self.get_pk() and field_value is None and field.default is not None:
                if callable(field.default):
                    field_value = field.default()
                else:
                    field_value = field.default
                setattr(self, field.name, field_value)
            return (field.name, field_value)

        pairs = map(get_field_val, self._meta.fields.values())

        return dict(pairs)
