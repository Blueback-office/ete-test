from odoo import fields, models


class SurveySurvey(models.Model):
    """Defining a Exam information."""

    _inherit = "survey.survey"

    is_ete_survey = fields.Boolean()
    school_id = fields.Many2one('school.school', 'School')
    teacher_id = fields.Many2one('school.teacher', 'Teacher')
    class_id = fields.Many2one('school.standard', 'Class')
    standard_id = fields.Many2one('standard.standard', 'Standard')
    academic_year_id = fields.Many2one("academic.year", 'Academic Year', help="Select Academic Year")
    s_exam_id = fields.Many2one("exam.exam", "Examination", help="Select Exam")
    subject_id = fields.Many2one("subject.subject")
    exam_type = fields.Selection([
        ("two", "Two Way Correction"),
        ("four", "Four Way Correction"),
        ("online", "Online")
    ])
    option_count = fields.Char(string="No of options", placeholder="2 or 4", default="2")


class SurveyUserInput(models.Model):
    """Defining a Exam information."""

    _inherit = "survey.user_input"

    class_id = fields.Many2one(related='survey_id.class_id')
    standard_id = fields.Many2one(related='survey_id.standard_id')
    subject_id = fields.Many2one(related='survey_id.subject_id')


class SurveyQuestion(models.Model):
    """Defining a Subject Category."""

    _inherit = 'survey.question'

    subject_id = fields.Many2one(related='survey_id.subject_id',store=True)
    sub_category_id = fields.Many2one('sub.category',domain=[])
