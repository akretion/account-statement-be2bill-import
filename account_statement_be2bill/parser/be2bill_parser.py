# -*- coding: utf-8 -*-
###############################################################################
#   account_statement_be2bill for OpenERP
#   Copyright (C) 2014-TODAY Akretion <http://www.akretion.com>.
#   @author Arthur Vuillard <arthur.vuillard@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.addons.account_statement_base_import.parser.file_parser import (
    float_or_zero,
    FileParser
)
    
from csv import Dialect
from _csv import QUOTE_MINIMAL, register_dialect
import codecs


class be2bill_dialect(Dialect):
    delimiter = ';'
    quotechar = '"'
    doublequote = False
    skipinitialspace = False
    lineterminator = '\n'
    quoting = QUOTE_MINIMAL


register_dialect("be2bill_dialect", be2bill_dialect)


class Be2BillFileParser(FileParser):
    def __init__(self, parse_name, ftype='csv'):
        conversion_dict = {
            'ORDERID': unicode,
            'AMOUNT': float_or_zero,
            'TRANSACTIONID': unicode,
        }
        super(Be2BillFileParser, self).__init__(
            parse_name, ftype=ftype, conversion_dict=conversion_dict,
            dialect=be2bill_dialect
        )

    @classmethod
    def parser_for(cls, parser_name):
        """
        Used by the new_bank_statement_parser class factory. Return true if
        the providen name is be2bill_csvparser
        """
        return parser_name == 'be2bill_csvparser'

    def _pre(self, *args, **kwargs):
        super(Be2BillFileParser, self)._pre(*args, **kwargs)
        split_file = self.filebuffer.split("\n")
        selected_lines = []
        for line in split_file:
            if line.startswith(codecs.BOM_UTF8):
                line = line[3:]
            selected_lines.append(line.strip())
        self.filebuffer = "\n".join(selected_lines)

    def get_st_line_vals(self, line, *args, **kwargs):
        amount = line['AMOUNT']
        if 'BILLINGFEESTTC' in line:
            amount /= 100
        if line['NATURE'] == 'refund':
            amount *= -1
        res = {
            'transaction_id': line['TRANSACTIONID'],
            'name': line['TRANSACTIONID'],
            'date': line['DATE'],
            'amount': amount,
            'ref': line['ORDERID'],
            'label': line['DESCRIPTION'],
        }
        return res

    def _post(self, *args, **kwargs):
        super(Be2BillFileParser, self)._post(*args, **kwargs)
        for row in self.result_row_list:
            if 'BILLINGFEESTTC' in row:
                commission_amount = row['BILLINGFEESTTC']
            elif 'BILLINGFEES INCL. VAT' in row:
                commission_amount = row['BILLINGFEES INCL. VAT']
            else:
                raise ValueError('Can\'t find fees amount')
            commission_amount = - float_or_zero(commission_amount)
            if 'BILLINGFEESTTC' in row:
                commission_amount /= 100
            if row['NATURE'] == 'refund':
                commission_amount = 0.0
            row['commission_amount'] = commission_amount
