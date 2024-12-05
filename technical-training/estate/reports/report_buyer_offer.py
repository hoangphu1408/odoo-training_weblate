from odoo import api, fields, models,tools
from odoo.exceptions import UserError, ValidationError


class ReportBuyerOffer(models.Model):
    _name = "report.buyer.offer"
    _description = "Report Buyer Offer"
    _auto = False

    buyer_id = fields.Many2one(
        'res.partner', 
        string="Buyer", 
        readonly=False
    )
    email = fields.Char(
        related="buyer_id.email", 
        string="Email", 
        readonly=True
    )
    property_accepted = fields.Integer(
        string="Property Accepted", 
        readonly=True
    )
    property_sold = fields.Integer(
        string="Property Sold", 
        readonly=True
    )
    property_cancel = fields.Integer(
        string="Property Canceled", 
        readonly=True
    )
    offer_accepted = fields.Integer(
        string="Offer Accepted", 
        readonly=True
    )
    offer_rejected = fields.Integer(
        string="Offer Rejected", 
        readonly=True
    )
    max_price_offer = fields.Float(
        string="Max Price Offer", 
        readonly=True
    )
    min_price_offer = fields.Float(
        string="Min Price Offer", 
        readonly=True
    )

    def init(self):
        tools.drop_view_if_exists(self._cr, 'report_buyer_offer')
        self._cr.execute("""
            CREATE OR REPLACE VIEW report_buyer_offer AS (
                SELECT 
                    row_number() OVER () AS id,
                    rp.id AS buyer_id,
                         
                    (SELECT COUNT(*) 
                        FROM estate_property ep_sub 
                        WHERE ep_sub.buyer_id = rp.id 
                        AND ep_sub.state = 'offer_accepted') 
                        AS property_accepted,
                         
                    (SELECT COUNT(*) 
                        FROM estate_property ep_sub 
                        WHERE ep_sub.buyer_id = rp.id 
                        AND ep_sub.state = 'sold') 
                        AS property_sold,
                         
                    (SELECT COUNT(*) 
                        FROM estate_property ep_sub 
                        WHERE ep_sub.buyer_id = rp.id 
                        AND ep_sub.state = 'canceled') AS property_cancel,
                         
                    (SELECT COUNT(*) 
                        FROM estate_property_offer eo_sub 
                        WHERE eo_sub.property_id IN (
                            SELECT id FROM estate_property WHERE buyer_id = rp.id ) 
                        AND eo_sub.status = 'accepted') 
                        AS offer_accepted,
                         
                    (SELECT COUNT(*) 
                        FROM estate_property_offer eo_sub 
                        WHERE eo_sub.property_id IN (
                            SELECT id FROM estate_property WHERE buyer_id = rp.id ) 
                        AND eo_sub.status = 'rejected') 
                        AS offer_rejected,
                         
                    MAX(eo.price) AS max_price_offer,
                         
                    MIN(eo.price) AS min_price_offer
                FROM 
                    estate_property ep
                LEFT JOIN 
                    res_partner rp ON ep.buyer_id = rp.id
                LEFT JOIN 
                    estate_property_offer eo ON eo.property_id = ep.id
                GROUP BY 
                    rp.id
            )
        """)

    