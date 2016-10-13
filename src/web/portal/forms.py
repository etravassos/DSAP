from django import forms
from django.contrib.auth.forms import AuthenticationForm 

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import InlineRadios, InlineCheckboxes
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions
from src.core.utils import constants as const

def get_supported_tlds():
    tlds = []
    for val in const.supported_tlds:
        tlds.append((val, "." + val))
    return tuple(tlds)

class MessageForm(forms.Form):
    dname_text_input = forms.CharField(label="Domain")
    ext_selector = forms.TypedChoiceField(label=False, choices=get_supported_tlds(), initial='ca')
    preview_check = forms.ChoiceField(
                choices = (
                    ('preview_mode', "Preview"),
                    # ('live_mode', "Live"),
                ),
                label="",
                initial= 'preview_mode',
                )

    # Uni-form
    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.form_id = 'dsap_query_form'
    helper.layout = Layout(
        Div(
            Field('dname_text_input',  css_class="form-controlz"),
            Field('ext_selector',  css_class="form-controlz"),
            InlineCheckboxes('preview_check', css_class="form-controlz"),
            css_id="form_container_div"
        ),
        
        FormActions(
            Submit('bootstrap_action_btn', 'Secure Domain', css_class="btn-primary form-controlz"),
            Submit('update_action_btn', 'Secure Domain Maintenance', css_class="btn-primary form-controlz"),
            Submit('unsign_action_btn', 'Remove Secure Delegation', css_class="btn-primary form-controlz")
        )
    )
    # helper['text_input'].wrap(Field, css_class="form-control")
    def __init__(self):
        super().__init__()
        text_input_kwargs = { 'css_class':    "form-control form-controlz",
                              'style':        "display:inline;",
                        }
        self.helper['dname_text_input'].wrap(AppendedText, "", **text_input_kwargs)
        selector_kwargs = { 'css_class':    "form-control form-controlz",
                        }
        self.helper['ext_selector'].wrap(AppendedText, "", **selector_kwargs)
    
class LoginForm(AuthenticationForm):
    #With temporary readonly cred values!
    username = forms.CharField(label="Username", max_length=30, 
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'username', 'value':'cira'}))
    password = forms.CharField(label="Password", max_length=30, 
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'name': 'password', 'value':'dsap'}))