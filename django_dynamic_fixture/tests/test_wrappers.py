# -*- coding: utf-8 -*-

from django.test import TestCase

from django_dynamic_fixture.models_test import EmptyModel, ModelWithRelationships, ModelForLibrary
from django_dynamic_fixture import N, G, F, C, P, teach, look_up_alias, PRE_SAVE, POST_SAVE


class NShortcutTest(TestCase):
    def test_shortcut_N(self):
        instance = N(EmptyModel)
        assert instance.id == None


class GShortcutTest(TestCase):
    def test_shortcut_G(self):
        instance = G(EmptyModel)
        assert instance.id != None


class PShortcutTest(TestCase):
    def test_accept_model_instance(self):
        P(N(EmptyModel))
        P(G(EmptyModel))

    def test_accepts_list(self):
        P([N(EmptyModel), G(EmptyModel)])

    def test_accepts_tuple(self):
        P((N(EmptyModel), G(EmptyModel)))

    def test_accepts_queryset(self):
        P(EmptyModel.objects.all())


class FShortcutTest(TestCase):
    def test_fk(self):
        instance = G(ModelWithRelationships, integer=1000, foreignkey=F(integer=1001))
        assert 1000, instance.integer == 1000
        assert instance.foreignkey.integer == 1001

    def test_self_fk(self):
        instance = G(ModelWithRelationships, integer=1000, selfforeignkey=F(integer=1001))
        assert instance.integer == 1000
        assert instance.selfforeignkey.integer == 1001

    def test_o2o(self):
        instance = G(ModelWithRelationships, integer=1000, onetoone=F(integer=1001))
        assert instance.integer == 1000
        assert instance.onetoone.integer == 1001

    def test_m2m_with_one_element(self):
        instance = G(ModelWithRelationships, integer=1000, manytomany=[F(integer=1001)])
        assert instance.integer == 1000
        assert instance.manytomany.all()[0].integer == 1001

    def test_m2m_with_many_elements(self):
        instance = G(ModelWithRelationships, integer=1000, manytomany=[F(integer=1001), F(integer=1002)])
        assert instance.integer == 1000
        assert instance.manytomany.all()[0].integer == 1001
        assert instance.manytomany.all()[1].integer == 1002

    def test_full_example(self):
        instance = G(ModelWithRelationships, integer=1000,
                     foreignkey=F(integer=1001),
                     selfforeignkey=F(integer=1002),
                     onetoone=F(integer=1003),
                     manytomany=[F(integer=1004), F(integer=1005), F(selfforeignkey=F(integer=1006))])
        assert instance.integer == 1000
        assert instance.foreignkey.integer == 1001
        assert instance.selfforeignkey.integer == 1002
        assert instance.onetoone.integer == 1003
        assert instance.manytomany.all()[0].integer == 1004
        assert instance.manytomany.all()[1].integer == 1005
        assert instance.manytomany.all()[2].selfforeignkey.integer == 1006

    def test_using_look_up_alias(self):
        instance = G(ModelWithRelationships, integer=1000,
                     foreignkey__integer=1001,
                     selfforeignkey__integer=1002,
                     onetoone__integer=1003,
                     manytomany=[F(integer=1004), F(integer=1005), F(selfforeignkey__integer=1006)])
        assert instance.integer == 1000
        assert instance.foreignkey.integer == 1001
        assert instance.selfforeignkey.integer == 1002
        assert instance.onetoone.integer == 1003
        assert instance.manytomany.all()[0].integer == 1004
        assert instance.manytomany.all()[1].integer == 1005
        assert instance.manytomany.all()[2].selfforeignkey.integer == 1006


class CShortcutTest(TestCase):
    def test_copying_from_the_same_model(self):
        instance = G(ModelWithRelationships, integer=C('integer_b'))
        assert instance.integer == instance.integer_b

    def test_copying_from_a_fk(self):
        instance = G(ModelWithRelationships, foreignkey=F(), integer=C('foreignkey.integer'))
        assert instance.integer == instance.foreignkey.integer

    def test_copying_from_a_one2one(self):
        instance = G(ModelWithRelationships, onetoone=F(), integer=C('onetoone.integer'))
        assert instance.integer == instance.onetoone.integer

    def test_copying_from_a_self_fk(self):
        instance = G(ModelWithRelationships, selfforeignkey=F(), integer=C('selfforeignkey.integer_b'))
        assert instance.integer == instance.selfforeignkey.integer_b

    def test_copying_inside_fk(self):
        instance = G(ModelWithRelationships, selfforeignkey=F(selfforeignkey=F(), integer=C('selfforeignkey.integer_b')))
        assert instance.selfforeignkey.integer == instance.selfforeignkey.selfforeignkey.integer_b

    def test_copying_inside_many_to_many(self):
        instance = G(ModelWithRelationships, manytomany=[F(integer=C('integer_b'))])
        instance1 = instance.manytomany.all()[0]
        assert instance1.integer == instance1.integer_b


class TeachingAndLessonsTest(TestCase):
    def test_global_lesson(self):
        teach(ModelForLibrary, integer=1000)
        instance = G(ModelForLibrary)
        assert instance.integer == 1000

        instance = G(ModelForLibrary, integer=1001)
        assert instance.integer == 1001

        instance = G(ModelForLibrary)
        assert instance.integer == 1000


class CreatingMultipleObjectsTest(TestCase):
    def test_new(self):
        assert N(EmptyModel, n=0) == []
        assert N(EmptyModel, n= -1) == []
        assert isinstance(N(EmptyModel), EmptyModel) # default is 1
        assert isinstance(N(EmptyModel, n=1), EmptyModel)
        assert len(N(EmptyModel, n=2)) == 2

    def test_get(self):
        assert G(EmptyModel, n=0) == []
        assert G(EmptyModel, n= -1) == []
        assert isinstance(G(EmptyModel), EmptyModel) # default is 1
        assert isinstance(G(EmptyModel, n=1), EmptyModel)
        assert len(G(EmptyModel, n=2)) == 2


class LookUpSeparatorTest(TestCase):
    def test_look_up_alias_with_just_one_parameter(self):
        assert {'a': 1} == look_up_alias(a=1)
        assert {'a': F()} == look_up_alias(a=F())
        assert {'a_b': 1} == look_up_alias(a_b=1)
        assert {'a': F(b=1)} == look_up_alias(a__b=1)
        assert {'a_b': F(c=1)} == look_up_alias(a_b__c=1)
        assert {'a': F(b=F(c=1))} == look_up_alias(a__b__c=1)
        assert {'a_b': F(c_d=F(e_f=1))} == look_up_alias(a_b__c_d__e_f=1)

    def test_look_up_alias_with_many_parameters(self):
        assert {'a': 1, 'b': 2} == look_up_alias(a=1, b=2)
        assert {'a': 1, 'b_c': 2} == look_up_alias(a=1, b_c=2)
        assert {'a': 1, 'b': F(c=2)} == look_up_alias(a=1, b__c=2)
        assert {'a': F(b=1), 'c': F(d=2)} == look_up_alias(a__b=1, c__d=2)


class PreAndPostSaveTest(TestCase):
    def tearDown(self):
        # Workaround to pass the tests in Travis, caused by an unknown issue
        # with LazySettings and ALLOWED_HOSTS
        pass

    def test_pre_save(self):
        PRE_SAVE(EmptyModel, lambda x: x)

    def test_post_save(self):
        POST_SAVE(EmptyModel, lambda x: x)

