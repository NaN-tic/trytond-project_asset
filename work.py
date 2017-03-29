# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.pyson import Eval


__all___ = ['Project']


class Project:
    __name__ = 'project.work'
    __metaclass__ = PoolMeta
    asset = fields.Many2One('asset', 'Asset',
#        domain=[('owners.owner', '=', Eval('party'))],
        states={
            'invisible': Eval('type') != 'project',
            },
        depends=['type', 'party'])
