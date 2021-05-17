function confirmreset()
{
    $('#confirmreset').show();
    $('#title').text("Are you sure of clearing every data and table?");
    $('div#data_form, div#form_submit, label#select').hide();
}

function scrapeloading()
{
    // Show loading spinner, hide table content whild scraping.
    $('#loading').show();
    $('#content').hide();
    $('#title').text("Scraping feeds...");
}

function selectbox()
{
    if ($('#checkbox').is(":hidden"))
    {
        $('#select').text("cancel");
        $('div#checkbox, input:checkbox:first-child').show();
        $('#title, div#form_submit').hide();
    }
    else
    {
        $('#select').text("select");
        $('div#checkbox, input:checkbox:first-child').hide();
        $('#title, div#form_submit').show();
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
        var rows = table.find("tr:gt(0)").toArray();
        for(i = 0; i < rows.length; i++)
        {
            console.log(rows[i]);
        }
    })
})

function ordercheck(order)
{
    if (order())
    {
        
    }
}

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