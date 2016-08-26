'use strict';

var checkout_complete = function checkout_complete(payment_type) {
  var member_id = encodeURIComponent($('#member_id').val());
  var price_ = encodeURIComponent($('#item_price').val());
  var project_title_ = encodeURIComponent($('#project_title').val());
  var item_name_ = encodeURIComponent($('#item_name').val());
  var payment_type_ = encodeURIComponent(payment_type);

  var adebis = document.getElementById('adebis');
  adebis.innerHTML = "<img src='https://ac.ebis.ne.jp/log.php?argument=MsNhvGYE" + "&referrer=" + encodeURIComponent(document.referrer) + "&" + "width=" + screen.width + "&" + "height=" + screen.height + "&" + "ebisPageID=complete&" + "ebisOther1=" + project_title_ + "&" + "ebisOther2=" + item_name_ + "&" + "ebisOther3=" + payment_type_ + "&" + "ebisOther4=&" + "ebisOther5=&" + "ebisMember=" + member_id + "&" + "ebisAmount=" + price_ + "&" + "color=" + screen.colorDepth + "' width='0' height='0'>";
  var ebisUniqueTagMsNhvGYE = 1;
};