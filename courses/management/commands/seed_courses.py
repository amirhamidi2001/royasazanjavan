from django.core.management.base import BaseCommand
from accounts.models import User
from courses.models import Course, Video
from django.utils.text import slugify


class Command(BaseCommand):
    help = "Seed database with sample courses and videos"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Starting to seed courses..."))

        # Create an instructor user if doesn't exist
        instructor, created = User.objects.get_or_create(
            email="instructor@example.com",
            defaults={"is_active": True, "is_verified": True},
        )
        if created:
            instructor.set_password("instructor123")
            instructor.save()
            self.stdout.write(
                self.style.SUCCESS("✓ Created instructor user (instructor@example.com)")
            )
        else:
            self.stdout.write(self.style.WARNING("→ Instructor user already exists"))

        # Create sample courses with videos
        courses_data = [
            {
                "title": "Django Web Development Masterclass",
                "description": "Learn Django from scratch and build powerful web applications. This comprehensive course covers everything from basic concepts to advanced features like REST APIs, authentication, and deployment.",
                "duration": 25,
                "price": 49.99,
                "videos": [
                    {
                        "title": "Introduction to Django Framework",
                        "description": "Overview of Django and its architecture",
                        "duration": 30,
                    },
                    {
                        "title": "Setting Up Your Development Environment",
                        "description": "Install Python, Django, and configure your IDE",
                        "duration": 25,
                    },
                    {
                        "title": "Django Models and Databases",
                        "description": "Learn about ORM, models, and database relationships",
                        "duration": 45,
                    },
                    {
                        "title": "Django Views and URL Routing",
                        "description": "Understanding function-based and class-based views",
                        "duration": 40,
                    },
                    {
                        "title": "Django Templates and Static Files",
                        "description": "Creating dynamic templates with Django template language",
                        "duration": 35,
                    },
                ],
            },
            {
                "title": "Python Programming from Zero to Hero",
                "description": "Master Python programming from fundamentals to advanced topics. Perfect for beginners who want to learn programming or experienced developers wanting to add Python to their skillset.",
                "duration": 18,
                "price": 39.99,
                "videos": [
                    {
                        "title": "Python Installation and Setup",
                        "description": "Get Python installed on your system",
                        "duration": 20,
                    },
                    {
                        "title": "Python Syntax and Basic Concepts",
                        "description": "Learn variables, data types, and basic operations",
                        "duration": 35,
                    },
                    {
                        "title": "Control Flow: If Statements and Loops",
                        "description": "Master conditional logic and iteration",
                        "duration": 40,
                    },
                    {
                        "title": "Functions and Modules",
                        "description": "Write reusable code with functions",
                        "duration": 30,
                    },
                ],
            },
            {
                "title": "JavaScript ES6+ Modern Development",
                "description": "Deep dive into modern JavaScript including ES6+ features, async programming, and best practices. Learn to write clean, efficient JavaScript code.",
                "duration": 22,
                "price": 44.99,
                "videos": [
                    {
                        "title": "JavaScript Fundamentals Review",
                        "description": "Quick review of JavaScript basics",
                        "duration": 25,
                    },
                    {
                        "title": "ES6 Features: Let, Const, Arrow Functions",
                        "description": "Modern JavaScript syntax and features",
                        "duration": 35,
                    },
                    {
                        "title": "Promises and Async/Await",
                        "description": "Mastering asynchronous JavaScript",
                        "duration": 45,
                    },
                    {
                        "title": "Modules and Import/Export",
                        "description": "Organizing your JavaScript code",
                        "duration": 30,
                    },
                ],
            },
            {
                "title": "React.js Complete Guide",
                "description": "Build modern, reactive user interfaces with React. Learn components, hooks, state management, and how to create production-ready React applications.",
                "duration": 30,
                "price": 59.99,
                "videos": [
                    {
                        "title": "Introduction to React",
                        "description": "What is React and why use it?",
                        "duration": 25,
                    },
                    {
                        "title": "JSX and Components",
                        "description": "Building blocks of React applications",
                        "duration": 40,
                    },
                    {
                        "title": "React Hooks: useState and useEffect",
                        "description": "Managing state and side effects",
                        "duration": 50,
                    },
                    {
                        "title": "Props and Component Communication",
                        "description": "Passing data between components",
                        "duration": 35,
                    },
                    {
                        "title": "React Router and Navigation",
                        "description": "Building multi-page React apps",
                        "duration": 40,
                    },
                ],
            },
            {
                "title": "Database Design and SQL Fundamentals",
                "description": "Learn database design principles and master SQL. Understand normalization, relationships, and write efficient queries for real-world applications.",
                "duration": 20,
                "price": 42.99,
                "videos": [
                    {
                        "title": "Introduction to Databases",
                        "description": "Database concepts and types",
                        "duration": 30,
                    },
                    {
                        "title": "SQL Basics: SELECT, INSERT, UPDATE, DELETE",
                        "description": "Essential SQL commands",
                        "duration": 45,
                    },
                    {
                        "title": "Database Relationships and Joins",
                        "description": "Connecting tables with foreign keys",
                        "duration": 50,
                    },
                    {
                        "title": "Database Normalization",
                        "description": "Designing efficient database schemas",
                        "duration": 40,
                    },
                ],
            },
        ]

        # Create courses and videos
        courses_created = 0
        videos_created = 0

        for course_data in courses_data:
            videos_data = course_data.pop("videos")

            course, created = Course.objects.get_or_create(
                slug=slugify(course_data["title"]),
                defaults={
                    **course_data,
                    "instructor": instructor,
                    "is_active": True,
                },
            )

            if created:
                courses_created += 1
                # Create videos for this course
                for i, video_data in enumerate(videos_data, 1):
                    Video.objects.create(
                        course=course,
                        title=video_data["title"],
                        description=video_data.get("description", ""),
                        video_link="https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Sample link
                        duration=video_data["duration"],
                        display_order=i,
                    )
                    videos_created += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Created course: {course.title} with {len(videos_data)} videos"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"→ Course already exists: {course.title}")
                )

        # Summary
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("Seeding completed!"))
        self.stdout.write(self.style.SUCCESS(f"Created {courses_created} courses"))
        self.stdout.write(self.style.SUCCESS(f"Created {videos_created} videos"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write("")
        self.stdout.write("You can now:")
        self.stdout.write("  • Visit http://localhost:8000/courses/ to see all courses")
        self.stdout.write(
            "  • Login as instructor@example.com (password: instructor123)"
        )
        self.stdout.write("  • Access admin panel to manage courses")
