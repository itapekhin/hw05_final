from django.db import IntegrityError
from django.test import Client, TestCase
from django.urls import reverse
from mixer.backend.django import mixer
from posts.models import Follow, Group, Post, User


class SubscriptionTests(TestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

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
        cls.post1 = Post.objects.create(
            text='au10',
            author=cls.author1,
            group=(Group.objects.get(slug='test1'))
        )
        cls.post2 = Post.objects.create(
            text='au20',
            author=cls.author2,
            group=(Group.objects.get(slug='test2'))
        )
        Post.objects.create(
            author=cls.author,
            text='Тестовый текст',
            group=cls.group[1]
        )

    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(SubscriptionTests.author)

        self.authorized_author1 = Client()
        self.authorized_author1.force_login(SubscriptionTests.author1)

        self.authorized_author2 = Client()
        self.authorized_author2.force_login(SubscriptionTests.author2)

    def test_subscription_follow_unfollow_author_create_post(self):

        self.authorized_author.get(reverse(
            'posts:profile_follow',
            kwargs={'username': SubscriptionTests.author2})
        )
        self.authorized_author.get(reverse(
            'posts:profile_follow',
            kwargs={'username': SubscriptionTests.author1})
        )
        response = self.authorized_author.get(reverse(
            'posts:follow_index')
        )
        first_object = response.context['page_obj'].object_list[0]
        self.assertEqual(first_object, SubscriptionTests.post1)
        self.authorized_author.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': SubscriptionTests.author2})
        )
        response1 = self.authorized_author.get(reverse(
            'posts:follow_index')
        )
        first_object1 = response1.context['page_obj'].object_list[0]
        self.assertEqual(first_object1, SubscriptionTests.post1)

        d_post = Post.objects.create(
            author=SubscriptionTests.author1,
            text='Дополнительный пост',
            group=SubscriptionTests.group[1]
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

    def test_model_mete_Follow(self):

        with self.assertRaisesMessage(IntegrityError, 'authoe_author'):
            Follow.objects.create(user=self.author, author=self.author)
