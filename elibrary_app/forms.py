from django import forms
from .models import EBooksModel, UserProfile


class EBooksForm(forms.ModelForm):
    CATEGORY_CHOICES = [
        ('Education', 'Education'),
        ('Fiction', 'Fiction'),
        ('Science', 'Science'),
        # Add more categories as needed
    ]

    category = forms.ChoiceField(choices=CATEGORY_CHOICES)

    class Meta:
        model = EBooksModel
        fields = ['title', 'summary', 'pages', 'pdf', 'category']

    def __init__(self, *args, **kwargs):
        super(EBooksForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter title'})
        self.fields['summary'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter summary'})
        self.fields['pages'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter pages'})
        self.fields['pdf'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter pdf'})
        self.fields['category'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Select category'})

        # Make all fields required
        for field_name, field in self.fields.items():
            field.required = True

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['role', 'phone']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }