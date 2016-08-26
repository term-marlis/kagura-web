'use strict';

var views = ['select', 'shipping', 'payment', 'confirm'];
var actions = ['cancel', 'back', 'next', 'submit'];

var labels = [['01_Back', undefined, '01_to02Form', undefined], [undefined, '02_to01Select', '02_to03Check', undefined], [undefined, '03_to02Form', '03_to04Confirm', undefined], [undefined, '04_to03Check', undefined, '04_to05Thanks']];

var send_ga_tracking = function send_ga_tracking(action, view) {
  var label_ = labels[views.indexOf(view)][actions.indexOf(action)];
  if (typeof ga !== "undefined") {
    ga('send', 'event', 'checkout', action, label_);
  } else {
    console.log(label_);
  }
};