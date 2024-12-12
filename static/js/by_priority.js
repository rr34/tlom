function by_priority (data_obj) {
    let items_div = document.createElement('div');
    let pri_current = 'none';
    let room_current = 'none';
    data_obj.forEach(function(obj) {
        if (obj.Priority!=pri_current) {
            pri_current = obj.Priority;
            let new_pri = document.createElement('h1');
            let new_text = document.createTextNode('Priority ' + obj.Priority + ' Rooms');
            new_pri.appendChild(new_text);
            items_div.appendChild(new_pri);
        }
        if (obj.Unit!=room_current) {
            room_current = obj.Unit;
            let new_room = document.createElement('h4');
            let new_text = document.createTextNode('Room ' + obj.Unit);
            new_room.appendChild(new_text);
            items_div.appendChild(new_room);
        }
        let sep_txt = ' - ';
        let new_item = document.createElement('p');
        let new_text = document.createTextNode('Step ' + obj.Step + sep_txt + '<b>' + obj.Item + '</b>' + ' ---NOTES--- ' + obj.Notes);
        new_item.appendChild(new_text);
        items_div.appendChild(new_item);
    });

        return items_div;
};