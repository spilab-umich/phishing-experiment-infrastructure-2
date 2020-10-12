var max_log_size = 3;
var send_intervals = 5000;
var timeOutId = 0;

// ajax_send_trigger();

function createLog(link, action, time){
    var link_id = 0, link_url;
    if (time==undefined) time= -1;
    if (typeof(link) == 'string') link_url = link;
    else if (link.attr('label')) link_url = link.attr('label');
    else if (link.attr('href')) link_url = link.attr('href');
    else link_url = '';
    // If link has an id, it should be that, else it's 0
    if (link[0].id) link_id = link[0].id;
    // var dest = '{% url "mail:ajax" %}';
    var d_to_add = {
        'username': username,
        'link': link_url,
        'action': action,
        'hover_time': time,
        'action': action,
        'link_id': link_id,
    };
    // var things = JSON.stringify({d_to_add});
    // var things = d_to_add.toString();
    console.log(d_to_add);
    add_to_array(d_to_add);
    // console.log(data);
}

function add_to_array(row){
    rows.push(row);
    console.log(rows.length);
    if (rows.length>0 || timeOutId == 0) {
        timeOutId = setTimeout(function(){
            send_data(rows);
        }, send_intervals);
    }
    if (rows.length==max_log_size){
        send_data(rows);
    }
}

function send_data(d){
    data = JSON.stringify(d);
    $.ajax({
        url: ajax_dest,
        method: 'POST',
        data: {
            data,
            csrfmiddlewaretoken: token,
        },
        success: function(){
            console.log('log recorded');
            console.log(data.length);
            if (timeOutId > 0) {
                clearTimeout(timeOutId);
            }
            rows = []; // This is dangerous if there is a delay between client and server but idk what else to do
        },
        error: function(){
            console.log('log failure');
        },
        // timeout: send_intervals,
    });
}