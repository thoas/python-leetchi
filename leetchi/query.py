import six

from .exceptions import APIError


class BaseQuery(object):
    def __init__(self, model, method=None, **kwargs):
        self.model = model
        self.method = method
        self.handler = kwargs.pop('handler', None)

    def get_field_transcription(self):
        return dict((field.api_name, field.name)
                    for field in self.model._meta.fields.values())

    def parse_result(self, result):
        pairs = {}
        for api_name, field_name in self.get_field_transcription().items():
            field = self.model._meta.get_field_by_name(field_name)
            if result and api_name in result:
                pairs[field_name] = field.python_value(result[api_name])

        return pairs

    def parse_url(self, meta_url, params=None):
        if isinstance(meta_url, dict):
            url = meta_url.get(self.identifier)
        else:
            url = meta_url

        if params:
            url = url % params

        return url


class SelectQuery(BaseQuery):
    identifier = 'SELECT'

    def __init__(self, model, *args, **kwargs):
        super(SelectQuery, self).__init__(model, 'GET', **kwargs)

    def get(self, reference, handler=None, resource_model=None, **kwargs):
        handler = handler or self.handler

        url = getattr(self.model._meta, 'url', None)

        if url is not None:
            url = self.parse_url(url, kwargs)

        try:
            if url is None:
                if resource_model is None:
                    url = '/%s/%d' % (self.model._meta.verbose_name_plural,
                                      reference)
                else:
                    url = '/%s/%d/%s' % (resource_model._meta.verbose_name_plural,
                                         reference,
                                         self.model._meta.verbose_name_plural)

            result, data = handler.request(self.method, url)
        except APIError as e:
            if e.code == 404:
                raise self.model.DoesNotExist('instance %s matching reference %d does not exist' % (self.model._meta.model_name, reference))

            raise e
        else:
            return self.model(**dict(self.parse_result(data), **{'handler': handler}))

    def list(self, reference, resource_model, handler=None):
        handler = handler or self.handler

        result, data = handler.request(self.method,
                                       '/%s/%d/%s' % (resource_model._meta.verbose_name_plural, reference,
                                                      self.model._meta.verbose_name_plural))

        return [self.model(**dict(self.parse_result(entry), **{'handler': handler})) for entry in data]


class InsertQuery(BaseQuery):
    identifier = 'INSERT'

    def __init__(self, model, **kwargs):
        super(InsertQuery, self).__init__(model, 'POST', **kwargs)

        kwargs.pop('handler', None)

        self.insert_query = kwargs

    def parse_insert(self):
        pairs = {}
        for k, v in six.iteritems(self.insert_query):
            field = self.model._meta.get_field_by_name(k)

            if field.required or v is not None:
                pairs[field.api_name] = field.api_value(v)

        return pairs

    def execute(self, handler=None):
        handler = handler or self.handler

        data = self.parse_insert()

        url = getattr(self.model._meta, 'url', None)

        if url:
            url = self.parse_url(url, self.insert_query)
        else:
            url = '/%s/' % self.model._meta.verbose_name_plural

        result, data = handler.request(self.method,
                                       url,
                                       data=data)

        return dict(self.parse_result(data), **{'handler': handler})


class UpdateQuery(BaseQuery):
    identifier = 'UPDATE'

    def __init__(self, model, reference, **kwargs):
        super(UpdateQuery, self).__init__(model, 'PUT', **kwargs)

        kwargs.pop('handler', None)

        self.update_query = kwargs
        self.reference = reference

    def parse_update(self):
        pairs = {}
        for k, v in six.iteritems(self.update_query):
            field = self.model._meta.get_field_by_name(k)

            if field.required or v is not None:
                pairs[field.api_name] = field.api_value(v)

        return pairs

    def execute(self, handler=None):
        handler = handler or self.handler

        data = self.parse_update()

        url = getattr(self.model._meta, 'url', None)

        if url:
            url = self.parse_url(url, self.update_query)
        else:
            url = '/%s/%d/' % (self.model._meta.verbose_name_plural, self.reference)

        result, data = handler.request(self.method,
                                       url,
                                       data=data)

        return self.parse_result(data)
