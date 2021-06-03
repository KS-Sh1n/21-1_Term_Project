// REVISED FUNCTION
// Show checkbox at the left site of table to modify it.
function selectbox()
{
    if ($('.checkbox').is(":hidden"))
    {
        $('#title h1').text("CLICK FEEDS TO SELECT")
        $('label#select').html('<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-x" viewBox="0 0 16 16"><path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/></svg>');
        $('.checkbox').show();
        $('.notcheckbox').hide();
        $('#feed_link a').css('pointer-events', 'none');
        $('#pagination').hide();
    }
    else
    {
        $('#title h1').text("GRID PRACTICE")
        $('label#select').html('<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-check" viewBox="0 0 16 16"> <path d="M10.97 4.97a.75.75 0 0 1 1.07 1.05l-3.99 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425a.267.267 0 0 1 .02-.022z"/></svg>');
        $('.checkbox').hide();
        $('.notcheckbox').show();
        $('#feed_link a').css('pointer-events', 'auto');
        $('#pagination').show();
        $('[id="feed"]').css({
            "border-top":"1.5px solid rgb(0, 0, 0)",
            "border-bottom":"1.5px solid rgb(0, 0, 0)",
            "border-left":"3px solid rgb(0, 0, 0)",
            "border-right":"3px solid rgb(0, 0, 0)",
            "filter":"contrast(1)"
        });
        $('[id="feed"] :checkbox').prop('checked', false);
    }
}

$(function()
{
    $('[id="feed"]').click(function()
    {
        if($('#pagination').is(":hidden"))
        {
            if($(this).find(':checkbox').is(":checked"))
            {
                $(this).css({
                    "border-top":"1.5px solid rgb(0, 0, 0)",
                    "border-bottom":"1.5px solid rgb(0, 0, 0)",
                    "border-left":"3px solid rgb(0, 0, 0)",
                    "border-right":"3px solid rgb(0, 0, 0)",
                    "filter":"contrast(1)"
                });
                $(this).find(':checkbox').prop('checked', false);
            }
            else
            {
                $(this).css({
                    "border-top":"3px solid rgb(0, 0, 0)",
                    "border-bottom":"3px solid rgb(0, 0, 0)",
                    "border-left":"6px solid rgb(0, 0, 0)",
                    "border-right":"6px solid rgb(0, 0, 0)",
                    "filter":"contrast(0.5)"
                });
                $(this).find(':checkbox').prop('checked', true);
            }
        }
    });

    var delay = (function()
    {
        var timer = 0;
        return function(callback, ms)
        {
            clearTimeout(timer);
            timer = setTimeout(callback, ms);
        };
    })();

    $(window).resize(function()
    {
        delay(function()
        {
            if ($(this).width() < 768)
                $('#feed_link a').attr("target", "_blank");
            else
                $('#feed_link a').attr("target", "preview");
        }, 200);
    });
});

// REVISED FUNCTION
// Check everyting if at least one checkbox has not been checked.
// Deselect everything if every checkbix has been checked.
function checkall()
{
    var boxes_length = $('[id="feed"]').find(':checkbox:checked').toArray().length;
    var element_length = $('[id="feed"]').find(':checkbox').toArray().length;
    
    if (boxes_length != element_length)
    {
        $("[id=feed]").css({
            "border-top":"3px solid rgb(0, 0, 0)",
            "border-bottom":"3px solid rgb(0, 0, 0)",
            "border-left":"6px solid rgb(0, 0, 0)",
            "border-right":"6px solid rgb(0, 0, 0)",
            "filter":"contrast(0.5)"
        });
        $('[id="feed"] :checkbox').prop('checked', true);
    }
    else
    {
        $("[id=feed]").css({
            "border-top":"1.5px solid rgb(0, 0, 0)",
            "border-bottom":"1.5px solid rgb(0, 0, 0)",
            "border-left":"3px solid rgb(0, 0, 0)",
            "border-right":"3px solid rgb(0, 0, 0)",
            "filter":"contrast(1)"
        });
        $('[id="feed"] :checkbox').prop('checked', false);
    }
}

// REVISED FUNCTION
// Show loading spinner, hide table content whild scraping.
function scrapeloading()
{
    $('[name=scrape]').html('<span class="spinner-border spinner-border-sm"></span>　SCRAPING FEEDS...');
    $('#title h1').text("SCRAPING FEEDS...");
    $('[class *= dropdown]').hide();
    $('.filter').show();
    $('[name=scrape]').css({
        "position":"relative",
        "z-index":"2",
        "pointer-events":"none"
    });
}

// When reset button is pressed, double-check reset process.
function confirmreset()
{
    $('#confirmreset').show();
    $('#title').text("Are you sure of clearing every data and table?");
    $('div#data_form, div#form_submit, label#select').hide();
}

// Outdated sotring function
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