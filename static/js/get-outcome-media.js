$("#id_outcomes .nav-item").click(function() {
    var previous_item = $("#id_outcomes .btn-secondary");

    $(this).find(".outcome-link").attr("hidden", false);
    previous_item.find(".outcome-link").attr("hidden", true);
    previous_item.removeClass("btn-secondary");
    $(this).addClass("btn-secondary");
});

$("#id_outcomes .outcome").click(function () {
    var previous_item = $("#id_outcomes .btn-secondary");
    if ($(this)[0] == previous_item.find(".outcome")[0])
        return false;

    var outcome = $(this);
    var previous_outcome = $(previous_item).find(".outcome")
    var outcome_id = outcome.attr('id').split('_').slice(-1).pop()
    var url = outcome.attr("data-outcome-media-url");


    if (outcome_id) {
        $.ajax({
            url: url,
            data: {'outcome_id': outcome_id},
            success: function (data) {
                var raw_data = $(data)[0]
                var analyzed_data = $(data)[2]
                var curriculum = $(data)[4]
                var title = $(data)[6]
                var description = $(data)[8]

                $("#curriculum").html(curriculum)
                $("#raw_data").html(raw_data)
                $("#analyzed_data").html(analyzed_data)
                $("#id_outcome_title").html(title)
                $("#id_outcome_description").html(description)
            }
        });
    }
});
