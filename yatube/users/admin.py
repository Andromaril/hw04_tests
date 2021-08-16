from django.contrib import admin

from .models import SignUp


class SignUpAdmin(admin.ModelAdmin):
    """Класс для настройки отображения модели в интерфейсе админки."""

    # Перечисляем поля, которые должны отображаться в админке
    list_display = ('pk', 'first_name', 'last_name', 'username', 'email',)
    # Добавляем интерфейс для поиска по тексту постов
    search_fields = ('username',)


admin.site.register(SignUp, SignUpAdmin)
