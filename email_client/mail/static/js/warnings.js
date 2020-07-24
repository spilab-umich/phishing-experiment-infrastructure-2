function load_warning(group_num){
    var template = document.getElementsByTagName("template")[0];
    var clon = template.content.cloneNode(true);
    if (group_num==4){
        $('.sender-info').before(clon);
    }
}

function read_email(group_num, email_id){
    var warning_ids = [12, 3, 18];
    group_num_int = parseInt(group_num);
    email_id_int = parseInt(email_id);
    if (warning_ids.includes((email_id_int))){
        load_warning(group_num_int);
    }
}