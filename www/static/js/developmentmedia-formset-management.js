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
    var newElement = $(selector).clone(true);

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
    return false;
}

$(document).on('click', '.add-media-upload', function(e){
    e.preventDefault();
    cloneMore('.media-upload:last', 'development_media');
    return false;
});

$(document).on('click', '.remove-media-upload', function(e){
    e.preventDefault();
    deleteForm('development_media', $(this));
    return false;
});

$('#development-media-forms select').click(function() {
    var file_input_id = $(this).attr('id').replace( '-development_type','-media');
    var existing_media_id = $(this).attr('id').replace( '-development_type','-id');
    var file_input = document.getElementById(file_input_id)
    var existing_media = document.getElementById(existing_media_id)

    if ($(this).val() && !existing_media)
        file_input.required = true;
    else
        file_input.required = false;
});

$('#development-media-forms input').change(function() {
    var select_input_id = $(this).attr('id').replace('-media', '-development_type');
    var select_input = document.getElementById(select_input_id)

    if ($(this).prop("files").length > 0)
        select_input.required = true;
    else
        select_input.required = false;
});
