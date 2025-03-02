from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError  # Add this import
from .models import Product

class ProductModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.product = Product.objects.create(
            name="Laptop",
            quantity=10,
            price=Decimal('999.99')
        )

    def test_product_creation(self):
        """Test if a product can be created."""
        self.assertEqual(self.product.name, "Laptop")
        self.assertEqual(self.product.quantity, 10)
        self.assertEqual(self.product.price, Decimal('999.99'))

    def test_name_max_length(self):
        """Test the max length of the name field."""
        max_length = self.product._meta.get_field('name').max_length
        self.assertEqual(max_length, 255)

    def test_quantity_positive_integer(self):
        """Test that the quantity field only accepts positive integers."""
        with self.assertRaises(IntegrityError):  # Use the imported IntegrityError
            Product.objects.create(
                name="Invalid Quantity",
                quantity=-5,  # Negative quantity should raise an IntegrityError
                price=Decimal('100.00')
            )

    def test_price_decimal_places(self):
        """Test that the price field has correct decimal places."""
        price_field = self.product._meta.get_field('price')
        self.assertEqual(price_field.max_digits, 10)
        self.assertEqual(price_field.decimal_places, 2)


    def test_str_representation(self):
        """Test the __str__ method of the Product model."""
        self.assertEqual(str(self.product), "Laptop")

    def test_created_at_auto_now_add(self):
        """Test that the created_at field is automatically set."""
        self.assertTrue(self.product.created_at <= timezone.now())

    def test_updated_at_auto_now(self):
        """Test that the updated_at field is updated when the object is saved."""
        initial_updated_at = self.product.updated_at
        self.product.name = "Updated Laptop"
        self.product.save()
        self.assertNotEqual(initial_updated_at, self.product.updated_at)
        self.assertTrue(self.product.updated_at > initial_updated_at)