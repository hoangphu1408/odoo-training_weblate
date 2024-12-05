import io
import xlsxwriter
from odoo import models


class EstatePropertyXlsxReport(models.AbstractModel):
    _name = 'report.estate.buyer_offers_xlsx_report'
    _inherit = 'report.report_xlsx.abstract'

    def create_excel_report(self, start_date, end_date, buyer_ids):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Buyer Offers')
        
        # Define formats
        bold = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#1F497D', 'font_color': '#FFFFFF'})
        header_format = workbook.add_format({'bold': True, 'bg_color': '#1F497D', 'font_color': '#FFFFFF', 'align': 'center'})
        currency_format = workbook.add_format({'num_format': '#,##0.00', 'align': 'center'})
        date_format = workbook.add_format({'align': 'center'})
        cell_centered = workbook.add_format({'align': 'center'})
        
        # Set column widths
        sheet.set_column('A:A', 20)  # Buyer name
        sheet.set_column('B:B', 25)  # Email
        sheet.set_column('C:H', 15)  # Other columns
        sheet.set_column('I:I', 18)  # Max Price Offer
        sheet.set_column('J:J', 18)  # Min Price Offer
        
        # Header Title
        sheet.merge_range('A5:I5', 'Report Buyer Offers', bold)
        sheet.write('C8', 'Date From', bold)
        sheet.write('D8', start_date.strftime('%d/%m/%Y'), date_format)
        sheet.write('E8', 'Date To', bold)
        sheet.write('F8', end_date.strftime('%d/%m/%Y'), date_format)

        # Column headers
        headers = ['Buyer', 'Email', 'Property Accepted', 'Property Sold', 'Property Cancel', 
                'Offer Accepted', 'Offer Rejected', 'Max Price Offer', 'Min Price Offer']
        for col, header in enumerate(headers):
            sheet.write(11, col, header, header_format)

        # Search for property and report data
    #     domain = [
    #     ('date_availability', '>=', start_date),
    #     ('date_availability', '<=', end_date),
    # ]
    #     if buyer_id:
    #         domain.append(('buyer_id', '=', buyer_id))

    #     buyer_ids = self.env['estate.property'].search(domain).mapped('buyer_id').ids
        
    #     records = self.env['report.buyer.offer'].search([
    #         ('buyer_id', 'in', buyer_ids)
    #     ])


    # SQL Query to retrieve data within the date range and optional buyer_id
        query = """
            SELECT
                rp.name AS buyer_name,
                rp.email AS buyer_email,
                (SELECT COUNT(*) FROM estate_property ep_sub WHERE ep_sub.buyer_id = rp.id AND ep_sub.state = 'offer_accepted' AND ep_sub.date_availability BETWEEN %s AND %s) AS property_accepted,
                (SELECT COUNT(*) FROM estate_property ep_sub WHERE ep_sub.buyer_id = rp.id AND ep_sub.state = 'sold' AND ep_sub.date_availability BETWEEN %s AND %s) AS property_sold,
                (SELECT COUNT(*) FROM estate_property ep_sub WHERE ep_sub.buyer_id = rp.id AND ep_sub.state = 'canceled' AND ep_sub.date_availability BETWEEN %s AND %s) AS property_canceled,
                (SELECT COUNT(*) FROM estate_property_offer eo_sub WHERE eo_sub.property_id IN (SELECT id FROM estate_property WHERE buyer_id = rp.id AND date_availability BETWEEN %s AND %s) AND eo_sub.status = 'accepted') AS offer_accepted,
                (SELECT COUNT(*) FROM estate_property_offer eo_sub WHERE eo_sub.property_id IN (SELECT id FROM estate_property WHERE buyer_id = rp.id AND date_availability BETWEEN %s AND %s) AND eo_sub.status = 'rejected') AS offer_rejected,
                MAX(eo.price) AS max_price_offer,
                MIN(eo.price) AS min_price_offer
            FROM
                res_partner rp
            LEFT JOIN
                estate_property ep ON ep.buyer_id = rp.id
            LEFT JOIN
                estate_property_offer eo ON eo.property_id = ep.id
            WHERE
                ep.date_availability BETWEEN %s AND %s
                {buyer_filter}
            GROUP BY
                rp.id
        """

        # Add filter for multiple buyer_ids if provided
        buyer_filter = ""
        params = [start_date, end_date, start_date, end_date, start_date, end_date, start_date, end_date, start_date, end_date, start_date, end_date]
        if buyer_ids:
            # Prepare a placeholder for each buyer_id in the IN clause
            buyer_filter = "AND rp.id IN ({})".format(','.join(['%s'] * len(buyer_ids)))
            params.extend(buyer_ids)

        # Execute query
        self.env.cr.execute(query.format(buyer_filter=buyer_filter), tuple(params))
        results = self.env.cr.fetchall()


        # Write data to Excel
        row = 12  # Starting row for data entries
        for result in results:
            sheet.write(row, 0, result[0] or '', cell_centered)  # Buyer name
            sheet.write(row, 1, result[1] or '', cell_centered)  # Email
            sheet.write(row, 2, result[2] or 0, cell_centered)   # Property Accepted
            sheet.write(row, 3, result[3] or 0, cell_centered)   # Property Sold
            sheet.write(row, 4, result[4] or 0, cell_centered)   # Property Canceled
            sheet.write(row, 5, result[5] or 0, cell_centered)   # Offer Accepted
            sheet.write(row, 6, result[6] or 0, cell_centered)   # Offer Rejected
            sheet.write(row, 7, result[7] or 0, currency_format) # Max Price Offer
            sheet.write(row, 8, result[8] or 0, currency_format) # Min Price Offer
            row += 1
        # Close workbook and prepare output
        workbook.close()
        output.seek(0)
        
        return output.getvalue()