
from django import forms
from .models import Post, User, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = '__all__'
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }
        exclude = ('author',)


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email")


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text', )
