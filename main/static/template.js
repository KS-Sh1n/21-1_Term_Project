function scrapeloading()
{
    // Show loading spinner, hide table content whild scraping.
    document.getElementById('loading').style.display='block';    document.getElementById('content').style.display='none';
    document.getElementById('title').innerHTML = "Scrping Feeds";
}

function sort(index)
{
    var table = $('th').parents('table').eq(0);
    var rows = table.find('tr:gt(0)').toArray().sort(comparer(index));
    console.log(rows);
    console.log();
    this.asc = !this.asc
    if (!this.asc){rows = rows.reverse()}
    for (var i = 0; i < rows.length; i++){table.append(rows)}
}

function comparer(index)
{
    return function(a, b) {
        var valA = getCellValue(a, index), valB = getCellValue(b, index)
        return $.isNumeric(valA) && $.isNumeric(valB) ? valA - valB : valA.toString().localeCompare(valB)
    }
}

function getCellValue(row, index)
{
    return $(row).children('td').eq(index).text()
}

$('#select').click(function(){
    console.log("1321312321");
    document.getElementById('checkbox').style.display='block';
})