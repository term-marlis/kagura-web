var semantic_form_keys_shipping = [
  'shipping_zipcode', 'shipping_state', 'shipping_town', 'shipping_address',
  'shipping_building', 'shipping_last_name', 'shipping_first_name', 'shipping_phone'
];
var semantic_form_validator_shipping = {
  on: 'blur',
  keyboardShortcuts: false,
  fields: {
    shipping_zipcode: {
      identifier: 'shipping_zipcode',
      rules: [
        {type: 'empty', prompt: '郵便番号を入力してください'},
        {type: 'regExp[/^\\d{3}-?\\d{4}$/]', prompt: '郵便番号を正しく入力してください'}
      ]
    },
    shipping_state: {
      identifier: 'shipping_state',
      rules: [{type: 'integer[1..47]', prompt: '都道府県を選択してください'}]
    },
    shipping_town: {
      identifier: 'shipping_town',
      rules: [{type: 'empty', prompt: '市区町村を入力してください'}]
    },
    shipping_address: {
      identifier: 'shipping_address',
      rules: [{type: 'empty', prompt: '番地を入力してください'}]
    },
    shipping_last_name: {
      identifier: 'shipping_last_name',
      rules: [
        {type: 'empty', prompt: 'お名前(姓)を入力してください'}
      ]
    },
    shipping_first_name: {
      identifier: 'shipping_first_name',
      rules: [
        {type: 'empty', prompt: 'お名前(名)を入力してください'}
      ]
    },
    shipping_phone: {
      identifier: 'shipping_phone',
      rules: [
        {type: 'empty', prompt: '電話番号を入力してください'},
        {type: 'regExp[/^[0-9]+[0-9-]+[0-9]+$/]', prompt: '電話番号を正しく入力してください'}
      ]
    }
  }
};

var semantic_form_keys_payment = [
  'payment_type', 'payment_credit_number', 'payment_credit_cvc',
  'payment_credit_exp_month', 'payment_credit_exp_year', 'payment_credit_mode',
  'payment_cvs_code', 'payment_cvs_first_name', 'payment_cvs_last_name', 'payment_cvs_first_name_kana',
  'payment_cvs_last_name_kana', 'payment_cvs_tel_no', 'payment_payeasy_first_name', 'payment_payeasy_last_name',
  'payment_payeasy_first_name_kana', 'payment_payeasy_last_name_kana', 'payment_payeasy_tel_no'
];
var semantic_form_validator_payment_credit = {
  on: 'blur',
  keyboardShortcuts: false,
  fields: {
    payment_credit_number: {
      identifier: 'payment_credit_number',
      rules: [
        {type: 'empty', prompt: 'カード番号を入力してください'},
        {type: 'regExp[/^\\d{16}$/]', prompt:'カード番号を正しく入力してください'}
      ]
    },
    payment_credit_cvc: {
      identifier: 'payment_credit_cvc',
      rules: [
        {type: 'empty', prompt: 'セキュリティコードを入力してください'},
        {type: 'regExp[^\\d{3}$|^\\d{4}$]', prompt: 'セキュリティコードを正しく入力してください'}
      ]
    },
    payment_credit_exp_month: {
      identifier: 'payment_credit_exp_month',
      rules: [{type: 'empty', prompt: '有効期限(月)を選択してください'}]
    },
    payment_credit_exp_year: {
      identifier: 'payment_credit_exp_year',
      rules: [{type: 'empty', prompt: '有効期限(年)を選択してください'}]
    }
  }
};
var semantic_form_validator_payment_cvs = {
  on: 'blur',
  keyboardShortcuts: false,
  fields: {
    payment_cvs_code: {
      identifier: 'payment_cvs_code',
      rules: [{type: 'empty', prompt: 'コンビニを選択してください'}]
    },
    payment_cvs_last_name: {
      identifier: 'payment_cvs_last_name',
      rules: [{type: 'empty', prompt: 'お名前(姓)を入力してください'}]
    },
    payment_cvs_first_name: {
      identifier: 'payment_cvs_first_name',
      rules: [{type: 'empty', prompt: 'お名前(名)を入力してください'}]
    },
    payment_cvs_last_name_kana: {
      identifier: 'payment_cvs_last_name_kana',
      rules: [
        {type: 'empty', prompt: 'フリガナ(セイ)を入力してください'},
        {type: 'regExp[/^[ァ-ンー]*$/]', prompt: '全角カナで入力してください'}
      ]
    },
    payment_cvs_first_name_kana: {
      identifier: 'payment_cvs_first_name_kana',
      rules: [
        {type: 'empty', prompt: 'フリガナ(メイ)を入力してください'},
        {type: 'regExp[/^[ァ-ンー]*$/]', prompt: '全角カナで入力してください'}
      ]
    },
    payment_cvs_tel_no: {
      identifier: 'payment_cvs_tel_no',
      rules: [
        {type: 'empty', prompt: '電話番号を入力してください'},
        {type: 'regExp[/^[0-9]+[0-9-]+[0-9]+$/]', prompt: '電話番号を正しく入力してください'}
      ]
    }
  }
};
var semantic_form_validator_payment_payeasy = {
  on: 'blur',
  keyboardShortcuts: false,
  fields: {
    payment_payeasy_last_name: {
      identifier: 'payment_payeasy_last_name',
      rules: [{type: 'empty', prompt: 'お名前(姓)を入力してください'}]
    },
    payment_payeasy_first_name: {
      identifier: 'payment_payeasy_first_name',
      rules: [{type: 'empty', prompt: 'お名前(名)を入力してください'}]
    },
    payment_payeasy_last_name_kana: {
      identifier: 'payment_payeasy_last_name_kana',
      rules: [
        {type: 'empty', prompt: 'フリガナ(セイ)を入力してください'},
        {type: 'regExp[/^[ァ-ンー]*$/]', prompt: '全角カナで入力してください'}
      ]
    },
    payment_payeasy_first_name_kana: {
      identifier: 'payment_payeasy_first_name_kana',
      rules: [
        {type: 'empty', prompt: 'フリガナ(メイ)を入力してください'},
        {type: 'regExp[/^[ァ-ンー]*$/]', prompt: '全角カナで入力してください'}
      ]
    },
    payment_payeasy_tel_no: {
      identifier: 'payment_payeasy_tel_no',
      rules: [
        {type: 'empty', prompt: '電話番号を入力してください'},
        {type: 'regExp[/^[0-9]+[0-9-]+[0-9]+$/]', prompt: '電話番号を正しく入力してください'}
      ]
    }
  }
};
