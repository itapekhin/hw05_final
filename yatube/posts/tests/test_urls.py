from django.test import Client, TestCase

from posts.models import Group, Post, User


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='1')
        cls.author = User.objects.create_user(username='2')

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый текст',
            group=cls.group,
        )
        cls.url_name = {
            '/': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.user.username}/': 'posts/profile.html',
            f'/posts/{cls.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{cls.post.pk}/edit/': 'posts/create_post.html',
        }

    def setUp(self):
        self.user = StaticURLTests.user
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)
        self.author = StaticURLTests.author
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

    def test_homepage(self):
        response = StaticURLTests.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200)

    def test_tech(self):
        response = StaticURLTests.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)

    def test_index(self):
        response = StaticURLTests.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group_list(self):
        response = StaticURLTests.guest_client.get(
            f'/group/{StaticURLTests.group.slug}/'
        )
        self.assertEqual(response.status_code, 200)

    def test_profile_author(self):
        response = StaticURLTests.guest_client.get(
            f'/profile/{self.author.username}/'
        )
        self.assertEqual(response.status_code, 200)

    def test_post_id(self):
        response = StaticURLTests.guest_client.get(
            f'/posts/{StaticURLTests.post.id}/'
        )
        self.assertEqual(response.status_code, 200)

    def test_post_create_auth(self):
        response = self.authorized_user.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_post_edit_author(self):
        response = self.authorized_author.get(
            f'/posts/{StaticURLTests.post.pk}/edit/'
        )
        self.assertEqual(response.status_code, 200)

    def test_post_edit_auth(self):
        response = self.authorized_user.get(
            f'/posts/{StaticURLTests.post.pk}/edit/',
            follow=True
        )
        self.assertRedirects(
            response, f'/posts/{StaticURLTests.post.id}/'
        )

    def test_unexisting_page(self):
        response = StaticURLTests.guest_client.get('/unexisting_page')
        self.assertEqual(response.status_code, 404)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for address, url in self.url_name.items():
            with self.subTest(address=address, follow=True):
                response = self.authorized_author.get(
                    address,
                    follow=True
                )
                self.assertTemplateUsed(response, url)
