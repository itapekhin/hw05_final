from django.forms import ModelForm, Select, Textarea

from posts.models import Comment, Post


class PostForm(ModelForm):

    class Meta:
        model = Post
        labels = {
            'text': 'Текст поста',
            'group': 'Group'
        }
        help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа к которой относится пост',
        }
        fields = ['text', 'group', 'image']
        widgets = {
            'text': Textarea(attrs={
                'name': 'text',
                'cols': '40',
                'rows': '10',
                'class': 'form-control',
                'id': 'id_text'
            }),
            'group': Select(attrs={
                'name': 'group',
                'class': 'form-control',
                'id': 'id_group'
            }),
        }


class CommentForm(ModelForm):

    class Meta:
        model = Comment
        labels = {
            'text': 'Текст комментария',
        }
        help_texts = {
            'text': 'Текст нового комментария',
        }
        fields = ['text']
        widgets = {
            'text': Textarea(attrs={
                'name': 'text',
                'cols': '40',
                'rows': '10',
                'class': 'form-control',
                'id': 'id_text'
            })
        }
