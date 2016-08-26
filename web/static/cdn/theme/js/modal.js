$(function () {
  var currentModalTrigger = null;
  var modalClassTrigger = "modal_trigger";
  var modals = document.getElementsByClassName(modalClassTrigger);
  for (var i = 0, l = modals.length; l > i; i++) {
    modals[i].onclick = function () {
      this.blur();
      var target = this.getAttribute("data-target");
      if (typeof (target) == "undefined" || !target || target == null) {
        return false;
      }
      currentModalTrigger = document.getElementById(target);
      if (currentModalTrigger == null) {
        return false;
      }
      if ($("#modal-overlay")[0]) return false; //新しくモーダルウィンドウを起動しない
      //if($("#modal-overlay")[0]) $("#modal-overlay").remove() ;		//現在のモーダルウィンドウを削除して新しく起動する

      $("body").append('<div id="modal-overlay"></div>');
      $("#modal-overlay").fadeIn("fast");
      centering_modal_window();
      $(currentModalTrigger).fadeIn("slow");
      $("#modal-overlay,#modal-close").unbind().click(function () {
        $("#" + target + ",#modal-overlay").fadeOut("fast", function () {
          $('#modal-overlay').remove();
        });
        currentModalTrigger = null;
      });
    }
  }
  $(window).resize(centering_modal_window);
  function centering_modal_window() {
    if (currentModalTrigger == null) return false;
    var w = $(window).width();
    // var h = $(window).height();
    var h = $('#modal-overlay').height();
    var cw = $(currentModalTrigger).outerWidth();
    var ch = $(currentModalTrigger).outerHeight();
    $(currentModalTrigger).css({
      "left": ((w - cw) / 2) + "px",
      "top": ((h - ch) / 2) + "px"
    });
  }
});