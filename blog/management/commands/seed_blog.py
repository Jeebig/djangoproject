from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from blog.models import Category, Tag, Post

User = get_user_model()

class Command(BaseCommand):
    help = "Seed initial categories, tags, and posts for the blog"

    def handle(self, *args, **options):
        # Ensure at least one user exists
        user = User.objects.first()
        if not user:
            self.stderr.write(self.style.ERROR('No users found. Please create a superuser first: python manage.py createsuperuser'))
            return

        # Repair any existing categories with empty slugs (from previous ascii-only slugify)
        empty_slug_cats = Category.objects.filter(slug="")
        for cat in empty_slug_cats:
            cat.slug = ""  # force regeneration logic in save
            cat.save()
            self.stdout.write(self.style.WARNING(f"Оновлено порожній slug для категорії: {cat.name}"))

        categories = [
            ("Програмування", "Категорія про код, мови програмування та фреймворки"),
            ("Подорожі", "Записи про подорожі та враження"),
            ("Мистецтво", "Статті про мистецтво та креативність"),
        ]
        created_categories = []
        for name, _desc in categories:
            # We attempt lookup by name first
            cat = Category.objects.filter(name=name).first()
            if not cat:
                cat = Category(name=name)  # slug will be auto-generated with unicode allowed
                cat.save()
                self.stdout.write(self.style.SUCCESS(f"Створено категорію: {name}"))
            else:
                if not cat.slug:
                    # Regenerate slug if still blank
                    cat.slug = ""
                    cat.save()
                    self.stdout.write(self.style.WARNING(f"Додано slug для існуючої категорії: {name}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Пропущено (категорія існує): {name}"))
            created_categories.append(cat)

        tags_list = ["python", "django", "web", "travel", "design", "art", "javascript", "css", "photography", "nature", "programming", "tutorial", "backend", "frontend", "security", "database", "api", "mobile", "ui", "ux"]
        created_tags = []
        for tag_name in tags_list:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            created_tags.append(tag)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Створено тег: {tag_name}"))

        sample_posts = [
            {
                "title": "Перший пост про Django",
                "content": "Це демонстраційний пост про те, як працює Django та його структура проекту. Django - це потужний веб-фреймворк для Python, який дозволяє швидко створювати складні веб-додатки.",
                "category": created_categories[0],
                "tags": ["python", "django", "web"],
                "image": "https://picsum.photos/seed/django/800/400"
            },
            {
                "title": "Надихаюча подорож у гори",
                "content": "Опис пригод та вражень від нещодавньої подорожі у Карпати. Гори завжди дарують неймовірні емоції та спогади на все життя.",
                "category": created_categories[1],
                "tags": ["travel", "nature", "photography"],
                "image": "https://picsum.photos/seed/travel/800/400"
            },
            {
                "title": "Креативність у цифровому дизайні",
                "content": "Роздуми про роль креативності у сучасному веб-дизайні. UI/UX дизайн стає все більш важливим у розробці веб-додатків.",
                "category": created_categories[2],
                "tags": ["design", "art", "web", "ui", "ux"],
                "image": "https://picsum.photos/seed/design/800/400"
            },
            {
                "title": "Основи JavaScript для початківців",
                "content": "Вивчення JavaScript - це перший крок у світ фронтенд розробки. У цій статті розглянемо основні концепції мови.",
                "category": created_categories[0],
                "tags": ["javascript", "frontend", "web", "tutorial"],
                "image": "https://picsum.photos/seed/javascript/800/400"
            },
            {
                "title": "Безпека веб-додатків",
                "content": "Огляд основних принципів безпеки у веб-розробці. HTTPS, CSP, CORS та інші важливі аспекти захисту додатків.",
                "category": created_categories[0],
                "tags": ["security", "web", "backend", "programming"],
                "image": "https://picsum.photos/seed/security/800/400"
            },
            {
                "title": "Подорож Європою на автомобілі",
                "content": "Захоплююча історія про подорож автомобілем через країни Європи. Поради щодо планування маршруту та корисні лайфхаки.",
                "category": created_categories[1],
                "tags": ["travel", "photography"],
                "image": "https://picsum.photos/seed/europe/800/400"
            },
            {
                "title": "Сучасні тренди у веб-дизайні",
                "content": "Аналіз останніх трендів у веб-дизайні 2025 року. Мінімалізм, градієнти, анімації та мікроінтеракції.",
                "category": created_categories[2],
                "tags": ["design", "web", "ui", "css"],
                "image": "https://picsum.photos/seed/webdesign/800/400"
            },
            {
                "title": "API розробка з Django REST Framework",
                "content": "Повний гайд по створенню RESTful API за допомогою Django REST Framework. Серіалізатори, вью та аутентифікація.",
                "category": created_categories[0],
                "tags": ["python", "django", "api", "backend"],
                "image": "https://picsum.photos/seed/api/800/400"
            },
            {
                "title": "Фотографія в подорожах",
                "content": "Секрети створення вражаючих фотографій під час подорожей. Композиція, освітлення та обробка знімків.",
                "category": created_categories[1],
                "tags": ["photography", "travel", "art"],
                "image": "https://picsum.photos/seed/photo/800/400"
            },
            {
                "title": "Мобільна розробка з React Native",
                "content": "Введення у розробку мобільних додатків за допомогою React Native. Cross-platform розробка стає все популярнішою.",
                "category": created_categories[0],
                "tags": ["mobile", "javascript", "programming"],
                "image": "https://picsum.photos/seed/mobile/800/400"
            },
            {
                "title": "База даних PostgreSQL у продакшені",
                "content": "Налаштування та оптимізація PostgreSQL для продакшн середовища. Індекси, репліки та моніторинг.",
                "category": created_categories[0],
                "tags": ["database", "backend", "programming"],
                "image": "https://picsum.photos/seed/database/800/400"
            },
            {
                "title": "Відпочинок на морському узбережжі",
                "content": "Розповідь про незабутній відпочинок на Чорному морі. Кращі пляжі, місцева кухня та культурні пам'ятки.",
                "category": created_categories[1],
                "tags": ["travel", "nature"],
                "image": "https://picsum.photos/seed/sea/800/400"
            }
        ]

        for data in sample_posts:
            post = Post.objects.filter(title=data["title"]).first()
            if not post:
                post = Post(
                    title=data["title"],
                    content=data["content"],
                    category=data["category"],
                    author=user,
                    image=data["image"],
                )
                post.save()
                post.tags.set(Tag.objects.filter(name__in=data["tags"]))
                self.stdout.write(self.style.SUCCESS(f"Створено пост: {post.title}"))
            else:
                # Ensure it has tags synchronised (add missing ones, keep existing)
                existing_tag_names = set(post.tags.values_list("name", flat=True))
                desired_tag_names = set(data["tags"])
                if not desired_tag_names.issubset(existing_tag_names):
                    post.tags.add(*Tag.objects.filter(name__in=(desired_tag_names - existing_tag_names)))
                    self.stdout.write(self.style.WARNING(f"Оновлено теги поста: {post.title}"))
                self.stdout.write(self.style.WARNING(f"Пропущено (вже існує): {post.title}"))

        self.stdout.write(self.style.SUCCESS("Готово! Дані для блогу додано."))
