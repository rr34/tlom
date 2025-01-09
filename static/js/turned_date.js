function turned_ticker (data_obj) {
    let items_div = document.createElement('div');
    data_obj.forEach(function(obj) {
        room_current = obj.Unit;
        let new_room = document.createElement('p');
        let new_text = document.createTextNode(obj.Unit + ' - ' + obj.Date);
        new_room.appendChild(new_text);
        items_div.appendChild(new_room);
});

    return items_div;
};