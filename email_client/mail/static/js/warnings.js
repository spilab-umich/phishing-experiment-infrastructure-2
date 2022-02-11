let hover_time_limit = 0;
// let rows = [];
// let time_delay = 5;
let warning_shown = false;
let warning_shown_text = 'warning-shown';

// automatically assign id attributes to all links in an email
function id_links(){
    var i = 1;
    $('.email-container a').each(function(){
        $(this).attr('id', i);
        i++;
    });
}

function createLog(link, action, emailid, hover_time){
    var link_id = 0, link_url;
    if (hover_time==undefined) hover_time= -1;
    // if link has an href property, assign it to link_url
    if (typeof(link) == 'string') link_url = link;
    // else if link has a label property, assign it to link_url
    else if (link.attr('href')) link_url = link.attr('href');
    // else if link is a string, assign the string to link_url
    else if (link.attr('label')) link_url = link.attr('label');
    // else if link is none of these things, just type 'NaN'
    else link_url = 'NaN'; 
    if (link[0].id) link_id = link[0].id; // If link has an id, link_id should be that id, else it's 0
    // consider changing to Date().toUTCString();
    var timestamp = new Date($.now()).toUTCString();
    var d = {
        'ref': emailid,
        'link': link_url,
        'action': action,
        'hover_time': hover_time,
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

// disables clicking on a phishing link
function disable_link(link){
    link.attr('onclick', 'return false')
        .css('cursor','not-allowed');
}

function addTemplate(_node, template){
    _node.after(template);
}

function enable_link(link){
    link.css('cursor','pointer')
        .removeAttr('onclick')
        // all live phishing links have id = -100
        .attr('id',-100);
}

// changes href of desired link to one of several phishing links
function adjust_link(group_num,p_id){
    var _this = $('.email-container a#'+p_id);
    // unrelated domains group_num % 3 = 0
    // sort of related domains group_num % 3 == 1
    // brand domains group_num % 3 = 2
    var plinks = [
        ['https://www.hrzzhfs.xyz/', 'https://dkozzlfods.info/', 'https://etooicdfi.studio/something'],
        ['https://www.financial-pay.info/global-service/', 'https://www.online-shopping-payment.com/', 'https://www.client-mail-services.com/'],
        ['https://www.westernunion-pay.com/global-service/track-transfer/', 'https://www.walmartpay.com/something','https://mail.google-services.com/'],
    ];
    if (eid == 3){
        var raw_link = plinks[group_num % 3][0];
    }
    else if (eid == 2){
        var raw_link = plinks[group_num % 3][1];
    }
    else if (eid == 1){
        var raw_link = plinks[group_num % 3][2]
    }
    _this.attr('href', raw_link);
}

function load_warning(group_num,p_id){
    // adjust group_num for warning assignment
    var adj_group_num = group_num % 27;
    // create boolean for branching
    var fa = adj_group_num > 11;
    // import the template
    var template = document.getElementsByTagName("template")[0];
    var clon = template.content.cloneNode(true);
    var _this = $('.email-container a#'+p_id);
    addTemplate(_this, clon);
    // change href attributes    
    var raw_link = _this.attr('href');
    var url = new URL(raw_link);
    // create domain text
    var hostname = url.host.split('www.');
    if (hostname.length > 1){
        hostname = hostname[1]
    }
    else {
        hostname = hostname[0];
    }
    hostname = hostname.split('').join(' '); // separate the characters in the host    
    var pathname = url.pathname;
    // add domain text to warning
    $('span.url-domain').text(hostname);
    $('span.url-path').text(pathname);
    $('a.warning-link').attr('href', raw_link); 
    // set time_delay for each group
    var timedelay_num = adj_group_num % 4;
    let time_delay = -1;
    // console.log(group_num);
    let inst_text = '';
    if (fa){
        inst_text = 'Click link in the warning to proceed.';
    }
    else {
        inst_text = 'Link active';
    }
    switch(timedelay_num){
        // default:
        //     console.log('error in assigning timedelay');
        case 0:
            time_delay = 0;
            break;
        case 1:
            time_delay = 3;
            break;
        case 2:
            time_delay = 5;
            break;
        case 3:
            time_delay = 7;
            break;
    }
    // disable all original links
    disable_link(_this);
    // activate links with no time delay, including original link for non-FA
    if (time_delay < 1){
        enable_link($('a.warning-link'));
        $('li.timer').text(inst_text);
        if (!fa){
            enable_link(_this);
        }
    }
    // add time_delay text if time_delay and disable the warning-link
    else {
        $('span.secsRemaining').text(time_delay);
        disable_link($('a.warning-link'));
    }
    _this.attr('data-toggle', 'tooltip');
    $("a[data-toggle='tooltip']")
        .on('mouseenter', function(){
            $('div.tooltip').css('opacity',100);
            if (!warning_shown){
                createLog(warning_shown_text,warning_shown_text,eid);
                warning_shown = true;
            }
            // for groups with time_delay > 0, interval has to trigger
            if (time_delay > 0){
                var countdownToClick = setInterval(function(){
                    time_delay--;
                    $('span.secsRemaining').text(time_delay);
                    // enable links if no time_delay, including original link for non-FA
                    if (time_delay <= 0){
                        enable_link($('a.warning-link'));
                        $('li.timer').text(inst_text);
                        if (!fa){
                            enable_link(_this);
                        }
                        clearInterval(countdownToClick);
                    }
                },1000);
            }
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

// function addTouchListener(_this, emailid) {
//     _this.on('touchstart', function(){
//         createLog(_this, 'touchstart', emailid);
//     });
// }

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

