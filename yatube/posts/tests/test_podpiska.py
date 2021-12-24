from django.test import TestCase, Client
from posts.models import Post, Group, User, Comments
from django.urls import reverse
from django import forms
import time
from mixer.backend.django import mixer
from django.core.cache import cache


class podpiskaTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()
        cls.author = User.objects.create_user(username='0')
        cls.author1 = User.objects.create_user(username='1')
        cls.author2 = User.objects.create_user(username='2')


        cls.group = mixer.cycle(3).blend(
            Group,
            title=mixer.sequence('TestGroup{0}'),
            slug=mixer.sequence('test{0}'),
            description=mixer.sequence('TestGroup{0}')
        )
        cls.post = Post.objects.create(
            text='au',
            author=cls.author,
            group=(Group.objects.get(slug='test0'))
        )
        time.sleep(0.01)
        cls.post1 = Post.objects.create(
            text='au10',
            author=cls.author1,
            group=(Group.objects.get(slug='test1'))
        )
        time.sleep(0.01)
        cls.post2 = Post.objects.create(
            text='au20',
            author=cls.author2,
            group=(Group.objects.get(slug='test2'))
        )
        time.sleep(0.01)
        Post.objects.create(
            author=cls.author,
            text='Тестовый текст',
            group=cls.group[1]
        )
    def setUp(self):
        self.author = podpiskaTests.author
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

        self.author1 = podpiskaTests.author1
        self.authorized_author1 = Client()
        self.authorized_author1.force_login(self.author1)

        self.author2 = podpiskaTests.author2
        self.authorized_author2 = Client()
        self.authorized_author2.force_login(self.author2)
    
    def test_podpiska(self):
        self.authorized_author.get(reverse(
            'posts:profile_follow', kwargs={'username': podpiskaTests.author2})
        )
        self.authorized_author.get(reverse(
            'posts:profile_follow', kwargs={'username': podpiskaTests.author1})
        )
        response = self.authorized_author.get(reverse(
            'posts:follow_index')
        )
        first_object = response.context['page_obj'].object_list[0]
        self.assertEqual(first_object, podpiskaTests.post2)
        self.authorized_author.get(reverse(
            'posts:profile_unfollow', kwargs={'username': podpiskaTests.author2})
        )
        response1 = self.authorized_author.get(reverse(
            'posts:follow_index')
        )
        first_object1 = response1.context['page_obj'].object_list[0]
        self.assertEqual(first_object1, podpiskaTests.post1)

        d_post = Post.objects.create(
            author=podpiskaTests.author1,
            text='Дополнительный пост',
            group=podpiskaTests.group[1]
        )
        response2 = self.authorized_author.get(reverse(
            'posts:follow_index')
        )
        first_object2 = response2.context['page_obj'].object_list[0]
        self.assertEqual(first_object2, d_post)
        response3 = self.authorized_author2.get(reverse(
            'posts:follow_index')
        )
        first_object3 = response3.context['page_obj'].object_list
        self.assertNotIn(d_post, first_object3)


