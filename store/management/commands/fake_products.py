from django.core.management.base import BaseCommand
from store.models import Product, Category
from faker import Faker
import random
from decimal import Decimal

fake = Faker()

class Command(BaseCommand):
    help = 'Generate fake products'

    def add_arguments(self, parser):
        parser.add_argument('total', type=int, help='Number of products to create')

    def handle(self, *args, **kwargs):
        total = kwargs['total']

        # Ensure categories exist
        categories = ['Electronics', 'Books', 'Clothing', 'Toys']
        category_objs = []

        for name in categories:
            cat, _ = Category.objects.get_or_create(name=name)
            category_objs.append(cat)

        for _ in range(total):
            name = fake.unique.word().capitalize() + " " + fake.word().capitalize()
            price = Decimal(random.randint(100, 10000))
            category = random.choice(category_objs)
            
            Product.objects.create(
                name=name,
                price=price,
                category=category
            )

        self.stdout.write(self.style.SUCCESS(f'Successfully added {total} fake products.'))
