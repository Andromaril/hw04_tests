from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class PostsURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    args=(self.group.slug,)): 'posts/group_list.html',
            reverse('posts:profile',
                    args=(self.user.username,)):
                        'posts/profile.html',
            reverse('posts:post_detail',
                    args=(self.post.pk,)):
                        'posts/post_detail.html',
            reverse('posts:post_edit',
                    args=(self.post.pk,)):
                        'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""

        response = self.guest_client.get(reverse('posts:index'))

        self.assertEqual(response.context['page_obj'][0].text,
                         'Тестовая группа')
        self.assertEqual(response.context['page_obj'][0].author, self.user)
        self.assertEqual(response.context['page_obj'][0].group, self.group)

    def test_group_list_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""

        response = self.guest_client.get(reverse('posts:group_list',
                                                 args=(self.group.slug,)))

        self.assertEqual(response.context['page_obj'][0].text,
                         'Тестовая группа')
        self.assertEqual(response.context['page_obj'][0].author,
                         self.user)
        self.assertEqual(response.context['page_obj'][0].group,
                         self.group)

        self.assertEqual(response.context['group'].title, 'Тестовая группа')
        self.assertEqual(response.context['group'].slug, 'test-slug')
        self.assertEqual(response.context['group'].description,
                         'Тестовое описание')

    def test_profile_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""

        response = self.guest_client.get(reverse('posts:profile',
                                                 args=(self.user.username,)))

        self.assertEqual(response.context['page_obj'][0].author,
                         self.user)
        self.assertEqual(response.context['page_obj'][0].text,
                         'Тестовая группа')
        self.assertEqual(response.context['page_obj'][0].group, self.group)

        self.assertEqual(response.context['author'].username, 'auth')

        self.assertEqual(response.context['count'], 1)

    def test_post_detail_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""

        response = self.authorized_client.get(reverse('posts:post_detail',
                                                      args=(self.post.pk,)))

        self.assertEqual(response.context.get('post').author, self.user)
        self.assertEqual(response.context.get('post').text, 'Тестовая группа')
        self.assertEqual(response.context.get('post').group, self.group)
        self.assertEqual(response.context.get('count'), 1)

    def test_correct_context_create(self):
        """Шаблон create сформированы с правильным контекстом."""

        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_correct_context_post_edit(self):
        """Шаблон post_edit сформированы с правильным контекстом."""

        response = self.authorized_client.get(reverse('posts:post_edit',
                                                      args=(self.group.pk,)))

        self.assertTrue(response.context.get('is_edit'))
        self.assertEqual(response.context.get('post').text, 'Тестовая группа')
        self.assertEqual(response.context.get('post').author, self.user)
        self.assertEqual(response.context.get('post').group, self.group)

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_appear_index_group_profile(self):
        """После создания поста он появляется
           на главной странице, страницах поста и профайла.
        """

        post_urls = (reverse('posts:index'),
                     reverse('posts:group_list', args=(self.group.slug,)),
                     reverse('posts:profile',
                             args=(self.user.username,)),

                     )

        for post_url in post_urls:
            with self.subTest(post_url=post_url):
                response = self.guest_client.get(post_url)

                self.assertEqual(response.context['page_obj'][0].text,
                                 'Тестовая группа')
                self.assertEqual(response.context['page_obj'][0].author,
                                 self.user)
                self.assertEqual(response.context['page_obj'][0].group,
                                 self.group)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        number_of_posts = 13
        for post in range(number_of_posts):
            cls.post = Post.objects.create(author=cls.user,
                                           text='Тестовая группа',
                                           group=cls.group,
                                           )

    def setUp(self):
        self.guest_client = Client()

    def test_first_page_contains_ten_records(self):
        """Проверка: количество постов на первой странице равно 10.
           Проверка для страниц профайла, группы, главной страницы.
        """

        responses = (reverse('posts:index'),
                     reverse('posts:group_list',
                             args=(self.group.slug,)),
                     reverse('posts:profile',
                             args=(self.user.username,)))

        for adress in responses:
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(len(response.context['page_obj']),
                                 settings.PAGINATOR)

    def test_second_page_contains_three_records(self):
        """Проверка: на второй странице должно быть три поста.
           Проверка для страниц профайла, группы, главной страницы.
        """

        responses = (reverse('posts:index') + '?page=2',
                     reverse('posts:group_list',
                             args=(self.group.slug,)) + '?page=2',
                     reverse('posts:profile',
                             args=(self.user.username,)) + '?page=2',)

        for adress in responses:
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(len(response.context['page_obj']), 3)
