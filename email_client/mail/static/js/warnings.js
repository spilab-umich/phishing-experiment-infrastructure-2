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

// changes href of desired link to the selected phishing link
function adjust_link(p_id,p_url){
    var _this = $('.email-container a#'+p_id);
    var raw_link = p_url;
    _this.attr('href', raw_link);
}

function load_warning(group_num,p_id){
    // adjust group_num to represent the time_delay group 
    // (0, 2, 4 secs) for groups ([0,3],[1,4],[2,5])
    let timedelay_num = group_num % 3;
    // create boolean for focused attention branching (groups 3, 4, 5)
    var fa = (group_num % 6) < 3;
    // import the template
    var template = document.getElementsByTagName("template")[0];
    var clon = template.content.cloneNode(true);
    var _this = $('.email-container a#'+p_id);
    let link_hovered = false;
    addTemplate(_this, clon);



    // TEMPORARY VARIABLE SETTING
    // fa = true;
    // timedelay_num = 0;
    // END VARIABLE SETTING



    // change href attributes    
    var raw_link = _this.attr('href');
    var url = new URL(raw_link);
    // create domain text
    var hostname = url.hostname.split('www.');
    let protocol = url.protocol + '//www.';
    // console.log(protocol);
    if (hostname.length > 1){
        protocol += hostname[0];
        hostname = hostname[1];
    }
    else {
        hostname = hostname[0]; // hostname is always an array
    }

    // SPACING OUT LINK IS CONDITIONAL FOR TESTING
    // if (group_num % 2 > 0){
    //     hostname = hostname.split('').join(' '); // separate the characters in the host  
    // }

    // END TESTING

    // DOMAIN ONLY AND WHOLE LINK CLICKABLE
    let pre_domain = '<span class="pre-domain"></span>';
    let main_domain = '<span class="main-domain"></span>';
    let post_domain = '<span class="post-domain"></span>';
    let iframe = '<iframe></iframe>';
    // if (group_num < 4){
    //     $('a.warning-link').prepend(pre_domain,main_domain,post_domain);
    //         // .prepend(iframe);
    // }
    // else {
    //     $('a.warning-link').before(pre_domain)
    //         .prepend(main_domain)
    //         // .prepend(iframe)
    //         .after(post_domain);
    // }
    // END TESTING

    // make whole link clickable
    $('a.warning-link').prepend(pre_domain,main_domain,post_domain);

    // apply browser style highlighting
    $('span.main-domain').css('color','black');
    $('span.post-domain').css('opacity',.6);
    $('span.pre-domain').css('opacity',.6);

    // BROWSER AND BUTTON STYLE HIGHLIGHTING FOR TESTING
    // if (group_num % 4 in [0,1]){
    //     $('span.main-domain').css('color','black');
    //     $('span.post-domain').css('opacity',.6);
    //     $('span.pre-domain').css('opacity',.6);
    // }
    // else {
    //     $('span.main-domain').css('border-radius','15px')
    //         .css('background-color','#E8E8F0')
    //         .css('font-weight','bold')
    //         .css('padding','.2rem .3rem');
    //     $('span.post-domain').css('opacity',.6);
    //     $('span.pre-domain').css('opacity',.6);
    // }
    // END TESTING

    let pathname = url.pathname;
    let search_params = url.search;
    // add domain text to warning
    $('span.pre-domain').text(protocol);
    $('span.main-domain').text(hostname);
    $('span.post-domain').text(pathname + search_params);
    // console.log('test');
    $('a.warning-link').attr('href', raw_link);
    
    // how to do iframe; set height and width to a.warning-link.height() and .length()
    // console.log($('a.warning-link').height());
    // $('iframe').on('click', function(){
    //     window.open('https://www.google.com/','_blank');
    // });



    // set initial time_delay
    let time_delay = -1;
    // set the text in the subheader
    let inst_text = '';
    if (fa){
        inst_text = 'Please check the link carefully before proceeding. The link in the warning is now active.';
    }
    else {
        inst_text = 'Please check the link carefully before proceeding. The link is now active.';
    }
    switch(timedelay_num){
        // default:
        //     console.log('error in assigning timedelay');
        case 0:
            time_delay = 0;
            break;
        case 1:
            time_delay = 2;
            break;
        case 2:
            time_delay = 3;
            break;
    }
    // disable original email link
    disable_link(_this);
    // activate warning link if no time delay, include email link for non-FA
    if (time_delay < 1){
        enable_link($('a.warning-link'));
        $('span.timer').text(inst_text);
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

    //initialize on-hover interactivity
    $("a[data-toggle='tooltip']")
        .on('mouseenter', function(){
            $('div.tooltip').css('opacity',100);
            if (!warning_shown){
                createLog(warning_shown_text,warning_shown_text,eid);
                warning_shown = true;
            }
            // for groups with time_delay > 0, interval has to trigger

            // && !countdownToClick
            if (time_delay > 0 && !link_hovered){
                // if this is the first time a link has been hovered, don't trigger this again on mouseenter
                link_hovered = true;
                var countdownToClick = setInterval(function(){
                    time_delay--;
                    $('span.secsRemaining').text(time_delay);
                    // enable links if no time_delay, including original link for non-FA
                    if (time_delay <= 0){
                        enable_link($('a.warning-link'));
                        $('span.timer').text(inst_text);
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

    // $('.email-container a').each(function(){
    //     addTouchListener($(this), eid);
    // });
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

