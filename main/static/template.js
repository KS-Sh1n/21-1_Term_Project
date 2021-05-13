function scrapeloading()
{
    // Show loading spinner, hide table content whild scraping.
    document.getElementById('loading').style.display='block';    document.getElementById('content').style.display='none';
    document.getElementById('title').innerHTML = "Scrping Feeds";
}

function filter_feed()
{
    table = document.getElementById('sitefeed');
    tr = table.getElementsByTagName("tr");
}

function sort_feed(col)
{
    var table = document.getElementById('sitefeed');
    var tr = table.getElementsByTagName("tr");
    
}