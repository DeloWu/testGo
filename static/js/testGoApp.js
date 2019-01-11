function delcfm(obj) {
    var url = obj.getAttribute("href")
    $('#url').val(url);//给会话中的隐藏属性URL赋值
    $('#delcfmModel').modal();
}

function urlSubmit(){
    var url=$.trim($("#url").val());//获取会话中的隐藏属性URL
    window.location.href=url;  
}

// 删除表格的单行
function del_row(obj) {
        var tr = obj.parentNode.parentNode;
        var tbody = tr.parentNode;
        tbody.removeChild(tr);
}

//  保存mockServer单个响应集
function save_mockServer_row(obj){
    var api_flag = 'add_single_mockServer';//区分多个不同接口标志
    var relative_api = document.getElementById('api_id').value;
    var setup_hooks = document.getElementById('setup_hooks').value;
    var teardown_hooks = document.getElementById('teardown_hooks').value;default_mockServer
    var tr = obj.parentNode.parentNode;
    var mockServer_name = tr.childNodes[0].textContent;
    var content_type = tr.childNodes[1].firstChild.value;
    var status_code = tr.childNodes[2].firstChild.value;
    var mockServer_headers = tr.childNodes[3].textContent;
    var mockServer_content = tr.childNodes[4].textContent;
    var description = tr.childNodes[5].textContent;
    var mock_status_class = tr.childNodes[6].firstChild.className;
    var mock_status = new String;
    if(mock_status_class.search('bootstrap-switch-off')==-1){
        mock_status = '1';
    }
    else{
        mock_status = '0';
    }
    $.ajax({
            url: "/autoTest/mockServer_add/",
            type: "post",
            data:{
                "api_flag": "add_single_mockServer",
                "relative_api": relative_api,
                "setup_hooks": setup_hooks,
                "teardown_hooks": teardown_hooks,
                "mockServer_name": mockServer_name,
                "content_type": content_type,
                "status_code": status_code,
                "mockServer_headers": mockServer_headers,
                "mockServer_content": mockServer_content,
                "description": description,
                "mock_status": mock_status,
            },
            success : function(data){
                // 为<tr>添加name="mockServer-**(id)"
                tr.setAttribute("name",'mockServer-' + data["mockServer_id"]);
                
            },
            error : function(data){
                console.log("保存失败！");
            }
        });
    
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

// 添加mockServer行
function add_mockServer_row(){
    var content_type = '<select name="mockServer_row" class="form-control">' + '<option value="json"> json </option>' + '<option value="text"> text </option>' + '<option value="xml"> xml </option>' + '<option value="html"> html </option>' + '</select>';
    var status_code = '<select name="mockServer_row" class="form-control">' + '<option value="200"> 200 OK </option>' + '<option value="301"> 301 Moved  </option>' + '<option value="302"> 302 Moved  </option>' + '<option value="400"> 400 Bad Request </option>' + '<option value="403"> 403 Forbidden </option>' + '<option value="404"> 404 Not Found </option>' + '<option value="405"> 405 Method Not Allowed </option>' + '<option value="500"> 500 Internal Server Error </option>' + '<option value="502"> 502 Bad Gateway </option>' + '<option value="504"> 504 Gateway Timeout </option>' + '</select>';
    var row_content = '<tr>' + '<td contenteditable="true" name="mockServer_name"></td>' + '<td contenteditable="true" name="content_type">' + content_type + '</td>' + '<td contenteditable="true" name="status_code">' + status_code + '</td>' + '<td contenteditable="true" name="mockServer_headers"></td>' + '<td contenteditable="true" name="mockServer_content"></td>' + '<td contenteditable="true" name="description"></td>' + '<td><input type="checkbox" name="switch" checked></td>' + '<td><button class="btn btn-success" onclick="save_mockServer_row(this)">保存</button><button class="btn btn-danger" onclick="del_row(this)">删除</button></td>' + '</tr>';
    $("#mockServer-table tbody").append(row_content);
    $('[name="switch"]').each(function(){
                $(this).bootstrapSwitch({  
                onColor:"info",  
                offColor:"danger",  
                size:"small",
            onSwitchChange:function(event,state){
                if(state==true){  
                   alert('已打开');  
                }else{  
                    alert('已关闭');  
                }  
            }  
     
                });
            });
}

// 添加mockServer匹配条件行
function add_mockSever_condition_row(){
    var select_content = '<select name="comparator" class="form-control">' + '<option value="eq"> = </option>' + '<option value="gt"> > </option>' + '<option value="ge"> >= </option>' + '<option value="lt"> < </option>' + '<option value="le"> <= </option>' + '<option value="len_eq">长度等于</option>' + '<option value="len_gt">长度大于</option>' + '<option value="len_lt">长度小于</option>' + '<option value="contains">包含</option>' + '<option value="contained_by">被包含</option>' + '<option value="startswith">startswith</option>' + '<option value="endswith">endswith</option>' +'</select>';
    //后面通过后端传mockServer_suite
    var mockSevrer_suite = '<select name="mockServer-condition" class="form-control">' + '<option value="200"> 200 OK </option>' + '<option value="404"> 404 NOT Found </option>' + '</select>';
    var row_content = '<tr>' + '<td contenteditable="true" name="request_args"></td>' + '<td>' + select_content + '</td>' + '<td contenteditable="true" name="expect_value"></td>' + '<td>' + mockSevrer_suite + '</td>' + '<td><button class="btn btn-success" onclick="">保存</button><button class="btn btn-danger" onclick="del_row(this)">删除</button></td>' + '</tr>';
    $("#mockServer-conditions-table tbody").append(row_content);
}