var hover_time_limit = 500;
var rows = [];

function createLog(link, action, time){
    var link_id = 0, link_url;
    if (time==undefined) time= -1;
    // need to rethink these if statements
    if (typeof(link) == 'string') link_url = link;
    // else if (link.attr('label')) link_url = link.attr('label');
    // else if (link.attr('href')) link_url = link.attr('href');
    else link_url = '';
    if (link[0].id) link_id = link[0].id; // If link has an id, link_id should be that id, else it's 0
    var timestamp = new Date($.now()).toUTCString();
    var d = {
        // 'username': username,
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

function send_data(d){
    $.ajax({
        url: ajax_dest,
        method: 'POST',
        data: d,
        success: function(){

        },
        error: function(){
        },
    });
}

function load_warning(group_num, p_id){
    var template = document.getElementsByTagName("template")[0];
    var clon = template.content.cloneNode(true);
    var raw_link = $('.email-container a#'+p_id).attr('href');
    switch (group_num){
        case 1:
            $(".email-container a#"+p_id)
            .attr('data-toggle', 'tooltip');
            $("a[data-toggle='tooltip']").after(clon);
        case 4:
            $('.email-container a#'+p_id)
            .attr('data-toggle', 'tooltip')
            // .attr('label', raw_link)
            .removeAttr('href')
            .css('cursor','pointer');
            $("a[data-toggle='tooltip']").after(clon)
                .on('click', function(){
                    $('div.overlay').css('display','block');
                    $('a.warning-link').attr('href', raw_link)
                    .text(raw_link);
            });
            $('.warning-link').on('click', function(){
                $(".overlay").css("display","none");
            });
            $('.closebtn').on('click', function(){
                $(".overlay").css("display","none");
            }); 
        case 5:
            $('.sender-info').before(clon);
    }
}

function initListeners(){
    $('a[href], a[label]').each(function(){
        addclicklistener($(this));
    });

    $('.email-container a').each(function(){
        addHoverListener($(this));
    });

    $('.email-container a').each(function(){
        addTouchListener($(this));
    });
}

function addTouchListener(_this) {
    _this.on('touchstart', function(){
        createLog(_this, 'touchstart');
    });
}

function addclicklistener(_this) {
    _this.on('click', function() {
        createLog(_this, 'click');
    });
}

function addHoverListener(_this) {
    _this.hover(function() {
        start = new Date();
    }, function() {
        end = new Date();
        var time = end - start;
        if (time >= hover_time_limit) {
          createLog(_this, 'hover', time);
        }
    });
}

