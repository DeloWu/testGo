function delcfm(obj) {
    var url = obj.getAttribute("href")
    $('#url').val(url);//给会话中的隐藏属性URL赋值
    $('#delcfmModel').modal();
}

function urlSubmit(){
    var url=$.trim($("#url").val());//获取会话中的隐藏属性URL
    window.location.href=url;  
}

// 若选择json或者application/x-www-form-urlencoded，自动添加headers行
function add_headers_contentType(obj){
    var contentType_value = 'application/'+ obj.value;
    var headers_contentType_obj_list = document.querySelectorAll("#headers-table tbody tr td[name='key']");
    try{
        var ContentTypeObject_td;
        $.each(headers_contentType_obj_list, function(i,item){
            if(item.textContent == "Content-Type"){
                ContentTypeObject_td = item;
                var tr_node = item.parentNode;
                tr_node.children[1].textContent=contentType_value;
            }
        });
        if(!ContentTypeObject_td){
            var add_content = '<tr><td contenteditable="true" name="key">Content-Type</td><td contenteditable="true" name="value">'+ contentType_value +'</td><td contenteditable="true" name="headers_necessary_flag"><select name="headers_necessary_flag" class="form-control"><option value="1"> 必填 </option><option value="0"> 非必填 </option></select></td><td contenteditable="true" name="headers_data_type"><select name="headers_data_type" class="form-control"><option value="string"> string </option><option value="int"> int </option><option value="double"> double </option><option value="list"> list </option><option value="dict"> dict </option></select></td><td contenteditable="true" name="headers_description"></td><td><button class="btn btn-danger" onclick="del_row(this)">删除</button></td></tr>';
            $("#headers-table tbody").append(add_content);
        }
    }catch(err){
        
    }
}