var formValues; 
var buttons_methods = {"bootstrap_action_btn": "POST", "update_action_btn": "PUT", "unsign_action_btn": "DELETE"};
var buttons_actions = {"bootstrap_action_btn": "bootstrap", "update_action_btn": "update", "unsign_action_btn": "unsign"};
var btnClickedFallback;

var PortalLandingModule = (function() {
    var _previewDialog = $("#preview-confirm-dialog")
    var _frm = $('#dsap_query_form'); 

    function _initPreviewDialog() {
        _previewDialog.dialog({
            autoOpen: false,
            modal: true,
            closeOnEscape: false,
            open: function(event, ui) {
                $(".ui-dialog-titlebar-close", ui.dialog | ui).hide();
            }
        });
    }

    function _initDsapForm(){
        _frm.on("click", ":submit", function(e){
            btnClickedFallback = $(this).attr('name');
        });

        _frm.submit(function (ev) { 
            _previewDialog.dialog({
                buttons : {
                    "Confirm" : { 
                        click:function() {
                            submitFormLogic();
                            $(this).dialog("close");
                        },
                        text: "Confirm",
                        class: "btn btn-primary"
                    },
                    "Cancel" : { 
                        click:function() {
                            $(this).dialog("close");
                        },
                        text: "Cancel",
                        class: "btn btn-primary"
                    },
                }
            });
            formValues = {}; 

            formValues['button'] = $(this.id).context.activeElement.name; 
            if (formValues['button'] == "dname_text_input"){
                formValues['button'] = "bootstrap_action_btn";
            }else if(typeof formValues['button'] === "undefined"){
                formValues['button'] = btnClickedFallback;
            }         

            $.each($(this).serializeArray(), function(i, field) { 
                formValues[field.name] = field.value; 
            }); 

            _previewDialog.text("Are you sure you want to " + 
                    buttons_actions[formValues['button']] + " " + formValues['dname_text_input'] + "." + formValues["ext_selector"] + "?");

            if($("#id_preview_check_1").prop('checked') == false){
                _previewDialog.dialog("open");
            } else {
                submitFormLogic();
            }

            function submitFormLogic(){
                $(".form-controlz").prop( "disabled", true );
                $.ajax({ 
                    type: _frm.attr('method'), 
                    url: _frm.attr('action'), 
                    data: formValues, 
                    success: function () { 
                        _renderResponseAjax();
                    },
                    error: function () {
                        $('#dsap_response_container').html("<pre>Request timeout</pre>");
                        $(".form-controlz").prop( "disabled", false );
                    }
                }); 
            }

            ev.preventDefault(); 
        }); 
    }

    function _renderResponseAjax() {
        return $.ajax({
            type: "GET",
            data: {"formSubmit": ""},
            success: function(data) {
                $('#dsap_response_container').html(data);
            }
        });
    }

    function initLandingPage(){
        _initPreviewDialog();
        _initDsapForm();
    }

    return {
        initLandingPage: initLandingPage
    };

})();

$(document).ready(function() { 
    PortalLandingModule.initLandingPage()
}); 