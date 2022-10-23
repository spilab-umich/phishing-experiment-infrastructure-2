let hover_time_limit = 0;
// let rows = [];
// let time_delay = 5;
let warning_shown = false;
let warning_shown_text = 'warning-shown';

// automatically assign id attributes to all links in an email
function id_links(){
    let i = 1;
    $('.email-container a').each(function(){
        $(this).attr('id', i*10);
        i++;
        // open all email links in a new window
        $(this).attr('target',  '_blank');
    });
}

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
    // consider changing to Date().toUTCString();
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
    link.attr('onclick', 'return false')
        .css('cursor','not-allowed');
}

function addTemplate(_node, template){
    _node.after(template);
}

// adjusts the cursor, changes the ID
// takes an anchor tag object and two integer IDs
function enable_link(link, link_id, p_loc){ // 
    link.css('cursor','pointer')
        // all live phishing links have id = -100
        .attr('id', link_id + p_loc); // , email_id+p_id);
}

// takes a string anchor tag ID
function add_email_link_class(email_link_id){
    // let email_span = '<span id="em-added"></span>';
    let _this = $('.email-container a#'+email_link_id);
    _this.addClass('email-link');

    // place cj span around email-link
    // $(window).on("load",function(){
    //     $(_this).prepend(email_span)
    //         // .css('position','relative')
    //         .css('z-index',1);
    //     $('span#em-added').css({
    //         height: _this.height(),
    //         width: _this.width(),
    //         zIndex: 2,
    //         opacity: 0,
    //         position: "absolute",
    //     });
    // });
}

// add click listener to cj span on warning link
function make_warning_link_clickable(for_link, p_id){
    $('a.warning-link').on('click',function(){
        let win = window.open(for_link,"_blank");
        // win.focus();
    });
    enable_link($('a.warning-link'),parseInt(p_id),2);
}

// add click listener to cj span on email link
function make_email_link_clickable(for_link, p_id){
    $('a.email-link').on('click',function(){
        let win = window.open(for_link,"_blank");
        // win.focus();
    });
    enable_link($('a.email-link'),parseInt(p_id),1);
}

// changes href of desired link to the selected phishing link and disable the link
function adjust_link(p_id,p_url){
    let _this = $('.email-container a#'+p_id);
    _this.attr('href', p_url);
}

function load_warning(group_num,p_id,for_link,fa,time_delay){
    // copy plink
    let _this = $('.email-container a#'+p_id);
    
    // adjust plink
    let link_hovered = false;
    // let raw_link = _this.attr('href');
    // // parse out plink components
    // let url = new URL(raw_link);
    // let hostname = url.hostname.split('www.');
    // let protocol = url.protocol + '//www.';
    // if (hostname.length > 1){
    //     protocol += hostname[0];
    //     hostname = hostname[1];
    // }
    // else {
    //     hostname = hostname[0]; // hostname is always an array
    // }

    // SPACING OUT LINK IS CONDITIONAL FOR TESTING
    // if (group_num % 2 > 0){
    //     hostname = hostname.split('').join(' '); // separate the characters in the host  
    // }

    // END TESTING

    // DOMAIN ONLY AND WHOLE LINK CLICKABLE
    // create spans for URL components
    // let pre_domain = '<span class="pre-domain"></span>';
    // let main_domain = '<span class="main-domain"></span>';
    // let post_domain = '<span class="post-domain"></span>';
    
    // populate plink with spans for URL components
    // $('a.warning-link').html(pre_domain+main_domain+post_domain);

    // BROWSER AND BUTTON STYLE HIGHLIGHTING FOR TESTING
    // apply browser style highlighting
    // if ([1,2,3].includes(group_num)){
    //     $('span.main-domain').css('color','#4F4F4F');
    //     $('span.post-domain').css('opacity',.6);
    //     $('span.pre-domain').css('opacity',.6);
    // }
    // // apply button style highlighting
    // else {
    //     $('span.main-domain').css('border-radius','15px')
    //         .css('background-color','#E8E8F0')
    //         .css('font-weight','bold')
    //         .css('padding','.2rem .3rem');
    //     $('span.post-domain').css('opacity',.6);
    //     $('span.pre-domain').css('opacity',.6);
    // }
    // END TESTING

    // populate spans with text from plink components
    // let pathname = url.pathname;
    // let search_params = url.search;
    // $('span.pre-domain').text(protocol);
    // $('span.main-domain').text(hostname);
    // $('span.post-domain').text(pathname + search_params);
    $('a.warning-link')
        .attr('target','_blank')
        .attr('onclick','return false'); // disable the warning-link by default
    // START WARNING DEPLOYMENT
    // initialize time_delay
    // let time_delay = -1;
    // set the text in the subheader
    let final_subhead_text = '';
    // create boolean for focused attention branching (groups 1, 2, 3)
    // let fa = (group_num % 7) < 4;
     // enable links for warnings with no time delay
    if ([1,4].includes(group_num)){
        // time_delay = 0;
        if (!fa) {
            make_email_link_clickable(for_link,p_id);
            // final_subhead_text = 'Please check the link carefully before proceeding.';
        }
        else {
            // final_subhead_text = 'Please check the link carefully before proceeding. The link in the warning is active.';
        }
        // enable original link in focused attention
        make_warning_link_clickable(for_link,p_id);
        // $('span.timer').text(final_subhead_text);
           // add on-click listener to warning link cj span for no FA groups
    }
    // handle warnings with time delay
    else {
        disable_link($('a.warning-link')); //this adds the no cursor and changes the link ID
        disable_link($('a.email-link'));
        // if ([2,5].includes(group_num)){
        //     time_delay = 2
        // }
        // else {
        //     time_delay = 3;
        // }
        //parseInt(p_id);
        $('span.secsRemaining').text(String(time_delay) );
        if (fa){
            final_subhead_text = 'Please check the link carefully before proceeding. The link in the warning is now active.';
        }
        else {
            final_subhead_text = 'Please check the link carefully before proceeding. The link is now active.';
        }
    }
    // let rect = $('a.email-link').getBoundingClientRect();
    // var x = rect.left;
    // var y = rect.top;
    // console.log(rect);

    _this.attr('data-toggle', 'tooltip');
    // DO IFRAME CLICKJACKING STUFF 
    // how to do iframe; set height and width to a.warning-link.height() and .length()

    // in Sprint's email, the dimensions of the anchor tag are dynamic based on the size of the image
    // to place a span over this link, you have to place the span after the image has loaded (on document ready)
    // if (for_link.slice(-1) == "1"){
    //     let offset = _this.offset();
    //     // let offset2 = $('span#em-added').offset();
    //     // console.log(offset);
    //     // console.log(offset2);
    //     // console.log(offset.left-offset2.left);
    //     $(window).on("load", function(){
    //         $('span#em-added').css({
    //             left: offset.left,
    //         });
    //     });
    // }

    //     // in Sprint's email, the dimensions of the anchor tag are dynamic based on the size of the image
    //     // to place a span over this link, you have to place the span after the image has loaded (on document ready)
    //     if (for_link.slice(-1) == "1"){
    //         let offset = _this.offset();
    //         // let offset2 = $('span#em-added').offset();
    //         // console.log(offset);
    //         // console.log(offset2);
    //         // console.log(offset.left-offset2.left);
    //         $(window).on("load", function(){
    //             $('span#em-added').css({
    //                 left: offset.left,
    //             });
    //         });
    //     }
    // }
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
            // trigger this countdown only if it is the first time the link has been hovered
            if (time_delay > 0 && !link_hovered){
                link_hovered = true;
                let countdownToClick = setInterval(function(){
                    time_delay--;
                    $('span.secsRemaining').text(time_delay);
                    // enable warning link after time delay, including email link for non-FA
                    if (time_delay <= 0){                       
                        if (!fa){
                            make_email_link_clickable(for_link,p_id);
                        }
                        make_warning_link_clickable(for_link,p_id);
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
        let time = end - start;
        if (time >= hover_time_limit) {
          createLog(_this, 'hover', emailid, time);
        }
    });
}


// position tooltip once everything loads
window.onload = function(){
    let offset = $('a.email-link').position();
    let height = $('a.email-link').outerHeight();
    let width = $('a.email-link').outerWidth();
    let wWidth = $('.tooltip').outerWidth();
    var top = offset.top;
    var right = offset.left;
    // console.log(offset);
    // $('.tooltip').css({
    //     // 'position': 'absolute',
    //     'right': offset.left,
    //     'top': offset.top,
    // });
    let pos = document.getElementsByClassName('email-link')[0].getBoundingClientRect();
    // console.log(pos);
    $('.tooltip').css({
        // 'position': 'absolute',
        'top': pos.bottom,
        'left': pos.left - 0.5 * (wWidth - width),
    });
}