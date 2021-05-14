
function sort(index)
{
    var table = $('th').parents('table').eq(0);
    var rows = table.find('tr:gt(0)').toArray();
    rows.sort(comparer(index));
    this.asc = !this.asc
    if (!this.asc){rows = rows.reverse()}
    for (var i = 0; i < rows.length; i++){table.append(rows)}
}
function comparer(index) {
    return function(a, b) {
        var row_a = $(a).children('td').toArr0-=ay();
        var row_b = $(b).children('td').toArray();
        console.log(row_a);
        console.log(row_b);
            return $.isNumeric(valA) && $.isNumeric(valB) ? valA - valB : valA.toString().localeCompare(valB)
        }
    }
function Zero_Matrix(row, index)
{ 
    return $(row).children('td').eq(index).text();
}