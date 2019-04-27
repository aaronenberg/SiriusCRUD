function ajax_outcome_media(url, data, success)
{
    $.ajax({
        url: url,
        data: data,
        success: success
    });
}


$("#id_outcomes .nav-item").click(function() {
    var previous_item = $("#id_outcomes .btn-secondary");

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
    var data;
    var outcome = $("#id_outcomes .btn-secondary .outcome");
    if (outcome.length === 0) {
        var outcome_slug = window.location.pathname.split('/').slice(-2)[0];
        data = {'outcome_slug': outcome_slug};
    }
    else {
        var outcome_id = parseInt(outcome.attr('id').split('_').slice(-1).pop());
        data = {'outcome_id': outcome_id};
    }
    if (outcome_id === null && outcome_slug === null)
        return false;

    var success;
    var url = $(this).attr("data-outcome-media-url");

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

        $("#curriculum").html(curriculum);
        $("#raw_data").html(raw_data);
        $("#analyzed_data").html(analyzed_data);
    };
    ajax_outcome_media(url, data, success);

});
