function load_warning(group_num){
    var template = document.getElementsByTagName("template")[0];
    var clon = template.content.cloneNode(true);
    var names = ["https://www.chase.co.us/","https://www.yahoo.co.br/",'https://www.venmo-payment.co.us/'];
    if (group_num==5){
        $('.sender-info').before(clon);
    }
    else if (group_num==1){
        // var names = ["https://www.chase.co.us/","https://www.yahoo.co.br/"];
        $("#email_container a").each(function(){
            var raw_link = $(this).attr("href");
            if (names.indexOf(raw_link) > 0){
                $(this).attr('data-toggle', 'tooltip');
                $("a[data-toggle='tooltip']").after(clon);
                // $("a[data-toggle='tooltip']").on("mouseenter", function(){
                //     $("div.tooltip").css('opacity', 100);
                // }).on("mouseleave", function(){
                //     $("div.tooltip").css('opacity', 0);
                // });
                
            }
        });
    }
    else if (group_num==4){
        $("#email_container a").each(function(){
            // var names = ["https://www.chase.co.us/","https://www.yahoo.co.br/"];
            var raw_link = $(this).attr("href");
            if (names.indexOf(raw_link) > -1){
                $(this).attr('data-toggle', 'tooltip')
                    .attr('label',raw_link)
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
                // function closeWarning(){
                //     $(".overlay").css("display","none");
                // }
                // $("a[data-toggle='tooltip']").on("mouseenter", function(){
                //     $("div.tooltip").css('opacity', 100);
                // }).on("mouseleave", function(){
                //     $("div.tooltip").css('opacity', 0);
                // });
                
            }
        });
    }
}

function read_email(group_num, email_id){
    var p_email_ids = [12, 3, 18];
    var group_num_int = parseInt(group_num);
    var email_id_int = parseInt(email_id);
    if (p_email_ids.includes((email_id_int))){
        load_warning(group_num_int);
    }
}