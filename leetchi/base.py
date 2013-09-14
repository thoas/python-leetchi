import six

from copy import deepcopy

from .fields import PrimaryKeyField, FieldDescriptor, Field

from .query import UpdateQuery, InsertQuery, SelectQuery

from .signals import pre_save, post_save


class DoesNotExist(Exception):
    pass


class BaseModelOptions(object):
    def __init__(self, model_class, options=None):
        self.rel_fields = {}
        self.fields = {}
        self.options = options or {}
        self.reverse_relations = {}
        self.defaults = {}

        for k, v in self.options.items():
            setattr(self, k, v)

        self.model_class = model_class

    def get_sorted_fields(self):
        return sorted(self.fields.items(), key=lambda k, v: (k == self.pk_name and 1 or 2, v._order))

    def get_field_names(self):
        return [f[0] for f in self.get_sorted_fields()]

    def get_fields(self):
        return [f[1] for f in self.get_sorted_fields()]

    def get_field_by_name(self, name):
        if name in self.fields:
            return self.fields[name]
        raise AttributeError('Field named %s not found' % name)

    def __contains__(self, k):
        return k in self.options

    def __setitem__(self, k, value):
        self.options[k] = value

    def __delitem__(self, k):
        if not k in self.options:
            raise KeyError('%s does not exists' % k)

        del self.options[k]

    def prepared(self):
        for field in self.fields.values():
            if field.default is None:
                continue

            self.defaults[field] = field.default

    def get_default_dict(self):
        dd = {}
        for field, default in self.defaults.items():
            if callable(default):
                dd[field.name] = default()
            else:
                dd[field.name] = default
        return dd


class ApiObjectBase(type):
    inheritable_options = ['verbose_name', 'verbose_name_plural']

    def __new__(cls, name, bases, attrs):
        super_new = super(ApiObjectBase, cls).__new__
        parents = [b for b in bases if isinstance(b, ApiObjectBase)]

        if not parents:
            # If this isn't a subclass of Model, don't do anything special.
            return super_new(cls, name, bases, attrs)

        module = attrs.pop('__module__')
        new_class = super_new(cls, name, bases, {'__module__': module})

        meta_options = {}
        meta = attrs.pop('Meta', None)
        if meta:
            meta_options.update((k, v) for k, v in meta.__dict__.items() if not k.startswith('_'))

        if not 'urls' in meta_options:
            meta_options['urls'] = {}

        orig_primary_key = None

        for b in bases:
            if not hasattr(b, '_meta'):
                continue

            base_meta = getattr(b, '_meta')
            for (k, v) in base_meta.__dict__.items():
                if k in cls.inheritable_options and k not in meta_options:
                    meta_options[k] = v

            for (k, attr) in b.__dict__.items():
                if not isinstance(attr, FieldDescriptor) or attr in attrs:
                    continue

                attrs[k] = deepcopy(attr.field)

                if isinstance(attr.field, PrimaryKeyField) and not orig_primary_key:
                    orig_primary_key = deepcopy(attr.field)

        cls = super(ApiObjectBase, cls).__new__(cls, name, bases, attrs)

        _meta = BaseModelOptions(cls, meta_options)
        cls._meta = _meta
        cls._data = None

        for name, attr in list(cls.__dict__.items()):
            if not isinstance(attr, Field):
                continue

            attr.add_to_class(cls, name)
            _meta.fields[attr.name] = attr

            if isinstance(attr, PrimaryKeyField):
                orig_primary_key = attr

        if not orig_primary_key is None:
            _meta.pk_name = orig_primary_key.name

        _meta.model_name = new_class.__name__

        for method in ('__unicode__', '__str__'):
            if hasattr(cls, method):
                setattr(cls, '__repr__', lambda self: '<%s: %s>' % (
                    _meta.model_name,
                    getattr(self, method)()
                ))

        exception_class = type('%sDoesNotExist' % _meta.model_name, (DoesNotExist,), {})

        cls.DoesNotExist = exception_class
        cls._meta.prepared()

        return cls


@six.add_metaclass(ApiObjectBase)
class BaseApiModel(object):

    def __init__(self, *args, **kwargs):
        self._data = self._meta.get_default_dict()
        self.handler = None

        for k, v in kwargs.items():
            setattr(self, k, v)

    def __eq__(self, other):
        return (other.__class__ == self.__class__ and
                self.get_pk() and
                other.get_pk() == self.get_pk())

    def save(self, handler=None, cls=None):
        if handler is None:
            handler = self.handler

        field_dict = dict(self._data)
        field_dict.update(self.get_field_dict())
        field_dict.pop(self._meta.pk_name)

        if cls is None:
            cls = self.__class__

        created = False

        pre_save.send(cls, instance=self)

        if self.get_pk():
            update = self.update(
                self.get_pk(),
                **field_dict
            )
            result = update.execute(handler)
        else:
            insert = self.insert(**field_dict)
            result = insert.execute(handler)

            created = True

        post_save.send(cls, instance=self, created=created)

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

    def one(self, resource_model):
        return resource_model.select().get(self.get_pk(),
                                           resource_model=self.__class__,
                                           handler=self.handler)

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
