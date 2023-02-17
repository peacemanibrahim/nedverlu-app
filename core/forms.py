from django import forms


class CheckoutForm(forms.Form):
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Enter your preferred shipping email address',
        'class': 'form-control'
    }))

    phone_no = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Enter your phone number',
        'class': 'form-control'
    }))

class ContactForm(forms.Form):
    from_email = forms.EmailField(required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Email',
        'class': 'form-control'
    }))
    subject = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'placeholder': 'Subject',
        'class': 'form-control'
    }))
    message = forms.CharField(required=True, widget=forms.Textarea(attrs={
        'placeholder': 'Message',
        'class': 'form-control'
    }))
