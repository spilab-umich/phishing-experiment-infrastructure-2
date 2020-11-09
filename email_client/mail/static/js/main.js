function createLog(link, action, time){
    var link_id = 0, link_url;
    if (time==undefined) time= -1;
    if (typeof(link) == 'string') link_url = link;
    else if (link.attr('label')) link_url = link.attr('label');
    else if (link.attr('href')) link_url = link.attr('href');
    else link_url = '';
    if (link[0].id) link_id = link[0].id; // If link has an id, link_id should be that id, else it's 0
    var timestamp = new Date($.now()).toUTCString();
    var d = {
        'username': username,
        'link': link_url,
        'action': action,
        'hover_time': time,
        'action': action,
        'link_id': link_id,
        'client_time': timestamp,
        csrfmiddlewaretoken: token,
    };
    send_data(d);
}

// function add_to_array(row){
//     rows.push(row);
//     console.log(rows.length);
//     if (rows.length>0 || timeOutId == 0) {
//         timeOutId = setTimeout(function(){
//             send_data(rows);
//         }, send_intervals);
//     }
//     if (rows.length==max_log_size){
//         send_data(rows);
//     }
// }

function send_data(d){
    // data = JSON.stringify(d);
    // data = d;
    // console.log(d);
    $.ajax({
        url: ajax_dest,
        method: 'POST',
        data: d,
        success: function(){

        },
        error: function(){
            // console.log('log failure');
        },
        // timeout: send_intervals,
    });
}