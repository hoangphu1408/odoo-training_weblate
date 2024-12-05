from odoo import models, fields

class BuyerOfferExportXlsxWizard(models.TransientModel):
    _name = 'buyer.offer.export.xlsx.wizard'
    _description = 'Buyer Offer XLSX Wizard'

    start_date = fields.Date(string="Date From", required=True)
    end_date = fields.Date(string="Date To", required=True)
    buyer_ids = fields.Many2many('res.partner', string="Buyers")

    def action_export_excel(self):
        # Gọi controller để xuất báo cáo
        buyer_ids = ','.join(map(str, self.buyer_ids.ids)) if self.buyer_ids else ''
        return {
            'type': 'ir.actions.act_url',
            'url': f'/estate/buyer_offer_report_xlsx?start_date={self.start_date}&end_date={self.end_date}&buyer_ids={buyer_ids}',
            'target': 'self',
        }
