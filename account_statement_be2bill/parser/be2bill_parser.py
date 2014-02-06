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

from account_statement_base_import.parser.file_parser import FileParser
from csv import Dialect
from _csv import QUOTE_MINIMAL, register_dialect
from openerp.osv import osv
from openerp.tools.translate import _
import codecs

class be2bill_dialect(Dialect):
    delimiter = ';'
    quotechar = '"'
    doublequote = False
    skipinitialspace = False
    lineterminator = '\n'
    quoting = QUOTE_MINIMAL


register_dialect("be2bill_dialect", be2bill_dialect)

def float_or_zero(val):
    """ Conversion function used to manage
    empty string into float usecase"""
    return float(val) if val else 0.0

class Be2BillFileParser(FileParser):
    def __init__(self, parse_name, ftype='csv'):
        print "__init__"
        conversion_dict = {
            'EXECCODE': float_or_zero,
            'MESSAGE': unicode,
            'ORDERID': float_or_zero,
            'AMOUNT': float_or_zero,
            'TRANSACTIONID': unicode,
        }
        self.refund_amount = None
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
        """
            Remove undesired character at the beginning of the file.
        """
        split_file = self.filebuffer.split("\n")
        selected_lines = []
        for line in split_file:
            if line.startswith(codecs.BOM_UTF8):
                line = line[3:]
            selected_lines.append(line.strip())
        self.filebuffer = "\n".join(selected_lines)

    def get_st_line_vals(self, line, *args, **kwargs):
        if line['EXECCODE'] != 0: 
            raise osv.except_osv(_('Error!'),
                    _('Use case not managed !\nEXECCODE (%s) MESSAGE. (%s)') % (line['EXECCODE'], line['MESSAGE']))
        res = {
            'transaction_id': line['TRANSACTIONID'],
            'name': line['TRANSACTIONID'],
            'date': line['DATE'],
            'amount': line['AMOUNT'] / 100,
            'ref': '/',             # TODO
            'label': '/',           # TODO
        }
        return res
