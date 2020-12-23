var hover_time_limit = 500;
var rows = [];

function load_warning(group_num, p_id){
    var template = document.getElementsByTagName("template")[0];
    var clon = template.content.cloneNode(true);
    // var names = ["https://www.chase.co.us/","https://www.yahoo.co.br/",'https://www.venmo-payment.co.us/']; // Can I pull from phish_domains.json?
    var raw_link = $('#email_container a#'+p_id).attr('href');
    if (group_num==5){
        $('.sender-info').before(clon);
    }
    else if (group_num==1){ // can load from warnings.json?
        // var names = ["https://www.chase.co.us/","https://www.yahoo.co.br/"];
        $("#email_container a#"+p_id)
            .attr('data-toggle', 'tooltip');
        $("a[data-toggle='tooltip']").after(clon);
    }
    else if (group_num==4){
        // console.log($('#email_container a#'+p_id).attr('href'));
        $('#email_container a#'+p_id)
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
    }
}

// function read_email(group_num, email_id){
//     // var p_email_ids = [12, 3, 18]; // can bring in phish_domains.json somehow?
//     var group_num_int = parseInt(group_num);
//     // var email_id_int = parseInt(email_id);
//     console.log('{{ email.phish_id }}');
//     if ('{{ email.is_phish }}'){
//         p_link_id = '{{ email.phish_id }}';
//         load_warning(group_num_int,p_link_id); // Can I also add django template from here?
//     }
//     initListeners();
// }

function initListeners(){
    $('a').each(function(){
        addclicklistener($(this));
    });

    $('#email_container a').each(function(){
        addHoverListener($(this));
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