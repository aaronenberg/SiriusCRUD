function updateElementIndex(el, prefix, ndx) {
    var id_regex = new RegExp('(' + prefix + '-\\d+)');
    var replacement = prefix + '-' + ndx;

    if ($(el).attr("for"))
        $(el).attr("for", $(el).attr("for").replace(id_regex, replacement));

    if (el.id)
        el.id = el.id.replace(id_regex, replacement);

    if (el.name)
        el.name = el.name.replace(id_regex, replacement);
}

function cloneMore(selector, prefix) {
    var total = $('#id_' + prefix + '-TOTAL_FORMS').val();
    var max = $('#id_' + prefix + '-MAX_NUM_FORMS').val();

    if (total >= max)
        return false;

    var newElement = $(selector).clone(true);
    if (total >= max - 1) {
        newElement.find('.btn.add-media-upload')
        .removeClass('btn-success').addClass('btn-danger')
        .removeClass('add-media-upload').addClass('remove-media-upload')
        .html('&#120273;');
    }

    newElement.find(':input').each(function() {
      if (typeof($(this).attr('name')) != 'undefined') {
          var name = $(this).attr('name').replace('-' + (total-1) + '-', '-' + total + '-');
          var id = 'id_' + name;

          $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
          $(this).removeAttr('required');
      }
    });
    total++;
    $('#id_' + prefix + '-TOTAL_FORMS').val(total);
    $(selector).after(newElement);

    var conditionRow = $('.media-upload:not(:last)');
    conditionRow.find('.btn.add-media-upload')
    .removeClass('btn-success').addClass('btn-danger')
    .removeClass('add-media-upload').addClass('remove-media-upload')
    .html('&#120273;');

    return false;
}

function deleteForm(prefix, btn) {
    var total = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());

    if (total > 1) {
      btn.closest('.media-upload').remove();
      var forms = $('.media-upload');
      $('#id_' + prefix + '-TOTAL_FORMS').val(forms.length);

      for (var i=0, formCount=forms.length; i<formCount; i++) {
          if (typeof($(this).attr('name')) != 'undefined') {
              $(forms.get(i)).find(':input').each(function() {
                  updateElementIndex(this, prefix, i);
              });
          }
      }
    }
    if (total <= 2) {
        console.log('hello');
       $('.btn.remove-media-upload')
        .removeClass('btn-danger')
        .removeClass('remove-media-upload')
        .addClass('add-media-upload')
        .html('+');
    }
    return false;
}

$(document).on('click', '.add-media-upload', function(e){
    e.preventDefault();
    cloneMore('.media-upload:last', 'media');
    return false;
});

$(document).on('click', '.remove-media-upload', function(e){
    e.preventDefault();
    deleteForm('media', $(this));
    return false;
});

$('#outcome-media-forms select').click(function() {
    var file_input_id = $(this).attr('id').replace( '-outcome_type','-media');
    var existing_media_id = $(this).attr('id').replace( '-outcome_type','-id');
    var file_input = document.getElementById(file_input_id)
    var existing_media = document.getElementById(existing_media_id)

    if ($(this).val() && !existing_media)
        file_input.required = true;
    else
        file_input.required = false;
});

$('#outcome-media-forms input').change(function() {
    var select_input_id = $(this).attr('id').replace('-media', '-outcome_type');
    var select_input = document.getElementById(select_input_id)

    if ($(this).prop("files").length > 0)
        select_input.required = true;
    else
        select_input.required = false;
});
