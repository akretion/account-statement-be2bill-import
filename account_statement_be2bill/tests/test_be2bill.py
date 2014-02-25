import base64

from datetime import date
from os.path import (
    join,
    abspath,
    dirname,
)

from openerp.tests.common import TransactionCase


class TestBe2bill(TransactionCase):
    def _import_file(self, filename):
        cr, uid = self.cr, self.uid

        _, profile_id = self.registry('ir.model.data').get_object_reference(
            cr, uid, 'account_statement_be2bill', 'be2bill_statement_profile'
        )
        data_filename = join(dirname(abspath(__file__)), filename)
        with open(data_filename, 'r') as data_file:
            input_statement = base64.encodestring(data_file.read())

        context = {'file_name': filename}
        statement_id = self.registry('account.statement.profile')\
            .statement_import(
                cr, uid, False, profile_id, input_statement, 'csv', context
            )
        return self.registry('account.bank.statement')\
            .browse(cr, uid, statement_id)[0]

    def test_import(self):
        cr, uid = self.cr, self.uid
        statement = self._import_file('be2bill_file.csv')

        self.assertEquals(len(statement.line_ids), 3)

        line_ids = map(lambda line: line.id, statement.line_ids)
        lines = self.registry('account.bank.statement.line')\
            .read(cr, uid, line_ids)
        for line in lines:
            if line['transaction_id'] == u'A00000001':
                self.assertEquals(line['name'], u'Payment')
                self.assertEquals(line['date'], '2014-02-03')
                self.assertEquals(line['amount'], 67.77)
                self.assertEquals(line['ref'], u'000000001')
            if line['transaction_id'] == u'A00000003':
                self.assertEquals(line['name'], u'annulation client')
                self.assertEquals(line['date'], '2014-02-04')
                self.assertEquals(line['amount'], -92.81)
                self.assertEquals(line['ref'], u'000002')
            if not line['transaction_id']:
                self.assertEquals(line['name'], u'IN Commission line')
                self.assertEquals(
                    line['date'],
                    date.today().strftime('%Y-%m-%d')
                )
                self.assertEquals(line['amount'], -0.59)
                self.assertEquals(line['ref'], u'commission')

    def test_import_new(self):
        cr, uid = self.cr, self.uid
        statement = self._import_file('be2bill_file_new.csv')

        self.assertEquals(len(statement.line_ids), 2)

        line_ids = map(lambda line: line.id, statement.line_ids)
        lines = self.registry('account.bank.statement.line')\
            .read(cr, uid, line_ids)

        line_transaction = lines[0]
        self.assertEquals(line_transaction['name'], u'Several times payment')
        self.assertEquals(line_transaction['date'], '2014-02-20')
        self.assertEquals(line_transaction['amount'], 74.18)
        self.assertEquals(line_transaction['ref'], u'ABCDEFGHI')
        self.assertEquals(line_transaction['transaction_id'], u'B00000005')

        line_fees = lines[1]
        self.assertFalse(line_fees['label'])
        self.assertEquals(line_fees['name'], u'IN Commission line')
        self.assertEquals(
            line_fees['date'],
            date.today().strftime('%Y-%m-%d')
        )
        self.assertEquals(line_fees['amount'], -0.62)
        self.assertEquals(line_fees['ref'], u'commission')
        self.assertFalse(line_fees['transaction_id'])


class TestAccountStatementProfil(TransactionCase):
    def test_get_import_type_selection(self):
        cr, uid = self.cr, self.uid
        import_types = self.registry("account.statement.profile")\
            .get_import_type_selection(cr, uid)
        expected = ('be2bill_csvparser', 'Parser for Be2Bill import statement')
        self.assertTrue(expected in import_types)
