===============
django-submodel
===============

A Django field which: works like a model instance, stores sub-model fields in single DB column, and supports smooth editing in Django admin. 

django-submodel works on Django 1.3+

Installation
============
#. ``pip install django-submodel``
#. Add `submodel` to INSTALLED_APPS in your current settings file.

Usage
=====

::

    # in you_app/models.py

    from django.db import models
    from submodel.fields import SubModelField


    # Define (field_name, model_field_instance) tuples in "fields" parameter in SubModelField,
    #   similar as normal Model definition
    # If SubModelField such as pref field is newly added to an existed model,
    #   you may want to use south to migrate the schema
    class UserProfile(models.Model):
        realname = models.CharField(max_length=100)
        pref = SubModelField(u'user preference',
                     fields=(
                         ('title', models.CharField(max_length=10)),
                         ('color', models.IntegerField(choices=((0, 'Black'), (1, 'White')))),
                         ('birthday_day', models.DateTimeField()),
                         ('feel_luck', models.BooleanField(default=True))))

::

    # in you_app/admin.py, to enable editing of sub fields of pref in Django admin

    from submodel.admin import SubModelFieldInlineAdmin
    from . models import UserProfile

    class PrefInilneAdmin(SubModelFieldInlineAdmin):
        model = UserProfile._meta.get_field('pref').submodel # TODO improve

    class UserProfileAdmin(admin.ModelAdmin):
        inlines = [PrefInilneAdmin]

    admin.site.register(UserProfile, UserProfileAdmin)

::

    >>> # TODO in Python shell, the value of pref field as a model instance


TODO
====
    - add tests
    - simpler API
    - dump and modify Deserializer to support missing subfields. schema policy?
    - better history
    - check compatibility w/ django-reversion and others ...
    - possible config
