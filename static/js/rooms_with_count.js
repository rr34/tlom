function rooms_with_count (data_obj) {
    let items_div = document.createElement('div');
    let room_current = 'none';
    let rooms_count = 0
    data_obj.forEach(function(obj) {
        if (obj.Unit!=room_current) {
            room_current = obj.Unit;
            let new_room = document.createElement('h3');
            if (obj.OriginalOccupancy == 'vacant') {
                rooms_count++
                let new_text = document.createTextNode(rooms_count + '. ' + obj.Unit);
                new_room.appendChild(new_text);
            }
            else {
                let new_text = document.createTextNode(obj.Unit);
                new_room.appendChild(new_text);
            }
            items_div.appendChild(new_room);
        }
        let sep_txt = ' - ';
        let new_item = document.createElement('p');
        let new_text = document.createTextNode(obj.Item + ' ---NOTES--- ' + obj.Notes);
        new_item.appendChild(new_text);
        items_div.appendChild(new_item);

    });

        return items_div;
};