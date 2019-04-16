$("#id_outcomes .nav-link").click(function () {
    var outcome_id = $(this).attr('id').split('_').slice(-1).pop()
    var url = $(this).attr("data-outcome-media-url");

    if (outcome_id) {
        $.ajax({
            url: url,
            data: {'outcome_id': outcome_id},
            success: function (data) {
                console.log($(data)[6])
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
