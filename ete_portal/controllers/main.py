
from collections import OrderedDict
from operator import itemgetter
from odoo import fields
from odoo import http
from odoo.http import request
from odoo.tools import date_utils, groupby as groupbyelem
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError



class WebsiteMyAccount(CustomerPortal):

    def get_domain_my_results(self, user):
        teacher = request.env['school.teacher'].search([('user_id', '=', user.id)],
                                                limit=1)
        return [
            ('teacher_id', '=', teacher and teacher.id or False),
        ]

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        # Leaves = request.env['hr.leave']
        if 'result_count' in counters:
            # values['leave_count'] = Leaves.search_count(self.get_domain_my_leaves(request.env.user)) if Leaves.check_access_rights('read', raise_exception=False) else 0
            values['result_count'] = '1'
        return values
    

    @http.route(['/result/class_infos/<int:standard>'], type='json', auth="public", methods=['POST'], website=True)
    def class_infos(self, standard, **kw):
        standard = request.env['school.standard'].sudo().browse(standard)
        return dict(
            students=[(st.id, st.name) for st in standard.get_result_class_students()],
            subjects=[(sub.id, sub.name) for sub in standard.get_result_class_subjects()],
            surveys=[(sur.id, sur.title) for sur in standard.get_result_class_survey()],
        )
        
    # @http.route(['/result/subject_infos/<int:subject>'], type='json', auth="public", methods=['POST'], website=True)
    # def subject_infos(self, subject, **kw):
    #     subject = request.env['subject.subject'].sudo().browse(subject)
    #     return dict(
    #         students=[(st.id, st.name) for st in standard.get_result_class_students()],
    #         subjects=[(sub.id, sub.name) for sub in standard.get_result_class_subjects()],
    #         surveys=[(sur.id, sur.title) for sur in standard.get_result_class_survey()],
    #     )

    @http.route(['/result', '/result/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_results(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, groupby='none', **kw):
        values = self._prepare_portal_layout_values()
        result_input = request.env['survey.user_input']
        result_input_sudo = request.env['survey.user_input'].sudo()
        domain = self.get_domain_my_results(request.env.user)

        # holiday_domain=([('virtual_remaining_leaves', '>', 0)])
        # holiday_type_ids = request.env['hr.leave.type'].search(holiday_domain)
        School_obj = request.env['school.school']
        Standard_obj = request.env['standard.standard']
        Student_obj = request.env['student.student']
        Subject_obj = request.env['subject.subject']
        Survey_obj = request.env['survey.survey']
        SchoolStd_obj = request.env['school.standard']
        # user = request.env.user
        # emp = request.env['hr.employee'].search([('user_id', '=', user.id)],
        #                                         limit=1)
        # values.update({
        #     'holiday_types':holiday_type_ids.with_context({'employee_id':emp and emp.id or False}).name_get()})
        # # fileter  By
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'Passed': {'label': _('Passed'), 'domain': [('scoring_success', '=', True)]},
            'Failed': {'label': _('Failed'), 'domain': [('scoring_success', '=', False)]},
            # 'refuse': {'label': _('Refused'), 'domain': [('state', '=', 'refuse')]},
            # 'validate1': {'label': _('Second Approval'), 'domain': [('state', '=', 'validate1')]},
            # 'validate': {'label': _('Approved'), 'domain': [('state', '=', 'validate')]},
        }
        # # sort By
        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'partner_id': {'label': _('Name'), 'order': 'partner_id'},
        }
        # # group By
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'Exam': {'input': 'Exam', 'label': _('Exam')},
        }
        # # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        # # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']
        # if date_begin and date_end:
        #     domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        # pager
        # result_count = HrLeave.search_count(domain)
        result_count = 1
        pager = request.website.pager(
            url="/result",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby},
            total=result_count,
            page=page,
            step=self._items_per_page
        )
        # # default groupby
        if groupby == 'exam':
            order = "survey_id, %s" % order
        # content according to pager and archive selected
        
        user_teacher = request.env['school.teacher'].sudo().search([('user_id', '=', request.env.user.id)],limit=1)
        school = School_obj.search([('id','=', user_teacher.school_id.id)])
        # standard = user_teacher.school_id.standards
        standard = user_teacher.standard_ids
        student = standard.student_ids
        subject = Subject_obj.search([])
        survey = Survey_obj.search([])
        Results = result_input.sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        if groupby == 'none':
            grouped_result = []
            if Results:
                grouped_result = [Results]
        else:
            grouped_result = [result_input_sudo.concat(*g) for k, g in groupbyelem(Results, itemgetter('survey_id'))]
        values.update({
            'date': date_begin,
            'results': Results,
            'schools': school,
            'standards': standard,
            'students': student,
            'subjects': subject,
            'surveys': survey,
            'grouped_result': grouped_result,
            'page_name': 'result',
            'default_url': '/result',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'searchbar_groupby': searchbar_groupby,
            'sortby': sortby,
            'groupby': groupby,
            'filterby': filterby,
        })
        return request.render("ete_portal.portal_my_result_details", values)

    # @http.route(['''/my/timeoff/<model('hr.leave'):timeoff>'''], type='http', auth="user", website=True)
    # def portal_my_timeoff(self, timeoff, **kw):
    #     user = request.env.user
    #     emp = request.env['hr.employee'].search([('user_id', '=', user.id)],
    #                                             limit=1)
    #     holiday_domain=([('virtual_remaining_leaves', '>', 0),
    #                      # ('requires_allocation', 'in', ['yes']),
    #                      # ('max_leaves', '>', '0')
    #                      ])
    #     holiday_type_ids = request.env['hr.leave.type'].search(holiday_domain)
    #     return request.render(
    #         "portal_timeoff.portal_my_timeoff", {
    #             'timeoff': timeoff,
    #             'holiday_types':holiday_type_ids.with_context({'employee_id':emp and emp.id or False}).name_get(),
    #             'emp_id': emp and emp.id or False,
    #             'page_name': 'leave_details',
    #         })

    # @http.route(['/my/leaves/summary'], type='http', auth="user", website=True)
    # def leaves_summary(self):
    #     get_days_all_request = request.env['hr.leave.type'].get_allocation_data_request()
    #     return request.render(
    #         "portal_timeoff.my_leaves_summary",{
    #             'timeoffs':get_days_all_request})


    @http.route('/get_survey_data', type='json', auth='user')
    def get_survey_data(self, survey_id):
        if not survey_id:
            raise ValidationError("Survey ID is required.")

        survey = http.request.env['survey.survey'].sudo().search([('id', '=', int(survey_id))], limit=1)

        if not survey:
            raise ValidationError("Survey not found.")

        question_and_page_data = {}
        for question_and_page in survey.question_and_page_ids:
            question_and_page_data[question_and_page.id] = {
                'title': question_and_page.title,
                'question_type': question_and_page.question_type,
                'suggested_answer_ids': [answer.value for answer in question_and_page.suggested_answer_ids]
                # 'suggested_answer_ids': question_and_page.suggested_answer_ids.ids
                # Add other fields as needed
            }

        return {
            'question_and_page_data': question_and_page_data,
            'Survey': {
                'id': survey.id,
                'name': survey.title,
                'option_count': survey.option_count
                # Add other survey fields as needed
            }
            # Add other fields as needed
        }
