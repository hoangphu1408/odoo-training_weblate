{
    'name': 'Estate',
    'version': '1.0',
    'summary': 'Module Estate',
    'description': """
Estate Property
=================
Module Estate provide management solution.
""",
    'category': 'Estate',
    'depends': ['base',
                'mail',
                'report_xlsx'],
    'data': [
        'data/res_groups.xml',
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_offer_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_user_views.xml',
        "wizards/report_buyer_offers_xlsx.xml",
        'reports/report_buyer_offer_views.xml',
        'reports/report.xml',
        'views/estate_menu.xml', 
    ],
    
    
    'installable': True,
    'application': True,
}
