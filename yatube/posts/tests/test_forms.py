from posts.models import Post, Group, User
from django.test import Client, TestCase
from django.urls import reverse
from mixer.backend.django import mixer
import random


class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = User.objects.create_user(username='1')
        cls.guest_client = Client()
        cls.author = User.objects.create_user(username='2')

        cls.group = mixer.cycle(3).blend(
            Group,
            title=mixer.sequence('Test Group {0}'),
            slug=mixer.sequence('test{0}'),
            description=mixer.sequence('Test Group {0}')
        )
        cls.post = mixer.cycle(12).blend(
            Post,
            text=mixer.sequence('Тестовый текст {0}'),
            author=cls.author,
            group=(Group.objects.get(slug=f'test{random.randrange(0, 1, 2)}'))
        )

    def setUp(self):
        self.author = TaskCreateFormTests.author
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

    def test_create_post(self):
        tasks_count = Post.objects.count()
        form_data = {
            'text': 'Test',
            'group': TaskCreateFormTests.group[0].id}
        self.authorized_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), tasks_count + 1)
        self.assertTrue(Post.objects.filter(
            text='Test',
            group=TaskCreateFormTests.group[0].id
        ).exists())

    def test_post_edit(self):
        form_data = {
            'text': 'Test',
            'group': TaskCreateFormTests.group[0].id}
        self.authorized_author.post(
            reverse('posts:post_edit', args=[1]),
            data=form_data,
            follow=True
        )
        self.assertTrue(Post.objects.filter(
            text='Test',
            group=TaskCreateFormTests.group[0].id
        ).exists())
