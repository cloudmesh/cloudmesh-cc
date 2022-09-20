$(document).ready(function () {
    var table = $('#example').DataTable({
        "columnDefs": [
            { "width": "5%", "targets": 0 }
        ],
        lengthMenu: [
            [-1, 10, 25, 50],
            ['All', 10, 25, 50],
        ],
    });
        $('a.toggle-vis').on('click', function (e) {
        e.preventDefault();

        // Get the column API object
        var column = table.column($(this).attr('data-column'));

        // Toggle the visibility
        column.visible(!column.visible());
    });
});