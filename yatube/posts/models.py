from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="Имя группы"
    )
    slug = models.SlugField(
        unique=True,
        verbose_name="Адрес Slug"
    )
    description = models.TextField(verbose_name="Описание")

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name="Содержание статьи",
        help_text="Введите текст статьи"
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации статьи"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name="Автор",
        help_text="Введите автора статьи"
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name="Группа"
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:30]


class Comments(models.Model):
    post = models.ForeignKey(Post,
			     on_delete=models.CASCADE,  
			     related_name='comments',
                 blank=True,
                 null=True,) 
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        )
    text = models.CharField(max_length=200)  
    created = models.DateTimeField(auto_now_add=True)  
      
    class Meta:  
        ordering = ('created',)  
          
    def __str__(self):
        return 'Comment by {} on {}'.format(self.text, self.post)

class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
        )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
        )
    def __str__(self):
        return f'Подписчик {self.user}, Автор {self.author}'
    
