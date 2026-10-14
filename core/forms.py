from django import forms


def _sin_espacios_ni_arroba(value):
    if len(value) < 3 or ' ' in value or '@' in value:
        raise forms.ValidationError('Mín. 3 caracteres, sin espacios ni @.')


class RegistroForm(forms.Form):
    nombre = forms.CharField(min_length=2, max_length=100,
                             error_messages={'min_length': 'Ingresa tu nombre.'})
    username = forms.CharField(max_length=150, validators=[_sin_espacios_ni_arroba])
    email = forms.EmailField(error_messages={'invalid': 'Ingresa un email válido.'})
    password = forms.CharField(min_length=6, widget=forms.PasswordInput,
                               error_messages={'min_length': 'La clave debe tener al menos 6 caracteres.'})
    presupuesto = forms.IntegerField(required=False, min_value=0, initial=100000)


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class EmisionForm(forms.Form):
    nombre = forms.CharField(min_length=2, max_length=100,
                             error_messages={'min_length': 'Ingresa el nombre.'})
    username = forms.CharField(max_length=150, validators=[_sin_espacios_ni_arroba])
    email = forms.EmailField(error_messages={'invalid': 'Email inválido.'})
    password = forms.CharField(min_length=6, widget=forms.PasswordInput,
                               error_messages={'min_length': 'La clave debe tener al menos 6 caracteres.'})
    saldo = forms.IntegerField(required=False, min_value=0)
    presupuesto = forms.IntegerField(required=False, min_value=0)
