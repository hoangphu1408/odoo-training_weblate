from odoo import api, fields, models
from odoo.exceptions import ValidationError


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate Property Type"
    _rec_name = "name"

    name = fields.Char(
        string="Name", 
        required=True, 
        unique=True
    )
    offer_ids = fields.One2many('estate.property.offer', 'property_type_id', string=("Offers"))
    offer_count = fields.Integer(string=("Offer Count"), compute="_compute_offer_count")
    property_ids = fields.One2many(
        'estate.property', 
        'property_type_id',
        string="Properties", 
    )
    
    _sql_constraints = [
        ('name_unique', 'UNIQUE(LOWER(name))', 'The property type name must be unique')
    ]


    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for rec in self:
            rec.offer_count = len(rec.offer_ids)

    @api.constrains('name')
    def _check_name_unique(self):
        for record in self:
            existing = self.search([('name', '=ilike', record.name)], limit=1)
            if existing and existing.id != record.id:
                raise ValidationError(_("The property type name must be unique"))
            
    # def action_open_offer_ids(self):
    #     return {
    #         "name": ("Offers"),
    #         "type": "ir.actions.act_window",
    #         "view_mode": "tree,form",
    #         "res_model": "estate.property.offer",
    #         "target": "current",
    #         "domain": [("property_type_id", "=", self.id)],
    #         "context": {"default_property_type_id": self.id},
    #     }