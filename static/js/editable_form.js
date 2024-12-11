function create_form(data_obj, display_pri=false) {
    let items_data_form=document.createElement('form');
    items_data_form.action="#"
    items_data_form.method='POST'
    data_obj.forEach(function(obj) {
        let status_select=document.createElement('select');
        status_select.name='siid ' + obj.siid;
        let unmarked_opt=document.createElement('option');
        unmarked_opt.value='unmarked';
        unmarked_opt.innerHTML='unmarked';
        if (obj.Status=='unmarked') {
            unmarked_opt.selected=true;
            status_select.id='unmarkedselected';
        }
        let todo_opt=document.createElement('option');
        todo_opt.value='todo';
        todo_opt.innerHTML='todo';
        if (obj.Status=='todo') {
            todo_opt.selected=true;
            status_select.id='todoselected';
        }
        let complete_opt=document.createElement('option');
        complete_opt.value='complete';
        complete_opt.innerHTML='complete';
        if (obj.Status=='complete') {
            complete_opt.selected=true;
            status_select.id='completeselected';
        }
        let sep_txt = ' - ';
        if (display_pri) {
            var label_txt = obj.Priority + sep_txt + obj.Unit + sep_txt + 'Step ' + obj.Step + sep_txt + obj.Item + sep_txt + obj.Trade + '---NOTES---' + obj.Notes + '<br>';
        }
        else {
            var label_txt = obj.Unit + sep_txt + obj.Item + ' ---NOTES--- ' + obj.Notes + '<br>';
        }
        let label_element=document.createElement('label');
        label_element.htmlFor=obj.siid;
        label_element.innerHTML=label_txt;
        let note_input=document.createElement('input');
        note_input.type='text';
        note_input.name= 'siidnote ' + obj.siid;
        status_select.appendChild(unmarked_opt);
        status_select.appendChild(todo_opt);
        status_select.appendChild(complete_opt);
        items_data_form.appendChild(note_input);
        items_data_form.appendChild(status_select);
        items_data_form.appendChild(label_element);
        });
    let submit_element=document.createElement('button');
    submit_element.type='submit';
    // submit_element.onclick='send_statuses()';
    submit_element.innerHTML='Submit';
    items_data_form.appendChild(submit_element);

    return items_data_form;
};