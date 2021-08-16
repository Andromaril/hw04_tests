from django import forms
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

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        # Собираем в словарь пары "reverse(name): имя_html_шаблона"
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': 'test-slug'}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': self.user.username}):
                        'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.pk}):
                        'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.pk}):
                        'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        # Проверяем, что при обращении к
        # name вызывается соответствующий HTML-шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""

        response = self.guest_client.get(reverse('posts:index'))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page_obj'][0]
        index_text_0 = first_object.text
        index_author_0 = first_object.author
        index_group_0 = first_object.group

        self.assertEqual(index_text_0, 'Тестовая группа')
        self.assertEqual(index_author_0, self.user)
        self.assertEqual(index_group_0, self.group)

    def test_group_list_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""

        response = self.guest_client.get(reverse('posts:group_list',
                                         kwargs={'slug': 'test-slug'}))

        first_object_group = response.context['page_obj'][0]
        object_group = response.context['group']

        group_list_text_0 = first_object_group.text
        group_list_author_0 = first_object_group.author
        group_list_group_0 = first_object_group.group

        list_group_title = object_group.title
        list_group_slug = object_group.slug
        list_group_description = object_group.description

        self.assertEqual(group_list_text_0, 'Тестовая группа')
        self.assertEqual(group_list_author_0, self.user)
        self.assertEqual(group_list_group_0, self.group)

        self.assertEqual(list_group_title, 'Тестовая группа')
        self.assertEqual(list_group_slug, 'test-slug')
        self.assertEqual(list_group_description, 'Тестовое описание')

    def test_profile_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""

        response = self.guest_client.get(reverse('posts:profile',
                                         kwargs={'username':
                                                 self.user.username}))

        first_object_profile = response.context['page_obj'][0]
        object_profile_author = response.context['author']
        object_profile_count = response.context['count']

        profile_list_author_0 = first_object_profile.author
        profile_list_text_0 = first_object_profile.text
        profile_list_group_0 = first_object_profile.group

        profile_author = object_profile_author.username

        self.assertEqual(profile_list_author_0, self.user)
        self.assertEqual(profile_list_text_0, 'Тестовая группа')
        self.assertEqual(profile_list_group_0, self.group)

        self.assertEqual(profile_author, 'auth')

        self.assertEqual(object_profile_count, 1)

    def test_post_detail_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""

        response = self.authorized_client.get(reverse('posts:post_detail',
                                              kwargs={'post_id':
                                                      self.post.pk}))

        self.assertEqual(response.context.get('post').author, self.user)
        self.assertEqual(response.context.get('post').text, 'Тестовая группа')
        self.assertEqual(response.context.get('post').group, self.group)
        self.assertEqual(response.context.get('count'), 1)

    def test_post_edit_and_create_correct_context(self):
        """Шаблон create сформированы с правильным контекстом."""

        response2 = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field2 = response2.context.get('form').fields.get(value)
                self.assertIsInstance(form_field2, expected)

    def test_post_edit_and_create_correct_context(self):
        """Шаблон post_edit сформированы с правильным контекстом."""

        response1 = self.authorized_client.get(reverse('posts:post_edit',
                                               kwargs={'post_id':
                                                       self.post.pk}))

        self.assertTrue(response1.context.get('is_edit'))
        self.assertEqual(response1.context.get('post').text, 'Тестовая группа')
        self.assertEqual(response1.context.get('post').author, self.user)
        self.assertEqual(response1.context.get('post').group, self.group)

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field1 = response1.context.get('form').fields.get(value)
                self.assertIsInstance(form_field1, expected)

    def test_post_appear_index_group_profile(self):
        """После создания поста он появляется
           на главной странице, страницах поста и профайла.
        """

        post_urls = (reverse('posts:index'),
                     reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
                     reverse('posts:profile',
                             kwargs={'username': self.user.username}),

                     )

        for post_url in post_urls:
            with self.subTest(post_url=post_url):
                response = self.guest_client.get(post_url)
                first_object = response.context['page_obj'][0]

                text_0 = first_object.text
                author_0 = first_object.author
                group_0 = first_object.group

                self.assertEqual(text_0, 'Тестовая группа')
                self.assertEqual(author_0, self.user)
                self.assertEqual(group_0, self.group)


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
        """Проверка: количество постов на первой странице равно 10."""

        response_index = self.guest_client.get(reverse('posts:index'))
        response_group_list = self.guest_client.get(reverse('posts:group_list',
                                                    kwargs={'slug':
                                                            'test-slug'}))
        response_profile = self.guest_client.get(reverse('posts:profile',
                                                 kwargs={'username':
                                                         self.user.username}))

        self.assertEqual(len(response_index.context['page_obj']), 10)
        self.assertEqual(len(response_group_list.context['page_obj']), 10)
        self.assertEqual(len(response_profile.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        """Проверка: на второй странице должно быть три поста."""

        response1 = self.guest_client.get(reverse('posts:index') + '?page=2')
        response2 = self.guest_client.get(reverse('posts:group_list',
                                                  kwargs={'slug':
                                                          'test-slug'})
                                          + '?page=2'
                                          )
        response3 = self.guest_client.get(reverse('posts:profile',
                                                  kwargs={'username':
                                                          self.user.username})
                                          + '?page=2')

        self.assertEqual(len(response1.context['page_obj']), 3)
        self.assertEqual(len(response2.context['page_obj']), 3)
        self.assertEqual(len(response3.context['page_obj']), 3)
