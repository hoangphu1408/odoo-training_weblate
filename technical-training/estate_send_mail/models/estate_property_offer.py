from odoo import api, fields, models, _



class EstatePropertyOffer(models.Model):
    _inherit = 'estate.property.offer'

    user_accept = fields.Many2one(
        'res.users',
        string="User Accept",
        readonly=True,
    )
    user_reject = fields.Many2one(
        'res.users',
        string="User Reject",
        readonly=True,
    )

    def action_accept(self):
        super(EstatePropertyOffer, self).action_accept()
        self.user_accept = self.env.user
        self.action_send_offer_mail()

    def action_reject(self):
        super(EstatePropertyOffer, self).action_reject()
        self.user_reject = self.env.user

    def action_send_offer_mail(self):
        template_id = self.env.ref('estate_send_mail.email_template_offer_accepted').id
        self.env['mail.template'].browse(template_id).send_mail(self.id)
