# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval


__all___ = ['Project']


class Project:
    __name__ = 'project.work'
    __metaclass__ = PoolMeta

    asset = fields.Many2One('asset', 'Asset',
        states={
            'invisible': Eval('type') != 'project',
            },
        depends=['type'])

    @classmethod
    def __setup__(cls):
        super(Project, cls).__setup__()
        pool = Pool()
        Asset = pool.get('asset')
        # If asset_owner module is installed we can add this domain
        if hasattr(Asset, 'owners'):
            cls.asset.domain = [
                ('owners.owner', '=', Eval('party')),
                ]
            cls.asset.depends.append('party')

