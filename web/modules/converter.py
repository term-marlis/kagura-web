import swagger_client as sw

from web.modules.form import ProjectBasicForm, ProjectItemForm, ProjectDetailForm, ProjectReportForm, ProjectFaqForm, \
    ProjectItemQuestionForm


def project_form_to_api_project(basic_form: ProjectBasicForm) -> sw.Project:
    """TODO プロジェクト基本情報: Form -> API"""
    project = sw.Project()
    project.title = basic_form.title.data
    project.summary = basic_form.summary.data
    project.type = basic_form.type.data
    project.target_amount = basic_form.target_amount.data
    project.open_amount = basic_form.open_amount.data
    project.start_time = '%s %s' % (basic_form.start_date.data, basic_form.start_time.data,)
    project.end_time = '%s %s' % (basic_form.end_date.data, basic_form.end_time.data,)
    project.main_color = basic_form.main_color.data
    project.accent_color = basic_form.accent_color.data.hex
    return project


def api_project_to_project_form(project: sw.Project) -> ProjectBasicForm:
    """プロジェクト基本情報: API -> Form"""
    basic_form = ProjectBasicForm()
    basic_form.title.data = project.title
    basic_form.summary.data = project.summary if project.summary else ''
    basic_form.type.data = project.type
    basic_form.target_amount.data = project.target_amount
    basic_form.open_amount.data = project.open_amount
    basic_form.start_date.data = project.start_time.date()
    basic_form.start_time.data = project.start_time.time()
    basic_form.end_date.data = project.end_time.date()
    basic_form.end_time.data = project.end_time.time()
    basic_form.main_color.data = project.main_color
    basic_form.accent_color.data = project.accent_color
    return basic_form


def item_form_to_api_item(item_form: ProjectItemForm) -> sw.ProjectItem:
    """プロジェクト/アイテム: Form -> API"""
    item = sw.ProjectItem()
    item.name = item_form.name.data
    item.description = item_form.description.data
    item.price = item_form.price.data
    item.deliver_date = item_form.deliver_date.data
    item.limit = int(item_form.limit.data) if item_form.limit.data else -1
    item.limit_user = int(item_form.limit_user.data) if item_form.limit_user.data else -1
    item.shipping = item_form.shipping.data
    return item


def api_item_to_project_item_form(item: sw.ProjectItem) -> ProjectItemForm:
    """プロジェクト/アイテム: API -> Form"""
    item_form = ProjectItemForm()
    item_form.name.data = item.name
    item_form.description.data = item.description
    item_form.price.data = item.price
    item_form.deliver_date.data = item.deliver_date
    item_form.limit.data = None if item.limit is -1 else str(item.limit)
    item_form.limit_user.data = None if item.limit_user is -1 else str(item.limit_user)
    item_form.shipping.data = item.shipping
    item_form.image.data = item.image
    return item_form


def item_question_form_to_api_item_question(question_form: ProjectItemQuestionForm) -> sw.ProjectItemQuestion:
    """プロジェクト/アイテム質問: Form -> API"""
    question = sw.ProjectItemQuestion()
    question.id = question_form.question_id.data if question_form.question_id.data else None
    question.name = question_form.description.data
    question.description = question_form.description.data
    question.type = question_form.type.data
    question.format = question_form.format.data
    question.is_required = question_form.required.data
    return question


def api_project_to_project_detail_form(project: sw.Project) -> ProjectDetailForm:
    """プロジェクト詳細: API -> Form"""
    detail_form = ProjectDetailForm()
    detail_form.note.data = project.note
    detail_form.detail.data = project.detail
    return detail_form


def project_detail_form_to_api_project(detail_form: ProjectDetailForm) -> sw.Project:
    """プロジェクト詳細: Form -> API"""
    project_ = sw.Project()
    project_.note = detail_form.note.data
    project_.detail = detail_form.detail.data
    return project_


def api_project_faq_to_project_faq_form(faq: sw.ProjectFaq) -> ProjectFaqForm:
    """プロジェクトFAQ: API -> Form"""
    faq_form = ProjectFaqForm()
    faq_form.question.data = faq.question
    faq_form.answer.data = faq.answer
    return faq_form


def project_faq_form_to_api_project_faq(faq_form: ProjectFaqForm) -> sw.ProjectFaq:
    """プロジェクトFAQ: Form -> API"""
    faq = sw.ProjectFaq()
    faq.question = faq_form.question.data
    faq.answer = faq_form.answer.data
    return faq


def report_form_to_api_report(report_form: ProjectReportForm) -> sw.ProjectReport:
    """プロジェクト活動報告: Form -> API"""
    report = sw.ProjectReport()
    report.title = report_form.title.data
    report.detail = report_form.report.data
    report.accessible = report_form.accessible.data
    report.notification = report_form.notification.data
    return report


def api_report_to_report_form(report: sw.ProjectReport) -> ProjectReportForm:
    """プロジェクト活動報告: API -> Form"""
    report_form = ProjectReportForm()
    report_form.title.data = report.title
    report_form.report.data = report.detail
    report_form.accessible.data = report.accessible
    return report_form
