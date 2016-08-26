"use strict";
var peach = {};
peach.view = peach.view || {};
peach.view.CheckoutView = Backbone.View.extend({
  el: '#checkout',
  template: null,
  model: {
    view: 'select',
    payment_type: 'credit'
  },
  events: {
    'click .cancel': 'cancel_checkout',
    'click .next': 'next_page',
    'click .back': 'back_page',
    'click .submit': 'submit',
    'change #zipcode': 'zipcode_changed',
    'change .saved_card': 'radio_card_changed'
  },
  semantic_form_validator_select: {},
  initialize: function () {
    var self = this;
    self.model.project_id = $('#project_id').val();
    self.model.item_id = $('#item_id').val();
    self.model.shipping = $('#shipping').val() == 'True';
    $.get('/api/validators/' + self.model.project_id + '/' + self.model.item_id, function (data) {
      self.semantic_form_validator_select = data;
      self.render();
      $('html, body').animate({scrollTop: $('div.title.active').offset().top});
    });
    $.get('/api/my/address', function (data) {
      if (data.address) {
        self.model.shipping_zipcode = data.address.zipcode;
        self.model.shipping_state = data.address.pref;
        self.model.shipping_town = data.address.town;
        self.model.shipping_building = data.address.building;
        self.model.shipping_address = data.address.address;
        self.model.shipping_last_name = data.address.last_name;
        self.model.shipping_first_name = data.address.first_name;
        self.model.shipping_phone = data.address.phone;
      }
    });
    $.get('/api/my/card', function (data) {
      if (data.card) {
        self.model.payment_credit_mode = 'old';
        self.model.payment_credit_saved_number = '************' + data.card.code;
      } else {
        self.model.payment_credit_mode = 'new';
        self.model.payment_credit_saved_number = null;
      }
    });
  },
  render: function () {
    var self = this;
    var template_name = "#" + self.model.view + "-template";
    var output = _.template($(template_name).html())(self.model);
    self.$el.html(output);
    active_step(self.model.view);
    $('.ui.dropdown').dropdown();
    $('.ui.privacy.checkbox').checkbox({
      onChecked: function () {
        $('#submit-button').removeClass('disabled');
        $('#submit-button').prop('disabled', false);
      },
      onUnchecked: function () {
        $('#submit-button').addClass('disabled');
        $('#submit-button').prop('disabled', true);
      }
    });
    $('.menu .item').tab({
      context: 'parent',
      onVisible: function (data) {
        self.model.payment_type = data;
        $('form.payment .field.error').removeClass('error');
        $('form.payment.error').removeClass('error');
        self.set_payment_validator();
      }
    }).tab('change tab', self.model.payment_type);
    if (self.model.view == 'select') {
      $('.ui.accordion').accordion({collapsible: false});
      $('form.select')
        .form(self.semantic_form_validator_select)
        .form('set values', self.model);
    } else if (self.model.view == 'shipping') {
      $('form.shipping')
        .form(semantic_form_validator_shipping)
        .form('set values', self.model);
    } else if (self.model.view == 'payment') {
      self.set_payment_validator();
    }
    if (self.model.payment_credit_mode == 'new') {
      $('div.card_input').show();
    } else {
      $('div.card_input').hide();
    }
    return self;
  },
  set_payment_validator: function () {
    var self = this;
    if (self.model.payment_type == 'credit') {
      if (self.model.payment_credit_mode == 'new') {
        $('form.payment')
          .form(semantic_form_validator_payment_credit)
          .form('set values', self.model);
      } else {
        $('form.payment')
          .form({})
          .form('set values', self.model);
      }
    }
    if (self.model.payment_type == 'cvs') {
      $('form.payment')
        .form(semantic_form_validator_payment_cvs)
        .form('set values', self.model);
    }
    if (self.model.payment_type == 'payeasy') {
      $('form.payment')
        .form(semantic_form_validator_payment_payeasy)
        .form('set values', self.model);
    }
  },
  cancel_checkout: function () {
    var self = this;
    send_ga_tracking('cancel', self.model.view);
    history.back();
  },
  next_page: function () {
    var self = this;
    if (!self.save_and_validate()) return;
    send_ga_tracking('next', self.model.view);
    if (self.model.view == 'select') {
      if (self.model.shipping) {
        self.model.view = 'shipping';
      } else {
        self.model.view = 'payment';
      }
    } else if (self.model.view == 'shipping') {
      self.model.view = 'payment';
    } else if (self.model.view == 'payment') {
      self.model.view = 'confirm';
    }
    self.render();
    $('html,body').animate({scrollTop: 0});
  },
  back_page: function () {
    var self = this;
    self.save_and_validate();
    send_ga_tracking('back', self.model.view);
    if (self.model.view == 'shipping') {
      self.model.view = 'select';
    } else if (self.model.view == 'payment') {
      if (self.model.shipping) {
        self.model.view = 'shipping';
      } else {
        self.model.view = 'select';
      }
    } else if (self.model.view == 'confirm') {
      $('#confirm-message').hide();
      self.model.view = 'payment';
    }
    self.render();
  },
  save_and_validate: function () {
    var self = this;
    if (self.model.view == 'select') {
      var select_form = $('form.select');
      self.merge_params(select_form.form('get values', _.keys(self.semantic_form_validator_select.fields)));
      return select_form.form('validate form');
    } else if (self.model.view == 'shipping') {
      var shipping_form = $('form.shipping');
      self.merge_params(shipping_form.form('get values', semantic_form_keys_shipping));
      self.model.shipping_state_text = $('#shipping_state').find('option:selected').text();
      return shipping_form.form('validate form');
    } else if (self.model.view == 'payment') {
      var payment_form = $('form.payment');
      self.merge_params(payment_form.form('get values', semantic_form_keys_payment));
      self.model.payment_cvs_text = $('#payment_cvs_code').find('option:selected').text();
      return payment_form.form('validate form');
    } else {
      return true;
    }
  },
  zipcode_changed: function (e) {
    if (/^\d{3}[-]*\d{4}$/g.test(e.target.value)) {
      $.get('/api/zipcode', {'zipcode': e.target.value}
      ).done(function (data) {
        if (data.status == 'ok') {
          $('form.shipping').form('set values', {
            'shipping_state': data.code, 'shipping_town': data.address
          });
        }
      });
    }
  },
  radio_card_changed: function (e) {
    var self = this;
    self.model.payment_credit_mode = e.target.value;
    if (self.model.payment_credit_mode == 'new') {
      $('div.card_input').show();
    } else {
      $('div.card_input').hide();
      self.model.payment_credit_number = null;
      self.model.payment_credit_cvc = null;
    }
    $('form.payment .field.error').removeClass('error');
    $('form.payment.error').removeClass('error');
    self.set_payment_validator();
  },
  merge_params: function (values) {
    var self = this;
    $.each(values, function (attr) {
      if (attr.indexOf('answer_') == 0) {
        self.model[attr] = values[attr];
      } else { // Trim and Replace space characters
        self.model[attr] = values[attr].trim().replace(/( |　)/g, '');
      }
    });
  },
  submit: function () {
    $('.ui.page.dimmer').dimmer({closable: false}).dimmer('show');
    var self = this;
    if (self.model.payment_type == 'credit'
      && /^\d+$/g.test(self.model.payment_credit_number)
      && /^\d+$/g.test(self.model.payment_credit_cvc)) {
      var gmo_shop_id = $('#gmo_shop_id').val();
      Multipayment.init(gmo_shop_id);
      Multipayment.getToken({
        cardno: self.model.payment_credit_number,
        expire: self.model.payment_credit_exp_year + ('0' + self.model.payment_credit_exp_month).slice(-2),
        securitycode: self.model.payment_credit_cvc
      }, generate_token);
      // holdername: 'SOME HOLDER' // TODO カード名義人
    } else {
      self.post_data();
    }
  },
  save_credit_token: function (resp) {
    var self = this;
    if (resp.resultCode == '000') {
      var tmp_credit_number = self.model.payment_credit_number;
      self.model.payment_credit_number = null;
      self.model.payment_credit_token = resp.tokenObject.token;
      self.post_data();
      self.model.payment_credit_number = tmp_credit_number;
    } else {
      $('.ui.page.dimmer').dimmer('hide');
    }
  },
  post_data: function () {
    var self = this;
    $.post('/api/checkout', self.model
    ).done(function (data) {
      // 結果を処理
      if (data.order_id) {
        send_ga_tracking('submit', self.model.view);
        checkout_complete(self.model.payment_type);
        self.model.view = 'complete';
        self.model.order_id = data.order_id;
        self.model.order_bk_code = data.bk_code;
        self.model.order_receipt_no = data.receipt_no;
        self.model.order_cust_id = data.cust_id;
        self.model.order_conf_no = data.conf_no;
        self.render();
      } else {
        if (!data.retryable) {
          self.model.view = 'error';
          self.render();
          $('#error-message').text(data.message);
        } else {
          $('#confirm-message').text(data.message);
          $('#confirm-message').show();
        }
      }
    }).fail(function () {
      self.model.view = 'error';
      self.render();
      $('#error-message').text('予期せぬエラーが発生しました。しばらくしてからもう一度やり直してください。');
    }).always(function () {
      $('.ui.page.dimmer').dimmer('hide');
      $('html,body').animate({scrollTop: 0});
    });
  }
});
