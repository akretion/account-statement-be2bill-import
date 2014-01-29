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
            #"OPERATION_DATE": format_date,
            #"PAYMENT_DATE": format_date,
            #"TRANSACTION_ID": unicode,
            #"OPERATION_NAME": unicode,
            #"OPERATION_AMOUNT": float_or_zero,
            #"OPERATION_SEQUENCE": unicode,
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

    def get_st_line_vals(self, line, *args, **kwargs):
        res = {
            'name': line["TRANSACTION_ID"],
            'date': line["OPERATION_DATE"],
            'amount': line['OPERATION_AMOUNT'],
            'ref': '/',
            'transaction_id': line["TRANSACTION_ID"],
            'label': line["OPERATION_NAME"],
        }
        return res
