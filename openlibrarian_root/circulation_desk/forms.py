from django import forms

class SeedForm(forms.Form):
    word1 = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'aria-describedby': 'inputGroup-sizing-sm', 'list': 'word-list'}))
    word2 = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'aria-describedby': 'inputGroup-sizing-sm', 'list': 'word-list'}))
    word3 = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'aria-describedby': 'inputGroup-sizing-sm', 'list': 'word-list'}))
    word4 = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'aria-describedby': 'inputGroup-sizing-sm', 'list': 'word-list'}))
    word5 = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'aria-describedby': 'inputGroup-sizing-sm', 'list': 'word-list'}))
    word6 = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'aria-describedby': 'inputGroup-sizing-sm', 'list': 'word-list'}))
    word7 = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'aria-describedby': 'inputGroup-sizing-sm', 'list': 'word-list'}))
    word8 = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'aria-describedby': 'inputGroup-sizing-sm', 'list': 'word-list'}))
    word9 = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'aria-describedby': 'inputGroup-sizing-sm', 'list': 'word-list'}))
    word10 = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'aria-describedby': 'inputGroup-sizing-sm', 'list': 'word-list'}))
    word11 = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'aria-describedby': 'inputGroup-sizing-sm', 'list': 'word-list'}))
    word12 = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'aria-describedby': 'inputGroup-sizing-sm', 'list': 'word-list'}))

# Create LoginForm which is an extension of SeedForm but with the additional fields NPUB and NSEC where NSEC is a password field

class npubForm(forms.Form):
    npub = forms.CharField(max_length=100, label='', required=True, widget=forms.TextInput(attrs={'placeholder': 'npub......', 'class': 'form-control', 'aria-describedby': 'inputGroup-sizing-sm'}))
    
class nsecForm(forms.Form):
    nsec = forms.CharField(max_length=100, label='', required=True, widget=forms.PasswordInput(attrs={'placeholder': 'nsec......', 'autocomplete': 'off', 'class': 'form-control', 'aria-describedby': 'inputGroup-sizing-sm'}, render_value=True))