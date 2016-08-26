(function () {
  share_facebook = function () {
    var url;
    url = "http://www.facebook.com/sharer.php";
    url += "?u=" + encodeURIComponent(window.location.toString());
    window.open(url, 'FBwindow', 'width=650, height=450, menubar=no, toolbar=no, scrollbars=yes');
    return false;
  };
  share_twitter = function (message, hashTags) {
    var url;
    url = "http://twitter.com/share";
    url += "?url=" + encodeURIComponent(window.location.toString());
    if (message != null) {
      url += "&text=" + encodeURIComponent(message);
    }
    if (hashTags != null) {
      url += "&hashtags=" + encodeURIComponent(hashTags);
    }
    window.open(url);
    return false;
  };
  share_line = function (message) {
    var url;
    message += " " + window.location.toString();
    url = "http://line.me/R/msg/text/?" + encodeURIComponent(message);
    window.open(url);
    return false;
  };
}());