{
    'name': 'Estate Send Mail',
    'version': '1.0',
    'summary': 'Module Estate Send Mail',
    'description': """
Estate Property
=================
Module Estate provide management solution.
""",
    'category': 'Estate',
    'depends': ['base',
                'mail'],
    'data': [
        'views/estate_property_inherited_views.xml',
        'data/estate_send_mail_data.xml',
    ],
    'installable': True,
    'application': True,
}
