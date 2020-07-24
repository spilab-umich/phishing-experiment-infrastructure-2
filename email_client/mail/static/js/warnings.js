function load_warning(group_num){
    const warning_text = "<div class='row banner-w text-center'><div style='padding: 15px;'><p class=''>Warning text here</p></div></div><style>.banner-w {padding: 10px;height: 100px;border-radius: 4px;background-color: #A64452;}</style>";
    // const warning_text = "{% include warning_fname %}"
    if (group_num=="4"){
        $(warning_text).insertBefore('.sender-info');
    }
}