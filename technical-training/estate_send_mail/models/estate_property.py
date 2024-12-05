from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import re

class EstatePropertyInherited(models.Model):
    _inherit = 'estate.property'

    buyer_email = fields.Char(
        string="Buyer Email",
        required=True,
        store=True,
        default="none@mail.com"
    )
    user_sold = fields.Many2one(
        'res.users',
        string="User Sold",
        readonly=True,
    )

    
    @api.onchange('buyer_id')
    def _load_buyer_email(self):

        for record in self:
            print("Hello ",record.buyer_id.email)
            if record.buyer_id:
                record.buyer_email = record.buyer_id.email


    @api.constrains('buyer_email')
    def _check_buyer_email_format(self):
        for record in self:
            if record.buyer_email and not re.match(r"[^@]+@[^@]+\.[^@]+", record.buyer_email):
                raise ValidationError(_("Please enter a valid email address for Buyer Email."))

    def action_send_mail(self):
        template_id = self.env.ref('estate_send_mail.email_template_property_sold').id
        self.env['mail.template'].browse(template_id).send_mail(self.id)

    def action_sold(self):
        super(EstatePropertyInherited, self).action_sold()
        self.user_sold = self.env.user
        
        self.action_send_mail()

