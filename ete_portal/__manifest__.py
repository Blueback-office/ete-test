# See LICENSE file for full copyright and licensing details.

{
    'name' : 'ETE Portal',
    'category' : 'Website',
    'version' : '17.0.1.0.0',
    'summary': 'ETE Portal',
    'description': """
        ETE Portal 
    """,
    'depends': [
        'website',
        'portal',
        'exam',
        'survey'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/survey_user_input.xml',
        # 'views/relate_emp_portal_user.xml',
        'views/templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'ete_portal/static/src/js/portal_add_result.js',
        ]
    },
    'author': 'Serpent Consulting Services',
    'website': 'https://www.serpentcs.com',
    'installable': True,
}

