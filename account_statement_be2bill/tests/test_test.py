import unittest2
from openerp.tests.common import TransactionCase

class TestTest(unittest2.TestCase):
    def test_it(self):
        self.assertEquals(1, 1)

    def test_fail(self):
        self.assertEquals(1, 2)


class TestResPartner(TransactionCase):
    def test_create(self):
        cr, uid = self.cr, self.uid
        vals = {
            'name': 'nice guy',
            'is_nice': True,
        }
        self.registry('res.partner').create(cr, uid, vals)

    def test_method(self):
        cr, uid = self.cr, self.uid
        self.registry('res.partner').method(cr, uid, [])
