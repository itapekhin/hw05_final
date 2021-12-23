import shutil
import tempfile
import random
import time
from django.test import TestCase, Client, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from posts.models import Post, Group, User
from django.urls import reverse
from django.conf import settings
from mixer.backend.django import mixer

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)


class ImageTests(TestCase):
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.author = ImageTests.author
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

    def test_create_post(self):
        tasks_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Test',
            'group': '1',
            'image': uploaded
        }
        self.authorized_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), tasks_count + 1)
        self.assertTrue(Post.objects.filter(
            text='Test',
            group='1',
            image='posts/small.gif'
        ).exists())
        templates_pages_names = {
            'posts/small.gif': reverse('posts:index'),
            'posts/small.gif': reverse(
                'posts:group_posts',
                kwargs={'slug': '1'}
            ),
            'posts/small.gif': reverse(
                'posts:profile', kwargs={'username': '2'}
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_author.get(reverse_name)
                first_object1 = response.context['page_obj'][0]
                post_image1 = first_object1.image
                self.assertEqual(post_image1, template)
        response1 = self.authorized_author.get(reverse(
                'posts:post_detail', kwargs={'post_id': '13'})
        )
        first_object1 = response1.context['post']
        post_image = first_object1.image
        self.assertEqual(post_image, 'posts/small.gif')
