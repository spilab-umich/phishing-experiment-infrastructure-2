function load_warning(group_num){
    var template = document.getElementsByTagName("template")[0];
    var clon = template.content.cloneNode(true);
    if (group_num==5){
        $('.sender-info').before(clon);
    }
    else if (group_num==1){
        var names = ["chase.co.br","https://www.yahoo.co.br/"];
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
}

function read_email(group_num, email_id){
    var email_ids = [12, 3, 18];
    var group_num_int = parseInt(group_num);
    var email_id_int = parseInt(email_id);
    if (email_ids.includes((email_id_int))){
        load_warning(group_num_int);
    }
}