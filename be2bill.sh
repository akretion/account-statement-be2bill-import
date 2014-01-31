#!/bin/bash

#source ~/.virtualenvs/be2bill/bin/activate

PYTHON=python
SERVER=ocb-server/openerp-server
ADDONS=ocb-addons,ocb-web/addons,banking-addons-reconcile,file-exchange,account-statement-be2bill-import

$PYTHON $SERVER --addons-path=${ADDONS} $@

