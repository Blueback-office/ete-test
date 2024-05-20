/** @odoo-module **/
import { _t } from "@web/core/l10n/translation";
import publicWidget from "@web/legacy/js/public/public_widget";
import { parseDate, formatDate, serializeDate } from "@web/core/l10n/dates";
const { DateTime } = luxon;
import { jsonrpc } from "@web/core/network/rpc_service";


publicWidget.registry.PortalAddResult = publicWidget.Widget.extend({
    selector: '',
    selector: '#wrapwrap:has(.modal_new_result, .new_result_form)',
    events: {
        'change #new-result-dialog .exam_select': '_onChangeExam',
        'click .new_result_confirm': '_onNewResultConfirm',
        'change #new-result-dialog .school_select': '_onChangeSchool',
        'change #new-result-dialog .class_select': '_onChangeClass',
        'change #new-result-dialog .student_select': '_onChangeStudent',
        'change #new-result-dialog .subject_select': '_onChangeSubject',
    },

    init() {
        this._super(...arguments);
        this.orm = this.bindService("orm");
        this.rpc = this.bindService("rpc");

    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {jQuery} $btn
     * @param {function} callback
     * @returns {Promise}
     */
    _buttonExec: function ($btn, callback) {
        // TODO remove once the automatic system which does this lands in master
        $btn.prop('disabled', true);
        return callback.call(this).catch(function (e) {
            $btn.prop('disabled', false);
            if (e instanceof Error) {
                return Promise.reject(e);
            }
        });
    },

    

    _addSurveyResult: function () {
        var self = this;
        var params = {};
        var $parent = this.$el.find('.o_survey_exam_form_choice')
        this.$('[t-att-data-question-type]').each(function () {
            var $input = $(this);
            var $questionWrapper = $input.closest(".o_survey_exam_form_choice");
            var questionId = $questionWrapper.attr('id');
            params = self._prepareSubmitChoices(params, $(this), questionId);
        });
        
        return this.orm.call("survey.user_input", "create_portal_result", [{
            class_id: parseInt($('.new_result_form .class_select').find(':selected').attr('value')),
            school_id: parseInt($('.new_result_form .school_select').find(':selected').attr('value')),
            student_id: parseInt($('.new_result_form .student_select').find(':selected').attr('value')),
            subject_id: parseInt($('.new_result_form .subject_select').find(':selected').attr('value')),
            survey_id: parseInt($('.new_result_form .exam_select').find(':selected').attr('value')),
            question_id : params
        }]).then(function (response) {
            if (response.errors) {
                $('#new-result-dialog .alert').remove();
                $('#new-result-dialog div:first').prepend('<div class="alert alert-danger">' + response.errors + '</div>');
                return Promise.reject(response);
            } else {
                window.location.reload();
                /*window.location = '/my/opportunity/' + response.id;*/
            }
        });
    },
    
    _prepareSubmitChoices: function (params, $parent, questionId) {
        var self = this;
        $parent.find('input:checked').each(function () {
            if (this.value !== '-1') {
                params = self._prepareSubmitAnswer(params, questionId, this.value);
            }
        });
        return params;
    },

     _prepareSubmitAnswer: function (params, questionId, value) {
        if (questionId in params) {
            if (params[questionId].constructor === Array) {
                params[questionId].push(value);
            } else {
                params[questionId] = [params[questionId], value];
            }
        } else {
            params[questionId] = value;
        }
        return params;
    },

    /**
     * @private
     * @param {Event} ev
     */
    _onNewResultConfirm: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        this._buttonExec($(ev.currentTarget), this._addSurveyResult);
    },

    _onChangeExam: function (ev) {
        var surveyId = ev.target.value;
        this.rpc('/get_survey_data', {
            survey_id: surveyId
        }).then(function (data) {
            console.log("data",data);
            var surveyData = '';
            for (var questionId in data.question_and_page_data) {
                var questionData = data.question_and_page_data[questionId];
                var OptionCount = data.Survey;
                var count = parseInt(OptionCount['option_count'])
                
                surveyData += '<div class="mb-3 o_survey_exam_form_choice" id="' + questionId + '">';
                surveyData += '<div class="question col-auto form-check-inline col-4" t-att-id="' + questionId + '">';
                surveyData += '<label class="col-form-label" for="question_' + questionId + '">' + questionData.title + '</label>';
                surveyData += '</div>';
                
                if (questionData.question_type === 'simple_choice') {
                    surveyData += '<div class="form-check-inline" t-att-data-question-type="'+ questionData.question_type +'" t-att-data-name="'+ questionId +'">';
                    for (let i = 1; i <= count; i++) {
                        surveyData += '<div class="form-check form-check-inline">';
                        surveyData += '<input class="form-check-input" type="radio" name="option_' + questionId + '" id="optionid'+i+'_'+ questionId +'" value="'+i+'"/>';
                        surveyData += '<label class="form-check-label" for="optionid'+i+'_' + questionId + '">'+ i +'</label>';
                        surveyData += '</div>';
                    }
                    surveyData += '</div>';
                }
                /*surveyData += '<div class="form-check form-check-inline">';
                surveyData += '<input class="form-check-input" type="radio" name="option_' + questionId + '" id="option1id_'+ questionId +'" value="1"/>';
                surveyData += '<label class="form-check-label" for="option1id_' + questionId + '">1</label>';
                surveyData += '</div>';
                
                surveyData += '<div class="form-check form-check-inline">';
                surveyData += '<input class="form-check-input" type="radio" name="option_' + questionId + '" id="option2id_'+ questionId +'" value="2"/>';
                surveyData += '<label class="form-check-label" for="option2id_' + questionId + '">2</label>';
                surveyData += '</div>';*/
                
                // Generate input elements based on question type
                /*if (!questionData.question_type) {
                    surveyData += '<input type="text" name="question_' + questionId + '">';
                } else if (questionData.question_type === 'simple_choice') {
                    for (var i = 0; i < questionData.suggested_answer_ids.length; i++) {
                        surveyData += '<input type="radio" name="question_' + questionId + '" value="' + questionData.suggested_answer_ids[i] + '">' + questionData.suggested_answer_ids[i] + '<br>';
                    }
                } else if (questionData.question_type === "multiple_choice") {
                    for (var i = 0; i < questionData.suggested_answer_ids.length; i++) {
                        surveyData += '<input type="checkbox" name="question_' + questionId + '" value="' + questionData.suggested_answer_ids[i] + '">' + questionData.suggested_answer_ids[i] + '<br>';
                    }
                }*/
                
                surveyData += '</div>';
            }
            $('.get_survey').html(surveyData);
        });
    },
    _onChangeSchool: function (ev) {
        console.log("_onChangeSchool");
    },
    _onChangeClass: function (ev) {
        console.log("_onChangeClass");
    },
    _onChangeStudent: function (ev) {
        console.log("_onChangeStudent");
    },
    _onChangeSubject: function (ev) {
        console.log("_onChangeSubject");
    },
    
    
});
