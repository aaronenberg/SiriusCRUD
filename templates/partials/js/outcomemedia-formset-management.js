{% load static %}


function setTargetLabelForAddFileInput()
{
    var file_upload_last = $('input[multiple]:last').attr('id');
    document.querySelector('#file_add').setAttribute('for', file_upload_last);
}


function setTargetLabelForAddDirectoryInput()
{
    var directory_upload_last = $('input[webkitdirectory]:last').attr('id');
    document.querySelector('#directory_add').setAttribute('for', directory_upload_last);
}


function updateElementIndex(el, prefix, ndx)
{
    var id_regex = new RegExp('(' + prefix + '-\\d+)');
    var replacement = prefix + '-' + ndx;

    if ($(el).attr("for"))
        $(el).attr("for", $(el).attr("for").replace(id_regex, replacement));

    if (el.id)
        el.id = el.id.replace(id_regex, replacement);

    if (el.name)
        el.name = el.name.replace(id_regex, replacement);
}

function cloneUpload(selector, prefix)
{
    var total = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
    var max = parseInt($('#id_' + prefix + '-MAX_NUM_FORMS').val());

    if (total >= max)
        return false;

    var newElement = $(selector).parents('.media-upload').clone(true);
    if (total >= max - 1) {
        newElement.find('.add-media-upload')
        .removeClass('add-media-upload').addClass('remove-media-upload')
        .html('<img class="svg-icon-small" src="{% static "img/font-awesome/times.svg" %}">');
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

    var conditionRow;
    if (prefix === 'directory')
        conditionRow = $('input[webkitdirectory]').parents('.media-upload');
    else
        conditionRow = $('input[multiple]').parents('.media-upload');
    conditionRow.find('.add-media-upload')
    .removeClass('add-media-upload').addClass('remove-media-upload')
    .html('<img class="svg-icon-small" src="{% static "img/font-awesome/times.svg" %}">');

    $(selector).parents('.media-upload').after(newElement);

    return false;
}

function deleteForm(prefix, btn) {
    var total = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
    if (total <= 1)
        return false;

    btn.closest('.media-upload').remove();

    var forms;
    if (prefix === 'directory')
        forms = $('.media-upload input[webkitdirectory]')
    else
        forms = $('.media-upload input[multiple]')

    $('#id_' + prefix + '-TOTAL_FORMS').val(forms.length);

    for (var i = 0, formCount = forms.length; i < formCount; i++)
    {
      if (typeof($(this).attr('name')) != 'undefined')
      {
          $(forms.get(i)).parents('.media-upload').find(':input').each(function() {
              updateElementIndex(this, prefix, i);
          });
      }
    }

    return false;
}

$(document).on('click', '.remove-media-upload', function(e){
    e.preventDefault();

    if (isDirectoryInput($(this).prev('.custom-file').children('input')))
    {
        deleteForm('directory', $(this));
        setTargetLabelForAddDirectoryInput();
    }
    else
    {
        deleteForm('media', $(this));
        setTargetLabelForAddFileInput();
    }

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

    if ($(this).prop("files").length > 0) {
        select_input.required = true;

        if (isDirectoryInput($(this)))
        {
            cloneUpload('input[webkitdirectory]:last', 'directory');
            setTargetLabelForAddDirectoryInput();
        }
        else
        {
            cloneUpload('input[multiple]:last', 'media');
            setTargetLabelForAddFileInput();
        }
    }
    else
        select_input.required = false;
    insertFileInputValue($(this));
    if ($(this).parents('.media-upload').css('display') == 'none')
        $(this).parents('.media-upload').show();
});

function insertFileInputValue(file_input)
{
    if (!isDirectoryInput(file_input))
    {
        var file_name = $(file_input).val().split('\\').pop();
    $(file_input).before('<span><img class="mb-1 mr-2 svg-icon-small" src="{% static "img/font-awesome/file.svg" %}">' + file_name + '</span>');
        return;
    }

    let output = $(file_input).parents(".media-upload").children(".media-listing");
    let files = $(file_input).prop("files");
    let rootDirectoryName = files[0].webkitRelativePath.split("/")[0]
    $(file_input).before('<span><img class="mb-1 mr-2 svg-icon" src="{% static "img/font-awesome/folder.svg" %}">' + rootDirectoryName + '</span>');
}

function isDirectoryInput(input_element)
{
    var id = input_element.attr('id').split('_').pop().split('-')[0]
    if (id === 'directory')
        return true;
    return false;
}
