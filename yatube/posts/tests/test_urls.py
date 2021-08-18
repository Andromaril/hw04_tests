from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
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

        )

    def setUp(self):

        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """Проверка доступа страниц для
           зарегистрированных и анонимных пользователей.
        """

        url = {
            self.guest_client.get('/'): HTTPStatus.OK,
            self.guest_client.get(f'/group/{self.group.slug}/'): HTTPStatus.OK,
            self.guest_client.get(f'/profile/{self.user.username}/'
                                  ): HTTPStatus.OK,
            self.guest_client.get(f'/posts/{self.post.pk}/'): HTTPStatus.OK,
            self.authorized_client.get('/create/'
                                       ): HTTPStatus.OK,
            self.authorized_client.get(f'/posts/{self.post.pk}/edit/'
                                       ): HTTPStatus.OK,
            self.guest_client.get('/unexisting_page/'
                                  ): HTTPStatus.NOT_FOUND,
        }
        for adress, response in url.items():
            with self.subTest(adress=adress):
                self.assertEqual(adress.status_code, response)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',

        }
        for adress, template in url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)
