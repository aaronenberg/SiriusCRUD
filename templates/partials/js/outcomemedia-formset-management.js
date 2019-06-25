{% load static %}



function setTargetLabelFor(input_element, prefix)
{
    if (checkRemainingNumForms(prefix) === 0 && $('input[type="file"]:last').val() !== "") {
        document.getElementById('file_add').setAttribute("for", "");
        return;
    }
    if (isDirectoryInput(input_element))
        setTargetLabelForAddDirectoryInput();
    else
        setTargetLabelForAddFileInput();
    return;
}

function setTargetLabelForAddFileInput()
{
    var file_upload_last = $('input:not([webkitdirectory])[type="file"]:last').attr('id');
    document.querySelector('#file_add').setAttribute('for', file_upload_last);
}


function setTargetLabelForAddDirectoryInput()
{
    var directory_upload_last = $('input[webkitdirectory]:last').attr('id');
    document.querySelector('#directory_add').setAttribute('for', directory_upload_last);
}

function getTotalNumForms(prefix)
{
    return parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
}

function getMaxNumForms(prefix)
{
    return parseInt($('#id_' + prefix + '-MAX_NUM_FORMS').val());
}

function checkRemainingNumForms(prefix)
{
    var total = getTotalNumForms(prefix);
    var max = getMaxNumForms(prefix);
    return max - total;
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
    var total = getTotalNumForms(prefix);

    if (checkRemainingNumForms(prefix) === 0)
        return false;

    var newElement = $(selector).parents('.media-upload').clone(true);
    if (checkRemainingNumForms(prefix) === 1) {
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
        conditionRow = $('input:not([webkitdirectory])[type="file"]').parents('.media-upload');
    conditionRow.find('.add-media-upload')
    .removeClass('add-media-upload').addClass('remove-media-upload')
    .html('<img class="svg-icon-small" src="{% static "img/font-awesome/times.svg" %}">');

    $(selector).parents('.media-upload').after(newElement);

    return false;
}

function deleteForm(prefix, btn) {
    var total = getTotalNumForms(prefix);
    if (total <= 1)
        return false;

    var media_upload = btn.closest('.media-upload')
    if ($(media_upload).hasClass('has-instance')) {
        var input_delete_id = $(media_upload).find('input[type="file"]').attr('id').replace('-media', '-DELETE');
        document.getElementById(input_delete_id).setAttribute('checked', 'checked');
        $(media_upload).hide();
    }
    else {
        $(media_upload).remove()
        total--;
    }

    var forms = $('input:not([webkitdirectory])[type="file"]');
    if (prefix === 'directory')
        forms = $('.media-upload input[webkitdirectory]');

    $('#id_' + prefix + '-TOTAL_FORMS').val(total);

    for (var i = 0; i < total; i++)
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

    var input_element = $(this).prevAll('.custom-file').children('input');

    if (isDirectoryInput(input_element))
        var prefix = 'directory';
    else
        var prefix = 'media';

    var total = getTotalNumForms(prefix);
    deleteForm(prefix, $(this));

    if (total >= getMaxNumForms(prefix) && $('input[type="file"]:last').parents('.media-upload').css('display') !== 'none') {
        if (prefix === 'directory')
            cloneUpload('input[webkitdirectory]:last', prefix)
        else
            cloneUpload('input:not([webkitdirectory])[type="file"]:last', prefix)
        var last_input = $('input[type="file"]:last');
        $(last_input).val("");
        $(last_input).parents('.media-upload').find(':input').each(function() {
            $(this).required = false;
        });
        $(last_input).prev().remove();
        $(last_input).parents('.media-upload').hide();
    }

    setTargetLabelFor(input_element, prefix);

    return true;
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


$('#outcome-media-forms input[type="file"]').change(function() {
    var select_input_id = $(this).attr('id').replace('-media', '-outcome_type');
    var select_input = document.getElementById(select_input_id)

    if ($(this).prop("files").length > 0) {
        select_input.required = true;

        var input_selector;
        var directory;
        if (isDirectoryInput($(this))) {
            input_selector = 'input[webkitdirectory]:last';
            prefix = 'directory'
        }
        else {
            input_selector = 'input:not([webkitdirectory])[type="file"]:last';
            prefix = 'media'
        }
        cloneUpload(input_selector, prefix)
        setTargetLabelFor($(this), prefix);
    }
    else
        select_input.required = false;

    insertFileInputValue($(this));
    if ($(this).parents('.media-upload').css('display') == 'none') {
        $(this).parents('.media-upload').css('display', 'flex');
    }
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

(function () {
    var form = document.getElementsByTagName('form')[0]
    var progressBar = document.getElementsByClassName('progress-bar')[0]

    form.addEventListener('progress', function (event) {
        // event.detail.progress is a value between 0 and 1
        var percent = Math.round(event.detail.progress * 100)

        progressBar.setAttribute('style', 'width:' + percent + '%')
        progressBar.setAttribute('aria-valuenow', percent)
        progressBar.innerText = percent + '%'
    })
})()
