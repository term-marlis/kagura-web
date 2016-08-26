"use strict";

var title = " | 共創型クラウドクリエイティング WIZY(ウィジー)";

var share_facebook = function share_facebook() {
  var url;
  url = "http://www.facebook.com/sharer.php";
  url += "?u=" + encodeURIComponent(window.location.toString());
  window.open(url, 'FBwindow', 'width=650, height=450, menubar=no, toolbar=no, scrollbars=yes');
  return false;
};
var share_twitter = function share_twitter(message, hashTags) {
  var url;
  url = "http://twitter.com/share";
  url += "?url=" + encodeURIComponent(window.location.toString());
  if (message != null) {
    url += "&text=" + encodeURIComponent(message);
  }
  if (hashTags != null) {
    url += "&hashtags=" + encodeURIComponent(hashTags);
  }
  url += "&via=wizy_official";
  window.open(url);
  return false;
};
var share_line = function share_line(message) {
  var url;
  message += " " + window.location.toString();
  url = "http://line.me/R/msg/text/?" + encodeURIComponent(message);
  window.open(url);
  return false;
};

/* Share Current Project */
var share_project = function share_project(mode, creator_name, project_title) {
  var text = creator_name + ' - ' + project_title + title;
  if (mode == 'line') {
    share_line(text);
  }
  if (mode == 'facebook') {
    share_facebook();
  }
  if (mode == 'twitter') {
    share_twitter(text, creator_name + ' #WIZY');
  }
};
/* Share Project */
var share_checkout = function share_checkout(mode, creator_name, project_title) {
  var text = creator_name + ' - ' + project_title + title;
  if (mode == 'line') {
    share_line(text);
  }
  if (mode == 'facebook') {
    share_facebook();
  }
  if (mode == 'twitter') {
    share_twitter(text, creator_name + ' #WIZY');
  }
};