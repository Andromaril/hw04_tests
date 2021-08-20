from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post

User = get_user_model()


class TaskCreateFormTests(TestCase):
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
            text='Тест текст',
            group=cls.group,
        )
        cls.form = PostForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_form_create(self):
        """Проверка создания поста в базе данных."""

        form_data = {
            'text': 'Тест текст',
            'group': self.group.pk,

        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        self.assertEqual(response.context.get('page_obj')[1].text,
                         form_data.get('text'))
        self.assertEqual(response.context.get('page_obj')[1].group, self.group)

        self.assertEqual(Post.objects.count(), 2)
        self.assertRedirects(
            response, reverse('posts:profile',
                              args=(self.user.username,)))

    def test_form_edit(self):
        """Проверка изменения записи в базе данных."""

        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тест',
            'group': self.group.pk,

        }

        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    args=(self.post.pk,)),
            data=form_data,
            follow=True
        )

        self.assertEqual(response.context.get('post').text,
                         form_data.get('text'))
        self.assertEqual(response.context.get('post').group, self.group)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertRedirects(
            response, reverse('posts:post_detail',
                              args=(self.post.pk,))
        )
