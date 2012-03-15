from django.contrib import admin
from django.forms.models import BaseInlineFormSet, BaseModelFormSet


class FormSet(BaseInlineFormSet):
    def __init__(self, data=None, files=None, instance=None,
                 save_as_new=False, prefix=None, queryset=None, **kwargs):
        from django.db.models.fields.related import RelatedObject
        if instance is None:
            self.instance = self.fk.rel.to()
        else:
            self.instance = instance
        self.save_as_new = save_as_new
        # is there a better way to get the object descriptor?
        self.rel_name = RelatedObject(self.fk.rel.to, self.model, self.fk).get_accessor_name()
        if queryset is None:
            queryset = self.model._default_manager
        # manually set queryset as evaluated
        obj = self.model.get_field().value_from_object(self.instance)
        if obj:
            queryset._result_cache = [obj]
        BaseModelFormSet.__init__(self, data, files, prefix=prefix,
                                                queryset=queryset, **kwargs)


class SubModelFieldInlineAdmin(admin.StackedInline):
    formset = FormSet

    def has_add_permission(self, request):
        return self.related_modeladmin.has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        return self.related_modeladmin.has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        # delete just works as change
        return self.has_change_permission(request, obj)

    @property
    def related_modeladmin(self):
        return self.admin_site._registry.get(self.parent_model)
