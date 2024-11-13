from django import forms

class SeedForm(forms.Form):
    word1 = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'id':'word1', 'class': 'form-control', 'aria-describedby': 'inputGroup-sizing-sm', 'list': 'word-list'}))
    word2 = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'id':'word2', 'class': 'form-control', 'aria-describedby': 'inputGroup-sizing-sm', 'list': 'word-list'}))
    word3 = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'id':'word3', 'class': 'form-control', 'aria-describedby': 'inputGroup-sizing-sm', 'list': 'word-list'}))
    word4 = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'id':'word4', 'class': 'form-control', 'aria-describedby': 'inputGroup-sizing-sm', 'list': 'word-list'}))
    word5 = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'id':'word5', 'class': 'form-control', 'aria-describedby': 'inputGroup-sizing-sm', 'list': 'word-list'}))
    word6 = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'id':'word6', 'class': 'form-control', 'aria-describedby': 'inputGroup-sizing-sm', 'list': 'word-list'}))
    word7 = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'id':'word7', 'class': 'form-control', 'aria-describedby': 'inputGroup-sizing-sm', 'list': 'word-list'}))
    word8 = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'id':'word8', 'class': 'form-control', 'aria-describedby': 'inputGroup-sizing-sm', 'list': 'word-list'}))
    word9 = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'id':'word9', 'class': 'form-control', 'aria-describedby': 'inputGroup-sizing-sm', 'list': 'word-list'}))
    word10 = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'id':'word10', 'class': 'form-control', 'aria-describedby': 'inputGroup-sizing-sm', 'list': 'word-list'}))
    word11 = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'id':'word11', 'class': 'form-control', 'aria-describedby': 'inputGroup-sizing-sm', 'list': 'word-list'}))
    word12 = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'id':'word12', 'class': 'form-control', 'aria-describedby': 'inputGroup-sizing-sm', 'list': 'word-list'}))

class npubForm(forms.Form):
    npub = forms.CharField(max_length=100, label='', required=True, widget=forms.TextInput(attrs={'id':'npub', 'placeholder': 'npub......', 'class': 'form-control', 'aria-describedby': 'inputGroup-sizing-sm'}))
    
class nsecForm(forms.Form):
    nsec = forms.CharField(max_length=100, label='', required=True, widget=forms.PasswordInput(attrs={'id':'nsec', 'placeholder': 'nsec......', 'autocomplete': 'off', 'class': 'form-control', 'aria-describedby': 'inputGroup-sizing-sm'}, render_value=True))