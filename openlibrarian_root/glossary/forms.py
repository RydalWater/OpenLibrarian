from django import forms

class SearchForm(forms.Form):
    """Search Form for Glossary"""
    # Main Search field
    search_field = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search...',
            'class': 'form-control',
            'aria-describedby': 'inputGroup-sizing-sm'
            })
    )

    # Search Type
    search_type = forms.ChoiceField(
        choices= [
            ('general', 'General'),            
            ('author', 'Author'),
            ('title', 'Title'),
            ('isbn', 'ISBN'),
        ],
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-sm',
            'id': 'search_type'
            })
    )

    # Sort Type
    sort_type = forms.ChoiceField(
        choices= [
            ('rating desc', 'Rating Descending'),
            ('rating asc', 'Rating Ascending'),
            ('new', 'Newest'),
            ('old', 'Oldest'),
            ('title', 'Title'),
            ('random', 'Random'),
        ],
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-sm',
            })
    )