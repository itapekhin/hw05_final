import time
from mixer.backend.django import mixer
from django import forms
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Comment, Group, Post, User


class viewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()
        cls.authot = User.objects.create_user(username='2')

        cls.group = mixer.cycle(3).blend(
            Group,
            title=mixer.sequence('TestGroup{0}'),
            slug=mixer.sequence('test{0}'),
            description=mixer.sequence('TestGroup{0}')
        )
        cls.post = mixer.cycle(11).blend(
            Post,
            text=mixer.sequence('testus{0}'),
            author=cls.authot,
            group=(Group.objects.get(slug='test0'))
        )
        time.sleep(0.01)
        Post.objects.create(
            author=cls.authot,
            text='Тестовый текст',
            group=cls.group[1]
        )

    def setUp(self):
        self.author = viewsTests.authot
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_posts',
                kwargs={'slug': viewsTests.group[0].slug}
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': viewsTests.authot.username}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail', kwargs={'post_id': viewsTests.post[0].id}
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_about_create_post_correct_template(self):
        response = self.authorized_author.get(
            reverse('posts:post_create')
        )
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_about_post_edit_correct_template(self):
        response = self.authorized_author.get(reverse(
            'posts:post_edit', kwargs={'post_id': viewsTests.post[0].id})
        )
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_index_page_show_correct_context(self):
        response = self.authorized_author.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author
        post_text_0 = first_object.text
        post_group_0 = first_object.group
        self.assertEqual(post_author_0, viewsTests.post[0].author)
        self.assertEqual(post_text_0, Post.objects.all()[0].text)
        self.assertEqual(post_group_0, viewsTests.group[1])

    def test_group_list_page_show_correct_context(self):
        response = self.authorized_author.get(reverse(
            'posts:group_posts',
            kwargs={'slug': viewsTests.group[1].slug})
        )
        group = response.context['group']
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author
        post_text_0 = first_object.text
        self.assertEqual(post_author_0, viewsTests.post[0].author)
        self.assertEqual(post_text_0, Post.objects.all()[0].text)
        self.assertAlmostEqual(group, viewsTests.group[1])

    def test_profile_page_show_correct_context(self):
        response = self.authorized_author.get(reverse(
            'posts:profile',
            kwargs={'username': viewsTests.authot.username})
        )
        author = response.context['author']
        profile_count = response.context['profile_count']
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        self.assertEqual(author, viewsTests.post[0].author)
        self.assertEqual(profile_count, Post.objects.all().count())
        self.assertEqual(post_text_0, Post.objects.all()[0].text)

    def test_post_detail_page_show_correct_context(self):
        response = self.authorized_author.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': viewsTests.post[0].id})
        )
        post = response.context['post']
        post_count = response.context['post_count']
        self.assertEqual(post, viewsTests.post[0])
        self.assertEqual(post_count, Post.objects.all().count())

    def test_post_create_page_type_pole_correct(self):
        response = self.authorized_author.get(
            reverse('posts:post_create')
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        response = self.authorized_author.get(reverse(
            'posts:post_edit',
            args=[1])
        )
        form_field_group = response.context['form'].initial['group']
        form_field_text = response.context['form'].initial['text']
        post = response.context['post']
        post_is_edit = response.context['is_edit']
        self.assertEqual(form_field_group, viewsTests.group[0].id)
        self.assertEqual(form_field_text, viewsTests.post[0].text)
        self.assertEqual(post, viewsTests.post[0])
        self.assertEqual(post_is_edit, True)

    def test_post_creat_page_show_correct_context(self):
        response = self.authorized_author.get(
            reverse('posts:post_create')
        )
        form_field_text = response.context['form']['text'].value()
        form_field_group = response.context['form']['group'].value()
        form_error = response.context['error']
        self.assertEqual(form_error, 'Данные не корректны')
        self.assertEqual(form_field_text, None)
        self.assertEqual(form_field_group, None)

    def test_first_page_index(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_index(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']),
                         Post.objects.all().count() - 10)

    def test_first_page_group_list(self):
        response = self.authorized_author.get(reverse(
            'posts:group_posts',
            kwargs={'slug': viewsTests.group[0].slug})
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_group_list(self):
        response = self.authorized_author.get(reverse(
            'posts:group_posts',
            kwargs={'slug': viewsTests.group[0].slug}) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']),
                         Post.objects.all().count() - 10)

    def test_first_page_group_list(self):
        response = self.authorized_author.get(reverse(
            'posts:profile',
            kwargs={'username': viewsTests.authot.username})
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_group_list(self):
        response = self.authorized_author.get(reverse(
            'posts:profile',
            kwargs={'username': viewsTests.authot.username}) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']),
                         Post.objects.all().count() - 10)

    def test_comment(self):
        comment_count = Comment.objects.count()
        form_data = {
            'text': '123456'
        }
        self.guest_client.post(
            reverse(
                'posts:add_comment', kwargs={'post_id': viewsTests.post[0].id}
            ), form_data, follow=True
        )
        self.assertEqual(Comment.objects.count(), comment_count)
        response = self.authorized_author.post(
            reverse(
                'posts:add_comment', kwargs={'post_id': viewsTests.post[2].id}
            ), form_data, follow=True
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': viewsTests.post[2].id})
        )
        response1 = self.authorized_author.get(
            reverse(
                'posts:post_detail', kwargs={'post_id': viewsTests.post[2].id}
            )
        )
        form_field_text = response1.context['comments'][0].text
        self.assertEqual(form_field_text, form_data['text'])

    def test_index_cash(self):
        cache.clear()
        response = self.client.get(
            reverse('posts:index')
        )
        Post.objects.all().delete()
        response = self.client.get(
            reverse('posts:index')
        )
        self.assertContains(response, viewsTests.post[2].text)
        cache.clear()
        response = self.client.get(
            reverse('posts:index')
        )
        self.assertNotIn(
            response.getvalue().decode('UTF8'),
            viewsTests.post[2].text
        )
