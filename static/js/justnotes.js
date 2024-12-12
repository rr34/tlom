function justnotes (data_obj) {
    let items_div = document.createElement('div');
    let day_current = 'none';
    data_obj.forEach(function(obj) {
        if (obj.Day!=day_current) {
            day_current = obj.Day;
            let new_day = document.createElement('h1');
            let new_text = document.createTextNode(obj.Day);
            new_day.appendChild(new_text);
            items_div.appendChild(new_day);
        }

        let sep_txt = ' - ';
        let new_item = document.createElement('p');
        new_item.innerHTML = obj.Time + sep_txt + obj.Unit + sep_txt + obj.Item + sep_txt + obj.Note;
        items_div.appendChild(new_item);
    });

        return items_div;
};