from odoo import fields,models
from odoo.fields import Date


class ResUsers(models.Model):
    _inherit = "res.users"
    property_ids = fields.One2many(
        'estate.property',
        'salesperson_id',
        string="Properties",
        domain=[('date_availability','<=',Date.today())]
    )   