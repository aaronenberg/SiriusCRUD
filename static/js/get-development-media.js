function ajax_development_media(url, data, success)
{
    $.ajax({
        url: url,
        data: data,
        success: success
    });
}


function get_development_media(el)
{
    var development_slug = window.location.pathname.split('/').slice(-2).pop();
    data = {'development_slug': development_slug};
    if (development_slug === null)
        return false;

    var success;
    var url = $(el).attr("data-development-media-url");

    var full_path = $(el).attr("data-full-path")

    if (full_path)
        data = Object.assign({'cwd': full_path}, data);

    success = function (data) {
        var agenda = $(data)[0];
        var assessment = $(data)[2];
        var people = $(data)[4];
        var presentation = $(data)[6];
        var other = $(data)[8];

        $("#agenda").html(agenda);
        $("#assessment").html(assessment);
        $("#people").html(people);
        $("#presentation").html(presentation);
        $("#other").html(other);
    };
    ajax_development_media(url, data, success);
}


$("#developmentmedia_filters select").change(function () {
    get_development_media($(this))
});


$("#id_development_media_content").on("click", "a[data-full-path]", function () {
    get_development_media($(this))
});


$("#development_media_tabs").on("click", ".nav-link", function () {
    get_development_media($(this))
});
