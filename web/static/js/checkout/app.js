$.ajaxSetup({
  beforeSend: function (xhr, settings) {
    if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
      xhr.setRequestHeader("X-CSRFToken", $('#csrf_token').val());
    }
  }
});
var checkoutView = new peach.view.CheckoutView();
function generate_token(resp) {
  checkoutView.save_credit_token(resp);
}
function active_step(name) {
  $('.step').each(function () {
    var step = $(this);
    if (step.hasClass(name)) {
      step.removeClass('disabled');
      step.addClass('active');
    } else {
      step.removeClass('active');
      step.addClass('disabled');
    }
  });
  $('.step_name').each(function () {
    var step = $(this);
    if (step.hasClass(name)) {
      step.show();
    } else {
      step.hide();
    }
  });
}