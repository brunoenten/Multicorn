# Nose redefines assert_raises
# pylint: disable=E0611
from nose.tools import eq_
# pylint: enable=E0611

from kalamar.request import Condition, And, Or

from .test_combinations import common

@common
def test_view_simple(site):
    """The simplest view request"""
    results = list(site.view('first_ap'))
    eq_(len(results), 5)

@common
def test_view_filters(site):
    """Various view filters"""
    condition = Condition('id', '>', 3)
    results = list(site.view('first_ap', request=condition))
    eq_(len(results), 2)
    condition = Condition('color', '!=', u'blue')
    results = list(site.view('first_ap', request=condition))
    eq_(len(results), 3)
    condition = Condition('second_ap.code', '=', u'BBB')
    results = list(site.view('first_ap', request=condition))
    eq_(len(results), 2)
    condition = And(
            Condition('color', '!=', u'blue'),
            Condition('second_ap.code', '=', u'BBB'))
    results = list(site.view('first_ap', request=condition))
    eq_(len(results), 1)
    condition = Or(
            Condition('color', '!=', u'blue'),
            Condition('second_ap.code', '=', u'BBB'))
    results = list(site.view('first_ap', request=condition))
    eq_(len(results), 4)
    condition = And(
            Condition('id', '>', 3),
            Or(
                Condition('color', '!=', u'blue'),
                Condition('second_ap.code', '=', u'BBB')))
    results = list(site.view('first_ap', request=condition))
    eq_(len(results), 2)

@common
def test_order(site):
    """Asserts that an order clause is working"""
    order = [('color', True), ('name', False)]
    results = list(site.view('first_ap', order_by=order))
    assert(all([a['color'] < b['color'] or
        (a['color'] == b['color'] and
        a['name'] >= b['name'])
        for a, b in  zip(results[:-1], results[1:])]))

@common
def test_mapping(site):
    """Test various selections mappings"""
    mapping = {'second_ap_name': 'second_ap.name'}
    results = list(site.view('first_ap', aliases=mapping ))
    eq_(len(results), 5)
    assert(all([a['second_ap_name'] in [None, 'second_ap AAA', 'second_ap BBB']
            for a in results]))
    mapping = {'id': 'id', 'label': 'name'}
    results = list(site.view('first_ap', aliases=mapping))
    eq_(len(results), 5)
    assert all(['id' in a and 'label' in a for a in results])

@common
def test_distinct(site):
    """Test a ``distinct`` view query"""
    results = list(site.view('first_ap', {'color':'color'}, distinct=True))
    eq_(len(results), 3)

@common
def test_range(site):
    """Test the range Query"""
    results = list(site.view('first_ap', select_range=(1,2)))
    eq_(len(results), 1)
    results = list(site.view('first_ap', {'color': 'color'}, distinct=True,
        order_by=[('color', True)], select_range=(1,2)))
    eq_(len(results), 1)
    eq_(results[0]['color'], 'green')

@common
def test_one_to_many(site):
    """Test one to many relationships traversals"""
    mapping = {'fname' : 'first_aps.name'}
    results = list(site.view('second_ap', aliases=mapping))
    eq_(len(results), 4)
    results = list(site.view('second_ap', aliases=mapping, request={'first_aps.color':u'blue'}))
    eq_(len(results), 2)


@common
def test_item_condition(site):
    """Test a condition on an item directly"""
    item = site.open('second_ap', {'code': u'AAA'})
    condition = Condition('second_ap', '=', item)
    items = list(site.search('first_ap', condition))
    eq_(len(items), 2)
    items = list(site.view('first_ap', request=condition))
    eq_(len(items), 2)

