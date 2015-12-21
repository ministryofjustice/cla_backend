/**
 * Created by joshrowe on 16/12/15.
 */
(function($) {
  var ReportTask = {
    url: '/admin/reports/api/exports/',
    el: null,

    init: function () {
      this.el = $('<div class="report-exports"></div>');
      this.table = $('<table class="report-table"></table>');
      this.el.append(this.table);

      $(document.body).append(this.el);
      this.fetch();
      this.bindEvents();
    },

    fetch: function () {
      var self = this;
      $.get(this.url, function (data) {
        self.load(data);
      });
    },

    deleteExport: function (id) {
      var self = this;
      $.ajax({
        method: 'DELETE',
        url: self.url  + id + '/',
        data: {
          id: id
        }
      }).done(function (data) {
        self.fetch();
      });
    },

    request: function () {

    },

    load: function (data) {
      this.table.empty();
      for (var i = 0; i < data.length; i++) {
        var $task = $('<tr class"report-ask"></tr>');
        var cols = ['id', 'link', 'path', 'status'];
        for (var k = 0; k < cols.length; k++) {
          var col = $('<td></td>')
          col.text(data[i][cols[k]])
          $task.append(col);
        }
        var col = $('<td></td>');
        var $deleteLink = $('<a class="delete-task"></a>')
          .text('DELETE')
          .data('id', data[i]['id']);
        col.append($deleteLink);
        $task.append(col);
        this.table.append($task)
      }
    },

    bindEvents: function () {
      var self = this;
      setInterval(function () {
        self.fetch();
      }, 10000);
      $(window.document).on('click', '.delete-task', function (e) {
        var $target = $(e.currentTarget);
        console.log($target.data());
        self.deleteExport($target.data('id'));
        $target.parent('tr').remove();
      });
    }
  }

  $( document ).ready(function() {
    ReportTask.init();
  });
})(django.jQuery);
