function scrapeloading()
{
    // Show loading spinner, hide table content whild scraping.
    document.getElementById('loading').style.display='block';    document.getElementById('content').style.display='none';
    document.getElementById('title').innerHTML = "Scrping Feeds";
}

function selectbox()
{
    if ($('#checkbox').is(":hidden"))
    {
        document.getElementById('select').innerHTML="cancel";
        document.getElementById('checkbox').style.display='block';
        $('input:checkbox, label#checkbox').show();
    }
    else
    {
        document.getElementById('select').innerHTML="select";
        document.getElementById('checkbox').style.display='none';
        $('input:checkbox, label#checkbox').hide();
    }
}
function checkall()
{
    var boxes = $('table').find(':checkbox:checked').toArray();
    var fulllength = $('table').find(':checkbox').toArray();
    boxes.length != fulllength.length ? $('table :checkbox').prop('checked', true) : $('table :checkbox').prop('checked', false);
}

$(document).ready(function(){
    $('th').click(function(){
        var table = $(this).parents('table:first');
        var rows = table.find("tr:gt(0)").toArray().sort(sortfunction(a, b, column))
    })
})

function outersort(a, b, column)
{
    var v = innersort(a, b, column);
}

function innersort(a, b, column)
{
    var row_a = zero_matrix(a, column);
    var row_b = zero_matrix(b, column);
    return $.isNumeric(row_a) && $.isNumeric(row_b) ? row_a - row_b : row_a.toString().localeCompare(row_b)
}

function zero_matrix(row, column)
{
    return $(row).children('td').eq(column).text();
}