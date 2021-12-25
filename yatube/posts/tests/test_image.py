import random
import shutil
import tempfile
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from mixer.backend.django import mixer
from posts.models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ImageTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        self.authorized_author = Client()
        self.authorized_author.force_login(ImageTests.author)

    def post_create_post(self):
        post_count = Post.objects.count()
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
            'group': ImageTests.group[0].id,
            'image': uploaded
        }
        self.authorized_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        out_post = Post.objects.order_by('-id')[0]
        self.assertTrue(Post.objects.filter(out_post).exists())

    def test_post_create_image_HTML(self):
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
            'text': 'Test123123',
            'group': ImageTests.group[0].id,
            'image': uploaded
        }
        self.authorized_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        response = self.authorized_author.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_image = first_object.image
        self.assertEqual(post_image, 'posts/small.gif')

        id_post = Post.objects.filter(text='Test123123').values()[0]
        response1 = self.authorized_author.get(reverse(
            'posts:post_detail', kwargs={'post_id': id_post["id"]})
        )
        first_object1 = response1.context['post']
        post_image = first_object1.image
        self.assertEqual(post_image, 'posts/small.gif')

        post_slig = Post.objects.filter(text='Test123123').values()[0]
        post_group = Group.objects.filter(id=post_slig["group_id"]).values()[0]
        response2 = self.authorized_author.get(reverse(
            'posts:group_posts',
            kwargs={'slug': post_group["slug"]})
        )
        first_object2 = response2.context['page_obj'][0]
        post_image = first_object2.image
        self.assertEqual(post_image, 'posts/small.gif')

        response3 = self.authorized_author.get(reverse(
            'posts:profile', kwargs={'username': ImageTests.author.username})
        )
        first_object3 = response3.context['page_obj'][0]
        post_image = first_object3.image
        self.assertEqual(post_image, 'posts/small.gif')
