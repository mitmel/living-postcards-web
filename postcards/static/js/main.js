$(function() {
    gallery();      
});

function gallery() {
    $.ajax({
        url: POSTCARD_API_URL,
        dataType: 'json',
        success: gallery_cb,
    });
}

function gallery_cb(data) {
    var html = '';
    for ( i in data ) {
        html += '<span>' + data[i].title + '</span>';
    }
    $('#gallery').html(html);
}
