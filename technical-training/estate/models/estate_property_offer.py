from datetime import timedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"

    price = fields.Float(
        string="Price", 
        required=True
    )
    status = fields.Selection(
        [('accepted', 'Accepted'), ('refused', 'Refused')],
        string="Status", 
        copy=False
    )
    partner_id = fields.Many2one(
        'res.partner', 
        string="Partner", 
        required=True
    )
    property_id = fields.Many2one(
        'estate.property', 
        string="Property", 
        required=True
    )
    property_type_id = fields.Many2one(
        related="property_id.property_type_id",
        store=True,
        string="Property Type"
    )
    validity = fields.Integer(
        string="Validity (days)", 
        default=7
    )
    date_deadline = fields.Date(
        string="Deadline", 
        compute="_compute_date_deadline", 
        store=True
    )
    
    @api.depends('property_id.state')
    def _compute_restricted_state(self):
        for record in self:
            record.restricted_state = record.property_id.state in ['offer_accepted', 'sold', 'canceled']


    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline = record.create_date + timedelta(days=record.validity)
            else:
                record.date_deadline = fields.Date.today() + timedelta(days=record.validity)

    def update(self, values):
        for record in self:
            if record.status=="accepted":
                raise ValidationError("Can not Edit Offer Accepted")
        return super().update(values)
    def unlink(self):
        for record in self:
            if record.status=="accepted":
                raise ValidationError("Can not Delete Offer Accepted") 
        return super().unlink()
    
    def action_accept(self):
        if self.property_id.state == "sold":
            raise UserError("This property has already been sold")
        if self.status == "refused":
            raise UserError("Offer already Refused.Please make another offer")
        
        self.status = 'accepted'
        accepted_offers = self.property_id.offer_ids.filtered(lambda o: o.status == 'accepted')
        
      

        total_selling_price = sum(offer.price for offer in accepted_offers)
        
        self.property_id.write({
            'buyer_id' : self.env.user.partner_id.id,
            'selling_price': total_selling_price,
        })
        self.property_id._load_buyer_email()

    def action_refuse(self):
        self.status = "refused"
    
    @api.model
    def create(self, vals):
        
        property = self.env['estate.property'].browse(vals['property_id'])
        if property.state == 'new':
            property.state = 'offer_received'
        
        
        if property.best_price and vals['price'] < property.best_price:
            raise ValidationError("You cannot create an offer lower than the existing best offer price")
        
        return super(EstatePropertyOffer, self).create(vals)