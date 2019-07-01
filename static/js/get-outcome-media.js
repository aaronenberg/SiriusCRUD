function ajax_outcome_media(url, data, success)
{
    $.ajax({
        url: url,
        data: data,
        success: success
    });
}


function get_outcome_media(el)
{
    var data;
    var outcome = $("#id_outcomes .btn-secondary .outcome");
    if (outcome.length === 0)
        return false;

    var outcome_id = parseInt(outcome.attr('id').split('_').slice(-1).pop());
    data = {'outcome_id': outcome_id};

    var success;
    var url = $(el).attr("data-outcome-media-url");

    var year = parseInt($("#outcomemedia_year").val());
    var section = parseInt($("#outcomemedia_section").val());
    var semester = $("#outcomemedia_semester").val();
    var full_path = $(el).attr("data-full-path")

    if (section === section)
        data = Object.assign({'section': section}, data);
    if (year === year)
        data = Object.assign({'year': year}, data);
    if (semester !== 'any')
        data = Object.assign({'semester': semester}, data);
    if (full_path)
        data = Object.assign({'cwd': full_path}, data);

    success = function (data) {
        var raw_data = $(data)[0];
        var analyzed_data = $(data)[2];
        var curriculum = $(data)[4];

        $("#curriculum").html(curriculum);
        $("#raw_data").html(raw_data);
        $("#analyzed_data").html(analyzed_data);
    };
    ajax_outcome_media(url, data, success);

}


$("#id_outcomes .nav-item").click(function() {
    var previous_item = $("#id_outcomes .btn-secondary");
    if ($(previous_item).is($(this)))
        return;

    $(this).find(".outcome-link").attr("hidden", false);
    previous_item.find(".outcome-link").attr("hidden", true);
    previous_item.removeClass("btn-secondary");
    $(this).addClass("btn-secondary");
});


$("#id_outcomes .outcome").click(function () {
    var previous_item = $("#id_outcomes .btn-secondary");
    var outcome = $(this);
    var outcome_id = parseInt(outcome.attr('id').split('_').slice(-1).pop());
    if (outcome[0] == previous_item.find(".outcome")[0] || outcome_id === null)
        return false;

    var url = outcome.attr("data-outcome-media-url");
    var success;
    var data = {'outcome_id': outcome_id};

    var year = parseInt($("#outcomemedia_year").val());
    var section = parseInt($("#outcomemedia_section").val());
    var semester = $("#outcomemedia_semester").val();

    if (section === section)
        data = Object.assign({'section': section}, data);
    if (year === year)
        data = Object.assign({'year': year}, data);
    if (semester !== 'any')
        data = Object.assign({'semester': semester}, data);

    success = function (data) {
        var raw_data = $(data)[0];
        var analyzed_data = $(data)[2];
        var curriculum = $(data)[4];
        var title = $(data)[6];
        var description = $(data)[8];

        $("#curriculum").html(curriculum);
        $("#raw_data").html(raw_data);
        $("#analyzed_data").html(analyzed_data);
        $("#id_outcome_title").html(title);
        $("#id_outcome_description").html(description);
    };
    ajax_outcome_media(url, data, success);
});


$("#outcomemedia_filters select").change(function () {
    get_outcome_media($(this))
});


$("#id_outcome_media_content").on("click", "a[data-full-path]", function () {
    get_outcome_media($(this))
});


$("#outcome_media_tabs").on("click", ".nav-link", function () {
    get_outcome_media($(this))
});
