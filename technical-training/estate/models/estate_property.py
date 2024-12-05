from datetime import timedelta
from odoo import api, fields, models,_
from odoo.exceptions import UserError, ValidationError


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Property"
    _inherit = ["mail.thread", "mail.activity.mixin"] 

    name = fields.Char(string="Name", required=True,tracking=True)
    description = fields.Text(string="Description")
    postcode = fields.Char(string="Post Code")
    date_availability = fields.Date(
        string="Date Availability", 
        store=True,
        copy=False, 
        default=lambda self: fields.Date.today() + timedelta(days=90)
    )
    expected_price = fields.Float(string="Expected Price", required=True)
    selling_price = fields.Float(string="Selling Price", readonly=True, copy=False)
    bed_room = fields.Integer(string="Bed Room", default=2)
    living_area = fields.Integer(string="Living Area")
    farcades = fields.Integer(string="Farcades")
    garage = fields.Boolean(string="Garage")
    garden = fields.Boolean(string="Garden")
    garden_area = fields.Integer(string ="Garden Area")
    garden_orientation = fields.Selection(
        [
            ("north", "North"),
            ("south", "South"),
            ('east', "East"),
            ("west", "West")
        ],
        string="Garden Orientation"
    )
    active = fields.Boolean(
        string="Active", 
        default=True
    )
    state = fields.Selection(
        [
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('canceled', 'Canceled')
        ],
        string="State",
        required=True,
        copy=False,
        default='new',
        tracking=True
        
    )
    property_type_id = fields.Many2one(
        "estate.property.type", 
        string="Property Type", 
        ondelete="set null"
    )
    salesperson_id = fields.Many2one(
        'res.users', 
        string="Salesperson", 
        default=lambda self: self.env.user
    )
    buyer_id = fields.Many2one(
        'res.partner', 
        string="Buyer", 
        copy=False
    )
    offer_ids = fields.One2many(
        'estate.property.offer', 
        'property_id', 
        string="Offers"
    )
    tag_ids = fields.Many2many(
        'estate.property.tag',         
        'estate_property_tag_rel',      
        'property_id',                  
        'tag_id',                       
        string="Tags"
    )
    total_area = fields.Integer(
        string="Total Area",
        compute="_compute_total_area",
        store=True
    )
    best_price = fields.Float(
        string="Best Price",
        compute="_compute_best_price",
        store=True
    )
    code = fields.Char(
        string="Code",
        readonly=True,
        copy=False,
        default="New"
    )


    _sql_constraints = [
        ('check_expected_price_positive', 'CHECK(expected_price > 0)', 'The expected price must be strictly positive'),
        ('check_selling_price_non_negative', 'CHECK(selling_price >= 0)', 'The selling price must be positive'),
        ('check_offer_price_positive', 'CHECK(price > 0)', 'The offer price must be strictly positive')
    ]

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = (record.living_area or 0) + (record.garden_area or 0)

    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for record in self:
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped('price'))
            else:
                record.best_price = 0
                
    @api.onchange('garden')
    def onchange_garden(self):
        if self.garden:
            self.garden_area = 50
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = False

    @api.constrains('date_availability')
    def _check_date_availability(self):
        for record in self:
            if record.date_availability and record.date_availability < fields.Date.today():
                raise ValidationError("Date Availability cannot be set to a date prior to today.")
            
    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price_above_90_percent(self):
        for record in self:
            if record.selling_price > 0 and record.selling_price < 0.9 * record.expected_price:
                raise ValidationError("The selling price cannot be lower than 90% of the expected price")
            
    @api.model_create_multi
    def create(self,vals_list):
        for vals in vals_list:
            if not vals.get('code') or vals['code'] == "New":
                vals['code'] = self.env['ir.sequence'].next_by_code('estate.property.code')
        return super().create(vals_list)
    

    def assign_sequence_to_old_records(self):
        records_to_update = self.search([('code', '=', "New")])
        for record in records_to_update:
            record.code = self.env['ir.sequence'].next_by_code('estate.property.code')

    def action_cancel(self):
        if self.state == 'sold':
            raise UserError(_("A sold property can not be cancelled"))
        self.state = "canceled"
        
    def action_sold(self):
        if self.state == "canceled":
            raise UserError(("A sold property can not be sold"))
        self.state = "sold"
    
    
    def unlink(self):
        for record in self:
            if record.state not in ['new', 'canceled']:
                raise UserError("You can only delete properties in 'New' or 'Canceled' state")
        return super(EstateProperty, self).unlink()

 