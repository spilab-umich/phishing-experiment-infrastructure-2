var hover_time_limit = 0;
var rows = [];
var time_delay = 5;

function createLog(link, action, emailid, time){
    var link_id = 0, link_url;
    if (time==undefined) time= -1;
    // need to rethink these if statements
    if (typeof(link) == 'string') link_url = link;
    else if (link.attr('label')) link_url = link.attr('label');
    else if (link.attr('href')) link_url = link.attr('href');
    else link_url = 'NaN';
    if (link[0].id) link_id = link[0].id; // If link has an id, link_id should be that id, else it's 0
    var timestamp = new Date($.now()).toUTCString();
    var d = {
        'ref': emailid,
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

function disable_link(link){
    link.attr('onclick', 'return false')
        .css('cursor','not-allowed');
}

function addTemplate(_node, template){
    _node.after(template);
}

function enable_link(link){
    link.css('cursor','pointer')
        .removeAttr('onclick');
}

function load_warning(group_num, p_id){
    // On-hover, forced choice
    var template = document.getElementsByTagName("template")[0];
    var clon = template.content.cloneNode(true);
    var raw_link = $('.email-container a#'+p_id).attr('href');
    switch (group_num){
        case 0:
            _this = $(".email-container a#"+p_id);
            _this.attr('data-toggle', 'tooltip');
            disable_link(_this);
            addTemplate(_this, clon);
            $('a.warning-link').text(raw_link).attr('href',raw_link);
            disable_link($('a.warning-link'));
            $('span.secsRemaining').text(time_delay);
            $("a[data-toggle='tooltip']")
                .on('mouseenter', function(){
                    $('div.tooltip').css('opacity',100);
                    var countdownToClick = setInterval(function(){
                        if (time_delay > 0){
                            $('span.secsRemaining').text(time_delay);
                        }
                        else {
                            $('li.timer').text('You may now visit the link');
                            enable_link($('a.warning-link'));
                            clearInterval(countdownToClick);
                        }
                        time_delay--;
                    },1000);
                }).on('mouseleave', function(){
                var refreshInterval = setInterval(function() {
                    // if the tooltip or link are not hovered over, clear the interval check and dismiss the tooltip
                    if (!$(".tooltip:hover").length && !$("[data-toggle='tooltip']:hover").length) {
                        // console.log($(".tooltip:hover").length);
                        $(".tooltip").css('opacity',0);
                        clearInterval(refreshInterval);
                    }
                }, 500);                    
            });
            break;
        case 1: //temporarily changed to 2
            _this = $('.email-container a#'+p_id)
            // disable_link(_this);
            addTemplate(_this, clon);
            _this.attr('data-toggle', 'tooltip')
                .attr('onclick','return false');
            $('a.warning-link').attr('href', raw_link).text(raw_link);
            disable_link($('a.warning-link'));
            $("a[data-toggle='tooltip']")
                .on('click', function(){
                    $('div.overlay').css('display','block');
                    var countdownToClick = setInterval(function(){
                        if (time_delay > 0){
                            $('span.secsRemaining').text(time_delay);
                        }
                        else {
                            $('li.timer').text('You may now visit the link');
                            enable_link($('a.warning-link'));
                            clearInterval(countdownToClick);
                        }
                        time_delay--;
                    },1000);
            });
            $('.warning-link').on('click', function(){
                if (!(time_delay)){
                    $(".overlay").css("display","none");
                }
            });
            $('.closebtn').on('click', function(){
                $(".overlay").css("display","none");
            });
            break; 
        case 2: //temporarily changed to 3
            $('.subject-info').before(clon);
            break;
    }
    // console.log($('.email-container a#'+p_id).attr('href'));
}

function initListeners(eid){
    $('a[href], a[label]').each(function(){
        addclicklistener($(this), eid);
    });

    $('.email-container a').each(function(){
        addHoverListener($(this), eid);
    });

    $('.email-container a').each(function(){
        addTouchListener($(this), eid);
    });
}

function addTouchListener(_this, emailid) {
    _this.on('touchstart', function(){
        createLog(_this, 'touchstart', emailid);
    });
}

function addclicklistener(_this, emailid) {
    _this.on('click', function() {
        createLog(_this, 'click', emailid);
    });
}

function addHoverListener(_this, emailid) {
    _this.hover(function() {
        start = new Date();
    }, function() {
        end = new Date();
        var time = end - start;
        if (time >= hover_time_limit) {
          createLog(_this, 'hover', emailid, time);
        }
    });
}

