// hover time threshold in ms
// this is useful if you don't want any hover logs below a certain amount of hover time
// e.g., setting this to 250 will not record any hover interactions below 250 ms
let hover_time_limit = 0;
let warning_shown = false;
let warning_shown_text = 'warning-shown';

function createLog(link, action, emailid, hover_time){
    let link_id = 0, link_url;
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
    let timestamp = new Date($.now()).toUTCString().replace(',','');
    let d = {
        'ref': emailid,
        'link': link_url,
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
    link.attr('onclick', 'return false;')
        .css('cursor','not-allowed');
}

// adjusts the cursor, changes the ID to indicate the link is clickable
// takes an anchor tag object and an integer link ID
function enable_link(link){ // 
    link.css('cursor','pointer')
        .attr('id', parseInt(link.attr('id')) + 1);
}

// takes a string anchor tag ID, appends the class email-link
function add_email_link_class(email_link_id){
    let _this = $('.email-container a#'+email_link_id);
    _this.addClass('email-link');
}

// add click listener to cj span on warning link
function make_warning_link_clickable(for_link){
    $('a.warning-link').on('click',function(){
        let win = window.open(for_link,"_blank");
    });
    enable_link($('a.warning-link'));
}

// add click listener to cj span on email link
function make_email_link_clickable(for_link){
    $('a.email-link').on('click',function(){
        let win = window.open(for_link,"_blank");
    });
    enable_link($('a.email-link'));
}

function load_warning(p_id,for_link,fa,time_delay,fp){
    // copy plink
    let _this = $('.email-container a#'+p_id);
    // disable p-link clickability
    let link_hovered = false;
    $('a.warning-link')
        .attr('target','_blank')
        .attr('onclick','return false;')
        .attr('id',parseInt(p_id)+4) // disable the warning-link by default
        .attr('href', _this.attr('href'));
    if (fp){
        // add fp link to warning-link
        let fp_link = document.getElementsByClassName('warning-link')[0];
        fp_link.innerHTML = _this.attr('href');
        fp_link.href = _this.attr('href');
    }

    // Create a blank variable for the subheader text
    let final_subhead_text = '';
     // enable links for warnings with no time delay
     if (td <= 0){
        // make warning link clickable     
        make_warning_link_clickable(for_link);
        // make email link clickable for non-focused attention groups
        if (!fa) {
            make_email_link_clickable(for_link);
        }

    }
    // disable links during active time delay
    else {
        disable_link($('a.warning-link')); //this adds the no cursor and changes the link ID
        disable_link($('a.email-link'));
        $('span.secsRemaining').text(String(time_delay) );
    }


    _this.attr('data-toggle', 'tooltip');

    //initialize on-hover interactivity
    $("a[data-toggle='tooltip']")
        .on('mouseenter', function(){
            $('div.tooltip').css({
                'opacity':100,
                'display':'block'});
            if (!warning_shown){
                createLog(warning_shown_text,warning_shown_text,eid);
                warning_shown = true;
            }
            // for groups with time_delay > 0, interval has to trigger
            // trigger this countdown only if it is the first time the link has been hovered on this page
            if (time_delay > 0 && !link_hovered){
                link_hovered = true;
                let countdownToClick = setInterval(function(){
                    time_delay--;
                    $('span.secsRemaining').text(time_delay);
                    // enable warning link after time delay, including email link for non-FA
                    if (time_delay <= 0){                       
                        if (!fa){
                            final_subhead_text = 'Please check the link carefully before proceeding. The link is now active.';
                            make_email_link_clickable(for_link);
                        }
                        else {
                            final_subhead_text = 'Please check the link carefully before proceeding. The link in the warning is now active.';
                        }
                        make_warning_link_clickable(for_link);
                        $('span.timer').text(final_subhead_text);
                        clearInterval(countdownToClick);
                    }
                },1000);
            }
        }).on('mouseleave', function(){
        let refreshInterval = setInterval(function() {
            // if both the tooltip and the link are not hovered over, clear the interval check and dismiss the tooltip
            if (!$('.tooltip:hover').length && !$("[data-toggle='tooltip']:hover").length) {
                $('.tooltip').css({
                    'opacity':0,
                    'display':'none'});
                clearInterval(refreshInterval);
            }
        }, 500);                    
    });
}

// add click and hover listeners to any anchor tag with an href, a label, or a tag within the email container
// warning-link is outside of the email container so we add this manually
function initListeners(eid){
    $('a[href], a[label]').each(function(){
        addclicklistener($(this), eid);
    });

    $('.email-container a, a.warning-link').each(function(){
        addHoverListener($(this), eid);
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
        let time = end - start;
        if (time >= hover_time_limit) {
          createLog(_this, 'hover', emailid, time);
        }
    });
}


// position tooltip once page load is complete
window.onload = function(){
    let width = $('a.email-link').outerWidth();
    let wWidth = $('.tooltip').outerWidth();
    let pos = document.getElementsByClassName('email-link')[0].getBoundingClientRect();
    $('.tooltip').css({
        'top': pos.bottom,
        'left': pos.left - 0.5 * (wWidth - width),
    });
}