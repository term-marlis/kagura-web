(function ($) {
  $(function () {
    var $header = $('#top-head');
    $(window).scroll(function () {
      if ($(window).scrollTop() > 350) {
        $header.addClass('fixed');
        $('#top-head').find('div.notify').hide();
      } else {
        $header.removeClass('fixed');
        $('#top-head').find('div.notify').show();
      }
    });
    $('#remove-notify').click(function () {
      $('#top-head').find('div.notify').remove();
      $.get('/api/notify/undelivery', function (data) {
      });
    });
    $('#info_toparea').click(function () {
      $(this).remove();
    });
    $('a.regist.newsletter').click(function () {
      $.get('/api/email/news', function (data) {
        // TODO ポップアップを表示する
        if (data.login) {
          alert('ニュースレターを登録しました。')
        } else {
          alert('ログインしてください。');
        }
      });
    });
    $('#faq-button').click(function () {
      $('#faq-form').submit();
    });
  });
})(jQuery);


$(function () {
  var topBtn = $("#page-top");
  topBtn.hide();
  //スクロールが100に達したらボタン表示
  $(window).scroll(function () {
    if ($(this).scrollTop() > 100) {
      topBtn.fadeIn();
    } else {
      topBtn.fadeOut();
    }
  });
  //スクロールしてトップ
  topBtn.click(function () {
    $('body,html').animate({
      scrollTop: 0
    }, 500);
    return false;
  });
});
