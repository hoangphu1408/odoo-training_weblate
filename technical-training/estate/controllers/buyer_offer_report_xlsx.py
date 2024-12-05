from odoo import http
from odoo.http import request
from datetime import datetime

class BuyerOfferReportController(http.Controller):

    @http.route('/estate/buyer_offer_report_xlsx', type='http', auth='user', csrf=False)
    def generate_buyer_offer_report_xlsx(self, start_date, end_date,buyer_ids):
        
       start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
       end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

       
       buyer_ids = [int(bid) for bid in buyer_ids.split(',')] if buyer_ids else []
        
       

       report_model = request.env['report.estate.buyer_offers_xlsx_report']
       file_content = report_model.create_excel_report(start_date, end_date,buyer_ids)

        
       headers = [
            ('Content-Disposition', 'attachment; filename="Estate_Property_Buyer_Offers_Report.xlsx"'),
            ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        ]

       return request.make_response(file_content, headers=headers)
