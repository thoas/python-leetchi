from .exceptions import APIError


class BaseQuery(object):
    def __init__(self, model, method=None):
        self.model = model
        self.method = method

    def get_field_transcription(self):
        return dict((field.api_name, field.name) for field in self.model._meta.fields.values())

    def parse_result(self, result):
        pairs = {}
        for api_name, field_name in self.get_field_transcription().items():
            field = self.model._meta.get_field_by_name(field_name)
            if api_name in result:
                pairs[field_name] = field.python_value(result[api_name])

        return pairs


class SelectQuery(BaseQuery):
    def __init__(self, model, *args, **kwargs):
        super(SelectQuery, self).__init__(model, 'GET')

    def get(self, reference, handler):
        try:
            result, data = handler.request(self.method,
                                           '/%s/%d' % (self.model._meta.verbose_name_plural, reference))
        except APIError as e:
            if e.code == 404:
                raise self.model.DoesNotExist('instance %s matching reference %d does not exist' % (self.model._meta.model_name, reference))
        else:
            return self.model(**dict(self.parse_result(data), **{'handler': handler}))

    def list(self, reference, resource_model, handler):
        result, data = handler.request(self.method,
                                       '/%s/%d/%s' % (resource_model._meta.verbose_name_plural, reference,
                                                      self.model._meta.verbose_name_plural))

        return [self.model(**dict(self.parse_result(entry), **{'handler': handler})) for entry in data]


class InsertQuery(BaseQuery):
    def __init__(self, model, **kwargs):
        self.insert_query = kwargs
        super(InsertQuery, self).__init__(model, 'POST')

    def parse_insert(self):
        pairs = {}
        for k, v in self.insert_query.iteritems():
            field = self.model._meta.get_field_by_name(k)

            if field.required or v is not None:
                pairs[field.api_name] = field.api_value(v)

        return pairs

    def execute(self, handler):
        data = self.parse_insert()

        result, data = handler.request(self.method,
                                       '/%s/' % self.model._meta.verbose_name_plural,
                                       data=data)

        return dict(self.parse_result(data), **{'handler': handler})


class UpdateQuery(BaseQuery):
    def __init__(self, model, reference, **kwargs):
        self.update_query = kwargs
        self.reference = reference
        super(UpdateQuery, self).__init__(model, 'PUT')

    def parse_update(self):
        pairs = {}
        for k, v in self.update_query.iteritems():
            field = self.model._meta.get_field_by_name(k)

            if field.required or v is not None:
                pairs[field.api_name] = field.api_value(v)

        return pairs

    def execute(self, handler):
        data = self.parse_update()

        result, data = handler.request(self.method,
                                       '/%s/%d/' % (self.model._meta.verbose_name_plural, self.reference),
                                       data=data)

        return self.parse_result(data)
