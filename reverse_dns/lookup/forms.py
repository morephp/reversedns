from django.forms import Form

class LoginForm(forms.Form):
username = forms.CharField(max_length=100)
password = forms.CharField(widget=forms.PasswordInput(render_value=False),max_length=100)

	