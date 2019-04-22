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
    var selected_section = $("#outcome_media_tabs .dropdown-item.selected");
    if (selected_section.length > 0)
        var section = parseInt(selected_section.attr('id').split('_').slice(-1).pop());
    var previous_item = $("#id_outcomes .btn-secondary");
    if ($(this)[0] == previous_item.find(".outcome")[0])
        return false;

    var outcome = $(this);
    var previous_outcome = $(previous_item).find(".outcome");
    var outcome_id = parseInt(outcome.attr('id').split('_').slice(-1).pop());
    var url = outcome.attr("data-outcome-media-url");

    var data;
    var success;
    if (outcome_id !== null) {
        if ( section !== null && section === section)
            data = {'outcome_id': outcome_id, 'section': section};
        else
            data = {'outcome_id': outcome_id};
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
    }
});


$("#outcome_media_tabs .dropdown-item").click(function () {
    var selected_outcome = $("#id_outcomes .btn-secondary .outcome");
    var outcome_id = parseInt(selected_outcome.attr('id').split('_').slice(-1).pop());
    var previous_item = $("#outcome_media_tabs .dropdown-item.selected");
    if ($(this)[0] == previous_item[0])
        return true;

    var dropdown_item = $(this);
    var section = parseInt(dropdown_item.attr('id').split('_').slice(-1).pop());
    var url = dropdown_item.attr("data-outcome-media-url");

    var data;
    var success;

    if (section !== null && outcome_id !== null) {
        if (section === section) {
            data = {'outcome_id': outcome_id, 'section': section};
        }
        else {
            data = {'outcome_id': outcome_id};
        }
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
});
