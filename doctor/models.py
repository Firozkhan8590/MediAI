from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class DoctorManager(models.Manager):
    def create_professional(self, name, email, contact_number, license_number, experience_years, image, specialization, password, **extra_fields):
        professional = self.model(
            name=name,
            email=email,
            contact_number=contact_number,
            license_number=license_number,
            experience_years=experience_years,
            image=image,
            specialization=specialization,
            **extra_fields
        )
        professional.set_password(password)
        professional.save(using=self._db)
        return professional

class CustomDoctor(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    contact_number = models.CharField(max_length=15)
    license_number = models.CharField(max_length=50, unique=True)
    experience_years = models.PositiveIntegerField()
    image = models.ImageField(upload_to='professional_profiles/')
    specialization = models.CharField(max_length=100)
    password = models.CharField(max_length=128)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)


    objects = DoctorManager()

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.email



class Product(models.Model):
    product_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    ingredients = models.TextField()
    image = models.ImageField(upload_to='product_images/')
    skin_type = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    stock_availability = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

