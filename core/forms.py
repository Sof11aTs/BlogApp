from django import forms
from .models import BlogEntry, Comments


class BlogEntryForm(forms.ModelForm):
    class Meta:
        model = BlogEntry
        fields = ["title","category", "content", "image"]
        widgets = {"image": forms.FileInput()}

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comments
        fields = ["content", "stars"]
        widgets = {
            "content": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Add a comment..."}
            ),
            "stars": forms.HiddenInput(),
        }