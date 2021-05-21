/**
 * Created by joshrowe on 16/12/15.
 */
(function($) {

  function readCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
      var c = ca[i];
      while (c.charAt(0) == ' ') c = c.substring(1, c.length);
      if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
  }

  var ReportTask = {
    url: window.reportUrl,
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
        headers: {
          'X-CSRFTOKEN': readCookie('csrftoken')
        },
        data: {
          id: id
        }
      }).done(function (data) {
        self.fetch();
      });
    },

    load: function (data) {
      this.table.empty();
      for (var i = 0; i < data.length; i++) {
        var $task = $('<tr class"report-ask"></tr>');
        var cols = ['id', 'status', 'message'];
        for (var k = 0; k < cols.length; k++) {
          var col = $('<td></td>');
          col.text(data[i][cols[k]]);
          $task.append(col);
        }
        var linkcol = $('<td></td>');
        if (data[i]['link']) {
          var $link = $('<a></a>').attr('href', data[i]['link'])
            .text(data[i]['link']);
          linkcol.append($link);
        } else {
          linkcol.text('pending...');
          $task.addClass('task-pending');
        }
        $task.append(linkcol);

        var deleteCol = $('<td></td>');
        var $deleteLink = $('<a class="delete-task"></a>')
          .text('DELETE')
          .data('id', data[i]['id']);
        deleteCol.append($deleteLink);
        $task.append(deleteCol);

        this.table.append($task);
      }
    },

    bindEvents: function () {
      var self = this;
      setInterval(function () {
        self.fetch();
      }, 5000);
      $(window.document).on('click', '.delete-task', function (e) {
        var $target = $(e.currentTarget);
        self.deleteExport($target.data('id'));
        $target.parent('tr').remove();
      });
    }
  }

  $( document ).ready(function() {
    ReportTask.init();
  });
})(django.jQuery);
