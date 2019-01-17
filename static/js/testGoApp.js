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
    console.log("del_row function worked!");
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
    $('[name="switch"]:last').each(function(){
                $(this).bootstrapSwitch({  
                onColor:"info",  
                offColor:"danger",  
                size:"small",
            // onSwitchChange:function(event,state){
            //     if(state==true){  
            //        alert('已打开');  
            //     }else{  
            //         alert('已关闭');  
            //     }  
            // }  
     
                });
            });
}

// 添加mockServer匹配条件行
    function add_mockSever_condition_row(){
        var api_id = $("#api_id option:selected").val();
        var comparator_content = '<select name="comparator" class="form-control" style="width: 200px;">' + '<option value="eq"> = </option>' + '<option value="gt"> > </option>' + '<option value="ge"> >= </option>' + '<option value="lt"> < </option>' + '<option value="le"> <= </option>' + '<option value="len_eq">长度等于</option>' + '<option value="len_gt">长度大于</option>' + '<option value="len_lt">长度小于</option>' + '<option value="contains">包含</option>' + '<option value="contained_by">被包含</option>' + '<option value="startswith">startswith</option>' + '<option value="endswith">endswith</option>' +'</select>';
        //后面通过后端传mockServer_suite
        // var status_code = '<select name="mockServer-condition" class="form-control">' + '<option value="200"> 200 OK </option>' + '<option value="301"> 301 Moved  </option>' + '<option value="302"> 302 Moved  </option>' + '<option value="400"> 400 Bad Request </option>' + '<option value="403"> 403 Forbidden </option>' + '<option value="404"> 404 Not Found </option>' + '<option value="405"> 405 Method Not Allowed </option>' + '<option value="500"> 500 Internal Server Error </option>' + '<option value="502"> 502 Bad Gateway </option>' + '<option value="504"> 504 Gateway Timeout </option>' + '</select>';
        var data_type_content = '<select name="headers_data_type" class="form-control">' + '<option value="string"> string </option>' + '<option value="int"> int </option>' + '<option value="double"> double </option>' + '<option value="list"> list </option>' + '<option value="dict"> dict </option>' + '</select>';
        $.ajax({
                url: "/autoTest/find_data/",
                type: "post",
                data:{
                    "model": "mockServer",
                    "data_id": api_id,
                    "data_name": "add_mockServer_condition",
                },
                success : function(data){
                    var row_content = '<tr>' + data['mockServer_default_condition_html'] + '<td>' + comparator_content + '</td>' + '<td contenteditable="true" name="expect_value"></td>'+ '<td contenteditable="true" name="data_type">' + data_type_content + '</td>' + '<td name="mockServer">' + data['mockServer_select_html'] + '</td>' + '<td><button class="btn btn-success" onclick="save_mockServer_condition_row(this)">保存</button><button class="btn btn-danger" onclick="del_row(this)">删除</button></td>' + '</tr>';
                    $("#mockServer-conditions-table tbody").append(row_content);
                },
                error : function(data){
                    alert("此接口没有设置请求参数！")
                }
            });

    }


//  保存mockServer单个响应集
function save_mockServer_row(obj){
    var api_flag = 'save_single_mockServer';//区分多个不同接口标志
    var relative_api = document.getElementById('api_id').value;
    var setup_hooks = document.getElementById('setup_hooks').value;
    var teardown_hooks = document.getElementById('teardown_hooks').value;
    var tr = obj.parentNode.parentNode;
    try{
        var mockServer_id = tr.getAttribute("name").slice(11,);
    } catch (TypeError){
        mockServer_id = '';
    }
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
    // 判断响应头若不为空，是否为正确的json格式
    if(mockServer_headers != ''){
        try{
            var headers_json = JSON.parse(mockServer_headers);
        } catch{
            alert("响应头json格式不正确！请检查修改后再次保存");
            return ;
        }
    }
    // 响应内容选择json格式，并且不为空，则判断是否为正确的json格式
    if(content_type=='json' & mockServer_content != ''){
        try{
            var content_json = JSON.parse(mockServer_content);
        } catch{
            alert("响应内容json格式不正确！请检查修改后再次保存");
            return ;
        }
    }

    $.ajax({
            url: "/autoTest/mockServer_add/",
            type: "post",
            data:{
                "mockServer_id":mockServer_id,
                "api_flag": api_flag,
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
                alert('保存成功!');
                //  为默认响应 下拉框 和 返回响应下拉框 加上新保存的选项
                $("select[name='mockServer_select'").each(function(index,element){
                    var option_node = document.createElement("option");
                    var name_text_node=document.createTextNode(data['mockServer_name']);
                    var value_attr_node = document.createAttribute("value");
                    value_attr_node.value = data['mockServer_id'];
                    option_node.setAttributeNode(value_attr_node);
                    option_node.appendChild(name_text_node);
                    element.appendChild(option_node);
                });
                
            },
            error : function(data){
                console.log("保存失败！");
            }
        });
    
    
}

//  保存mockServer单个响应集--去掉保存成功提示，用于保存全部使用
function save_mockServer_row_son(obj){
    var api_flag = 'save_single_mockServer';//区分多个不同接口标志
    var relative_api = document.getElementById('api_id').value;
    var setup_hooks = document.getElementById('setup_hooks').value;
    var teardown_hooks = document.getElementById('teardown_hooks').value;
    var tr = obj.parentNode.parentNode;
    try{
        var mockServer_id = tr.getAttribute("name").slice(11,);
    } catch (TypeError){
        mockServer_id = '';
    }
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
                "mockServer_id":mockServer_id,
                "api_flag": api_flag,
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

 // 保存mockServer单个匹配响应条件
function save_mockServer_condition_row(obj){
    var api_flag = "save_single_mockServer_condition";
    var relative_api = document.getElementById('api_id').value;
    var tr = obj.parentNode.parentNode;
    try{
        var mockServer_id = tr.getAttribute("name").slice(11,);
    } catch (TypeError){
        mockServer_id = '';
    }
    var mockServer_condition_arg = tr.childNodes[0].firstChild.value;
    var mockServer_condition_comparator = tr.childNodes[1].firstChild.value;
    var mockServer_condition_expect_value = tr.childNodes[2].textContent;
    var mockServer_condition_dataType = tr.childNodes[3].firstChild.value;
    var mockServer_condition_status_code = tr.childNodes[4].firstChild.value;
    $.ajax({
            url: "/autoTest/mockServer_add/",
            type: "post",
            data:{
                "relative_api": relative_api,
                "mockServer_id":mockServer_id,
                "api_flag": api_flag,
                "mockServer_condition_arg": mockServer_condition_arg,
                "mockServer_condition_comparator": mockServer_condition_comparator,
                "mockServer_condition_expect_value": mockServer_condition_expect_value,
                "mockServer_condition_dataType": mockServer_condition_dataType,
                "mockServer_condition_status_code": mockServer_condition_status_code,
            },
            success : function(data){
                // 为<tr>添加name="mockServer-**(id)"
                tr.setAttribute("name",'mockServer-' + data["mockServer_id"]);
                alert("保存成功!");
            },
            error : function(data){
                console.log("保存失败！");
            }
        });    
}
 // 保存mockServer单个匹配响应条件--去掉保存成功提示，用于保存全部使用
function save_mockServer_condition_row_son(obj){
    var api_flag = "save_single_mockServer_condition";
    var relative_api = document.getElementById('api_id').value;
    var tr = obj.parentNode.parentNode;
    try{
        var mockServer_id = tr.getAttribute("name").slice(11,);
    } catch (TypeError){
        mockServer_id = '';
    }
    var mockServer_condition_arg = tr.childNodes[0].firstChild.value;
    var mockServer_condition_comparator = tr.childNodes[1].firstChild.value;
    var mockServer_condition_expect_value = tr.childNodes[2].textContent;
    var mockServer_condition_dataType = tr.childNodes[3].firstChild.value;
    var mockServer_condition_status_code = tr.childNodes[4].firstChild.value;
    $.ajax({
            url: "/autoTest/mockServer_add/",
            type: "post",
            data:{
                "relative_api": relative_api,
                "mockServer_id":mockServer_id,
                "api_flag": api_flag,
                "mockServer_condition_arg": mockServer_condition_arg,
                "mockServer_condition_comparator": mockServer_condition_comparator,
                "mockServer_condition_expect_value": mockServer_condition_expect_value,
                "mockServer_condition_dataType": mockServer_condition_dataType,
                "mockServer_condition_status_code": mockServer_condition_status_code,
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


// mockServer页面保存全部
function save_all_mockServer(){
    // var api_flag = 'save_all_mockServer';//区分多个不同接口标志
    // var setup_hooks = document.getElementById('setup_hooks').value;
    // var teardown_hooks = document.getElementById('teardown_hooks').value;
    save_default_mockServer();
    // 遍历保存响应集信息
    $('#mockServer-table tbody tr td>button[onclick="save_mockServer_row(this)"]').each(function(index, ele){
        save_mockServer_row_son(ele);
    });
    //  遍历保存匹配响应条件信息
    $('#mockServer-conditions-table tbody tr td>button[onclick="save_mockServer_condition_row(this)"]').each(function(index, ele){
        save_mockServer_condition_row_son(ele);
    });
    alert("全部保存成功");
}

// 保存mokServer_update的默认响应信息
function save_default_mockServer(){
    var api_flag = 'save_default_mockServer';//区分多个不同接口标志
    var api_id = document.getElementById('api_id').value;
    var default_mockServer_id = document.getElementById('default_mockServer').value;
    $.ajax({
                url: "/autoTest/mockServer_update/",
                type: "post",
                data:{
                    "api_id": api_id,
                    "api_flag": api_flag,
                    "default_mockServer_id": default_mockServer_id,
                },
                success : function(data){
                    break;
                },
                error : function(data){
                    console.log("查找指定接口失败");
                    console.log('api_id: ', api_id);
                }
            });

}