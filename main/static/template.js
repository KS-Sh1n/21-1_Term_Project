// When reset button is pressed, double-check reset process.
function confirmreset()
{
    $('#confirmreset').show();
    $('#title').text("Are you sure of clearing every data and table?");
    $('div#data_form, div#form_submit, label#select').hide();
}

// Show loading spinner, hide table content whild scraping.
function scrapeloading()
{
    $('div#loading').show();
    $('div#content, label#select, [name = scrape]').hide();
    $('#title').text("Scraping feeds...");
}


// Show checkbox at the left site of table to modify it.
function selectbox()
{
    if ($('#checkbox').is(":hidden"))
    {
        $('#select').text("cancel");
        $('div#checkbox, input:checkbox:first-child').show();
        $('#title, div#form_submit, [name = scrape]').hide();
    }
    else
    {
        $('#select').text("select");
        $('div#checkbox, input:checkbox:first-child').hide();
        $('#title, div#form_submit, [name = scrape]').show();
    }
}

// Check everyting if at least one checkbox has not been checked.
// Deselect everything if every checkbix has been checked.
function checkall()
{
    var boxes = $('table').find(':checkbox:checked').toArray();
    var fulllength = $('table').find(':checkbox').toArray();

    boxes.length != fulllength.length ? $('table :checkbox').prop('checked', true) : $('table :checkbox').prop('checked', false);
}

function tablesort(index)
{
    var table = $('tr').parents('table:first');
    var rows = table.find("tr:gt(0)").toArray().sort(comparefunction(index));
    ascendingcheck(rows, index);
    for (i = 0; i < rows.length; i++)
    {
        table.append(rows[i]);
    }
}

function comparefunction(index)
{
    //index 1 = site, index 2 = type, index 3 = scraped at
    return function(a, b)
    {
        var a_1 = zero_matrix(a, 1);
        var b_1 = zero_matrix(b, 1);
        var a_2 = zero_matrix(a, 2);
        var b_2 = zero_matrix(b, 2);
        var a_3 = new Date(zero_matrix(a, 3));
        var b_3 = new Date(zero_matrix(b, 3));
        if (index == 1)
        {
            return $('#sorted_1').text() != "▲"? a_1.toString().localeCompare(b_1) || b_3 - a_3 : b_1.toString().localeCompare(a_1) || b_3 - a_3;
        }
        else if (index == 2)
        {
            return $('#sorted_2').text() != "▲"? a_2.toString().localeCompare(b_2) || a_1.toString().localeCompare(b_1) || b_3 - a_3 : b_2.toString().localeCompare(a_2) || a_1.toString().localeCompare(b_1) || b_3 - a_3;
        }
        else if (index == 3)
        {   
            return $('#sorted_3').text() != "▼"? b_3 - a_3: a_3 - b_3;
        }
    }
}

function zero_matrix(row, column)
{
    return $(row).children('td').eq(column).text();
}

function ascendingcheck(index)
{
    switch(index)
    {
        case 1:
            if ($('#sorted_1').text() == "▲")
            {
                $('#sorted_1').text("▼");
            }
            else
            {
                $('#sorted_1').text("▲");
                $('#sorted_2').text("");
                $('#sorted_3').text("");    
            }
            break;
        case 2:
            if ($('#sorted_2').text() == "▲")
            {
                $('#sorted_2').text("▼");
            }
            else
            {
                $('#sorted_1').text("");
                $('#sorted_2').text("▲");
                $('#sorted_3').text("");    
            }
            break;
        case 3:
            if ($('#sorted_3').text() == "▼")
            {
                $('#sorted_3').text("▲");
            }
           else
            {
                $('#sorted_1').text("");
                $('#sorted_2').text("");
                $('#sorted_3').text("▼");    
            }
            break;
    }
}