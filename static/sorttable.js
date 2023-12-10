/*
 * sorttable.js
 *
 * Requires: jQuery (tested with v 1.11)
 *
 * jQuery plug-in that allows you to sort table by any column
 */

jQuery.fn.addSortWidget = function (options) {
  var dashboardUrl = $("#dashboardUrl").attr("dashboard-url");
  console.log(dashboardUrl);
  var defaults = {
    img_asc: dashboardUrl + "static/asc_sort.gif",
    img_desc: dashboardUrl + "static/desc_sort.gif",
    img_nosort: dashboardUrl + "static/no_sort.gif",
  };

  console.log(defaults);

  var options = $.extend({}, defaults, options),
    $destElement = $(this),
    is_asc = true;

  $("th", $destElement).each(function (index) {
    // to each header cell (index is useful while sorting)
    $("<img>") // create image that allows you to sort by specific column
      .attr("src", options.img_nosort)
      .addClass("sorttable_img")
      .css({
        cursor: "pointer",
        "margin-left": "10px",
      })
      .on("click", function () {
        $(".sorttable_img", $destElement).attr("src", options.img_nosort);
        $(this).attr("src", is_asc ? options.img_desc : options.img_asc);
        is_asc = !is_asc;

        var rows = $("tr", $destElement).not(":has(th)").not(":last").get(); // save all rows (tr) into array (.get())
        rows.sort(function (a, b) {
          // sort array with table rows
          var m = $("td:eq(" + index + ")", a).text(); // get column you needed by using index of th element (closure)
          var n = $("td:eq(" + index + ")", b).text();

          // if elements are numbers
          if (
            !isNaN(parseFloat(m.replace(/,/g, ""))) &&
            !isNaN(parseFloat(n.replace(/,/g, "")))
          )
            return is_asc
              ? parseFloat(m.replace(/,/g, "")) -
                  parseFloat(n.replace(/,/g, ""))
              : parseFloat(n.replace(/,/g, "")) -
                  parseFloat(m.replace(/,/g, ""));

          // if elements are strings
          if (is_asc) return m.localeCompare(n);
          // asc
          else return n.localeCompare(m); // desc
        });

        var tbody = $destElement.has("tbody") ? "tbody" : ""; // check if table has tbody
        for (var i = 0; i < rows.length; i++) {
          $(rows[i])
            .find("td:first")
            .text(i + 1);
          $(tbody, $destElement).append(rows[i]); // add each row to table (elements do not duplicate, just place to new position)
        }
      })
      .appendTo(this); // add created sort image with click event handler to current th element
  });

  return $destElement;
};
