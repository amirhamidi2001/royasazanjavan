import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from articles.models import Category, Tag, Article, Comment
from django.contrib.auth import get_user_model

User = get_user_model()
# fake = Faker("fa_IR")
fake = Faker()


class Command(BaseCommand):
    help = "Seed blog data (categories, tags, articles, comments)"

    def handle(self, *args, **options):
        self.stdout.write("Seeding blog data...")

        author = self.get_author()
        categories = self.create_categories(10)
        tags = self.create_tags(10)
        articles = self.create_articles(100, author, categories, tags)
        self.create_comments(200, articles)

        self.stdout.write(self.style.SUCCESS("Blog data seeded successfully."))

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def get_author(self):
        user, _ = User.objects.get_or_create(
            username="editor",
            defaults={
                "email": "editor@example.com",
                "first_name": "Blog",
                "last_name": "Editor",
            },
        )
        user.set_password("editor123")
        user.save()
        return user

    def create_categories(self, count):
        categories = []
        for _ in range(count):
            category, _ = Category.objects.get_or_create(
                name=fake.unique.word(),
                defaults={
                    "description": fake.sentence(),
                },
            )
            categories.append(category)
        return categories

    def create_tags(self, count):
        tags = []
        for _ in range(count):
            tag, _ = Tag.objects.get_or_create(
                name=fake.unique.word(),
            )
            tags.append(tag)
        return tags

    def create_articles(self, count, author, categories, tags):
        articles = []

        for _ in range(count):
            article = Article.objects.create(
                title=fake.sentence(nb_words=6),
                excerpt=fake.text(max_nb_chars=300),
                content="\n\n".join(fake.paragraphs(nb=5)),
                author=author,
                status="published",
                published_at=timezone.now()
                - timezone.timedelta(days=random.randint(0, 60)),
                view_count=random.randint(0, 2000),
                featured_image="articles/default.webp",
            )

            article.categories.set(random.sample(categories, k=random.randint(1, 3)))
            article.tags.set(random.sample(tags, k=random.randint(0, 4)))

            articles.append(article)

        return articles

    def create_comments(self, count, articles):
        created_comments = []

        for _ in range(count):
            article = random.choice(articles)

            comment = Comment.objects.create(
                article=article,
                name=fake.name(),
                email=fake.email(),
                website=fake.url() if random.random() < 0.3 else "",
                body=fake.paragraph(nb_sentences=3),
                is_approved=random.random() > 0.2,
            )

            created_comments.append(comment)

            if random.random() < 0.25:
                Comment.objects.create(
                    article=article,
                    parent=comment,
                    name=fake.name(),
                    email=fake.email(),
                    body=fake.sentence(),
                    is_approved=True,
                )
