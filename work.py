# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval


__all___ = ['Project', 'Contract', 'ContractLine']


class Project:
    __name__ = 'project.work'
    __metaclass__ = PoolMeta

    asset = fields.Many2One('asset', 'Asset',
        states={
            'invisible': Eval('type') != 'project',
            },
        depends=['type'])
    contract_lines = fields.One2Many('contract.line', 'work',
       'Contract Lines',
       domain=[
           ('asset', '=', Eval('asset')),
           ],
       add_remove=[
           ('project', '=', None),
           ],
       depends=['asset'])
    contract = fields.Function(fields.Many2One('contract', 'Contract'),
       'get_contract', searcher='search_contract')

    @classmethod
    def __setup__(cls):
        super(Project, cls).__setup__()
# TODO: Dependency with shipment work?
#        cls.work_shipments.context.update({
#                'asset': Eval('asset'),
#                })
        pool = Pool()
        Asset = pool.get('asset')
        # If asset_owner module is installed we can add this domain
        if hasattr(Asset, 'owner'):
            cls.asset.domain = [
                ('current_owner', '=', Eval('party')),
                ]
            cls.asset.depends.append('party')

# TODO: Dependency with contract?
    def get_contract(self, name):
        return self.contract_lines and \
            self.contract_lines[0].contract.id or None

    @classmethod
    def search_contract(cls, name, clause):
        contract = clause[2]
        ContractLine = Pool().get('contract.line')
        lines = ContractLine.search([('contract', 'in', contract)])
        works = [x.work.id for x in lines if x.work]
        return [('id', 'in', works)]
#
# TODO: Dependency with shipment work?
#
#class ShipmentWork:
#    __name__ = 'shipment.work'
#    __metaclass__ = PoolMeta
#
#    @classmethod
#    def __setup__(cls):
#        super(ShipmentWork, cls).__setup__()
#        if 'asset' not in cls.project.depends:
#            cls.project.domain.append(If(Bool(Eval('asset')),
#                    ('asset', '=', Eval('asset')), ()))
#            cls.project.depends.append('asset')
#
# TODO: Dependency with contract?
#


class Contract:
    __name__ = 'contract'
    __metaclass__ = PoolMeta

    projects = fields.Function(fields.One2Many('project.work', None,
           'Projects'),
       'get_projects', searcher='search_projects')

    def get_projects(self, name):
        projects = set()
        for line in self.lines:
            if line.work:
                projects.add(line.work.id)
        return list(projects)

    @classmethod
    def search_projects(cls, name, clause):
        return [('lines.projects',) + tuple(clause[1:])]

    @classmethod
    def confirm(cls, contracts):
        super(Contract, cls).confirm(contracts)
        ContractLine = Pool().get('contract.line')
        lines = []
        for contract in contracts:
            lines += contract.lines
            print lines
        ContractLine.create_projects(lines)


class ContractLine:
    __name__ = 'contract.line'
    __metaclass__ = PoolMeta

    work = fields.Many2One('project.work', 'Project', select=True,
        domain=[
           ('asset', '=', Eval('asset')),
        #   ('maintenance', '=', True),
           ],
        depends=['asset'])

    def get_shipment_work(self, planned_date):
        shipment = super(ContractLine, self).get_shipment_work(planned_date)
        shipment.project = self.work
        return shipment

    def get_projects(self):
        pool = Pool()
        Project = pool.get('project.work')

        if self.work or not self.asset:
            return

        if not self.asset.current_owner:
            self.raise_user_error('no_asset_owner', self.asset.rec_name)

        project = Project.search([
               ('asset', '=', self.asset.id),
               # ('maintenance', '=', True),
               ])
        if project:
            self.work = project[0].id
            self.save()
            return

        project = Project()
        project.name =  self.contract.number
        project.company = self.contract.company
        project.party = self.asset.current_owner
        project.asset = self.asset
        project.type = 'project'
        project.invoice_product_type = 'service'
        project.maintenance = True
        project.start_date = self.contract.start_date
        project.end_date = self.contract.end_date if self.contract.end_date \
            else None
        project.contract_lines = []
        project.contract_lines += (self.id,)
        return project

    @classmethod
    def create_projects(cls, lines):
        pool = Pool()
        Project = pool.get('project.work')
        new_projects = {}
        for line in lines:
            print line
            if not line.work and line.asset and line.asset in new_projects:
                pass
                # new_projects[line.asset].contract_lines += (line,)
            else:
                project = line.get_projects()
                if project:
                    new_projects[line.asset] = project
        for key, val in new_projects.iteritems():
            print key, val

        for p in new_projects.values():
            print p._save_values

        if new_projects:
            Project.save(new_projects.values())