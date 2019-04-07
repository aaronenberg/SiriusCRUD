$("#outcome_course").change(function () {
    var url = $("#outcome-form").attr("data-sections-url");
    var course_id = $(this).val();

    if (course_id) {
        $.ajax({
            url: url,
            data: {'course': course_id},
            success: function (data) {
                $('#outcome_course_section').prop('disabled', false);
                $("#outcome_course_section").html(data);
            }
        });
    }
    else {
      $('#outcome_course_section').prop('disabled', true);
      $("#outcome_course_section").html("");
    }
});
