from django.core.serializers.json import Serializer, Deserializer
from django.db import models


class Manager(models.Manager):
    def get_query_set(self):
        return FakeQuerySet(self.model, using=self._db)


class FakeQuerySet(models.query.EmptyQuerySet):
    """Faked QuerySet that always treats itself as evaluated.
    Only the changing of _result_cache can change the content of a FakeQuerySet()
    """
    def count(self):
        return len(self)

    def _clone(self, klass=None, setup=False, **kwargs):
        c = super(FakeQuerySet, self)._clone(klass, setup=setup, **kwargs)
        c._result_cache = self._result_cache[:]
        return c

    def iterator(self):
        yield iter(self._result_cache).next()


class SubModelField(models.TextField):
    """A field which could include model fields and work as a model instance.
    Data of the field are stored in single json-like TextField.
    """

    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.fields = kwargs.pop('fields', ())
        # TODO kwargs for json dumping and loading?
        kwargs.setdefault('editable', False)
        super(SubModelField, self).__init__(*args, **kwargs)

    @property
    def submodel(self):
        if not hasattr(self, '_submodel'):
            def save(self_, *args_, **kwargs_):
                setattr(self_._fk, self.name, self_)
                self_._fk.save()
            def delete(self_, *args_, **kwargs_):
                setattr(self_._fk, self.name, None)
                self_._fk.save()
            class Meta:
                verbose_name = self.verbose_name or self.name
            attrs = dict(self.fields)
            # TODO need to ensure field types?
            assert '_fk' not in attrs, u'name "_fk" is reserved for pk for submodel.'
            attrs.update({
                '__module__': self.model.__module__,
                'save': save,
                'delete': delete,
                '_fk': models.OneToOneField(self.model, primary_key=True),
                'objects': Manager(),
                'get_field': classmethod(lambda x: self),
                # XXX override Model.prepare_database_save to save whole dump instead of pk only
                'prepare_database_save': lambda obj, unused: self.get_db_prep_value(obj),
                'Meta': Meta
                # TODO help_text and customized fields such as __unicode__
            })
            self._submodel = type('%s%sSubModel' % (self.model._meta.object_name, self.name.capitalize()), (models.Model,), attrs)
        return self._submodel

    def to_python(self, value):
        """
        submodel instance => submodel instance
        deserializable dumped submodel array => submodel instance
        otherwise => None
        """
        if isinstance(value, self.submodel):
            return value
        try:
            obj = tuple(Deserializer(value))[0].object
            assert isinstance(obj, self.submodel)
            return obj
        except:
            return

    def get_db_prep_value(self, value, *args, **kwargs):
        """Model instance to json-dumped string.
        Always store as array, for easy Deserializer()
        """
        if isinstance(value, self.submodel):
            return Serializer().serialize([value])
        if isinstance(value, basestring):
            # TODO check
            return value
        return '[]'

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)


try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], [r'^submodel\.fields\.SubModelField'])
except ImportError:
    pass
