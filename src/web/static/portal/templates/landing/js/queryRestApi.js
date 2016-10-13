
qmethod_routes = {"POST": "bootstrap/", "PUT": "maintenance/", "DELETE": "unsign/"};

function queryRestApi(q_method, prev_check) {
    q_domain = getDname(formValues["dname_text_input"], formValues["ext_selector"]); 
    
    if (prev_check){
        endpoint_extra = qmethod_routes[q_method];
        q_method = "GET";
    } else { endpoint_extra = ""; }

    jQuery.ajax({
            type: q_method,
            url: "/api/domains/" + q_domain + "/cds/" + endpoint_extra,
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data, status, jqXHR) {

                $(function() {
                    $("#rf_domain").html(data["domain"] + " " + jqXHR.status + ": " + jqXHR.statusText); // data["domain"] type: string - no need to stringify
                    $("#rf_domain").show();

                    $("#rf_description").html(data["description"]); // data["description"] type: string - no need to stringify
                    $("#rf_description").show();

                    $("#rf_debug").html(JSON.stringify(data["debug"], null, 4) );
                    $("#rf_debug").show();

                    $("#rf_epp_result").html(JSON.stringify(data["epp"], null, 4) );
                    $("#rf_epp_result").show();

                    $("#rf_lloading").hide();
                    $(".form-controlz").prop( "disabled", false );
                });
            },
        
            error: function (jqXHR, status) {

                edata = jqXHR.responseJSON;
                $("#rf_domain").addClass('eprettyprint').removeClass('prettyprint');
                $("#rf_debug").addClass('eprettyprint').removeClass('prettyprint');
                $("#rf_epp_result").addClass('eprettyprint').removeClass('prettyprint');

                $(function() {
                    if (edata == null) {
                        
                        $("#rf_domain").html(jqXHR.status + ": " + jqXHR.statusText); // data["domain"] type: string - no need to stringify
                        $("#rf_domain").show(); 

                    } else {

                        $("#rf_domain").html(edata["domain"] + " " + jqXHR.status + ": " + jqXHR.statusText); // data["domain"] type: string - no need to stringify
                        $("#rf_domain").show();

                        if (edata["error"] != null){ // it's possible to get an error without error json if unexpected
                            $("#rf_error").html(edata["error"]); // edata["error"] type: string - no need to stringify
                            $("#rf_error").show();
                        }

                        if (edata["debug"] != null){ // it's possible to get an error without debug if unexpected
                            $("#rf_debug").html(JSON.stringify(edata["debug"], null, 4) );
                            $("#rf_debug").show();
                        }

                        if (edata["epp"] != null){ // it's possible to get an error without debug if unexpected
                            $("#rf_epp_result").html(JSON.stringify(edata["epp"], null, 4) );
                            $("#rf_epp_result").show();
                        }
                    }
                    $("#rf_lloading").hide();
                    $(".form-controlz").prop( "disabled", false );
                });
            }
    });
}