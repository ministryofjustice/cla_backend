/**
 * Created by joshrowe on 16/12/15.
 */
(function($) {
  var ReportTask = {
    url: '/admin/reports/api/exports/',
    el: null,

    init: function () {
      this.fetch();
      this.el = $('<div id="reportExports">')
      $(document.body).append(this.el);
    },

    fetch: function () {
      var self = this;
      $.get(this.url, function (data) {
        self.load(data);
      })
    },

    deleteExport: function (id) {
      var self = this;
      $.ajax({
        method: 'DELETE',
        url: self.url + id + '/'
      }).done(function (data) {
        self.fetch();
      });
    },

    request: function () {

    },

    load: function (data) {
      this.el.empty();
      for (var i = 0; i < data.length; i++) {
        var $task = $('<div class"reportTask">');
        this.el.append($task)
      }
    }
  }

  ReportTask.init();
})(django.jQuery);
