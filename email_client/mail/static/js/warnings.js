function load_warning(group_num){
    var template = document.getElementsByTagName("template")[0];
    var clon = template.content.cloneNode(true);
    if (group_num==1){
        $('.sender-info').before(clon);
    }
    else if (group_num==4){
        var names = ["chase.co.br","https://www.yahoo.co.br/"];
        $("#email_container a").each(function(){
            var raw_link = $(this).attr("href");
            // console.log(raw_link);
            var temp = '<div class="tooltip" role="tooltip"><div class="tooltip-arrow"></div><div class="tooltip-inner warning"></div></div>';
            var text = "Warning text goes here";
            if (names.indexOf(raw_link) > 0){
                $(this).attr('data-toggle', 'tooltip');
                var trigger = 'hover';
                //options for tooltip
                options = {
                    placement: 'bottom',
                    html: true,
                    title: text,
                    trigger: trigger,
                    template: temp,
                }
                $("[data-toggle='tooltip']").tooltip(options);
                
            }
        });
    }
}

function read_email(group_num, email_id){
    var email_ids = [12, 3, 18];
    var group_num_int = parseInt(group_num);
    var email_id_int = parseInt(email_id);
    if (email_ids.includes((email_id_int))){
        load_warning(group_num_int);
    }
}