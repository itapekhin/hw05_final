from django.test import TestCase

from posts.models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
            group=cls.group
        )

    def test_verbose_name(self):
        task = PostModelTest.post
        field_verboses = {
            'author': 'Автор',
            'text': 'Содержание статьи',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    task._meta.get_field(field).verbose_name, expected_value)

    def test_help_text(self):
        task = PostModelTest.post
        field_help_texts = {
            'author': 'Введите автора статьи',
            'text': 'Введите текст статьи',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    task._meta.get_field(field).help_text, expected_value)

    def test_models_have_correct_object_names(self):
        post = PostModelTest.post
        field_verboses = {
            'title': 'Тестовая группа',
            'text': 'Тестовая группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    expected_value[:15], str(post)[:15])
