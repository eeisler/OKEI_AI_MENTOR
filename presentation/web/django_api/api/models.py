from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class BaseModel(models.Model):
    class Meta:
        abstract = True 


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('Login обязателен')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.pop('email', None)
        if 'first_name' not in extra_fields:
            extra_fields['first_name'] = 'Admin'
        if 'middle_name' not in extra_fields:
            extra_fields['middle_name'] = 'Admin'
        if 'last_name' not in extra_fields:
            extra_fields['last_name'] = ''
        
        return self.create_user(username, password, **extra_fields)


class Department(BaseModel):
    name = models.CharField(max_length=200, blank=False, unique=True)

    def __str__(self):
        return f"{self.name}"


class Specialty(BaseModel):
    code = models.CharField(max_length=100, blank=False, unique=True)
    short_name = models.CharField(max_length=100, blank=False, unique=True)
    full_name = models.CharField(max_length=100, blank=False, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.full_name}"

class Group(BaseModel):
    course = models.IntegerField()
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE)
    group_number = models.IntegerField(blank=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.course}{self.specialty.short_name}{self.group_number}"


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        verbose_name='Логин'
    )
    first_name = models.CharField(max_length=255, blank=False, verbose_name='Имя', default='test')
    middle_name = models.CharField(max_length=255, blank=False, verbose_name='Фамилия', default='test')
    last_name = models.CharField(max_length=255, blank=True, verbose_name='Отчество', default='test')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    email = None
    
    REQUIRED_FIELDS = [] 
    USERNAME_FIELD = 'username'

    objects = UserManager()

    class Meta:
        db_table = 'user'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Dialog(BaseModel):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    user_message = models.CharField(max_length=1000, blank=False)
    ai_response = models.CharField(max_length=1000, blank=False)
    question_id = models.IntegerField(blank=True, null=True)
    user_message_time = models.DateTimeField()
    ai_response_time = models.DateTimeField()

class SkillMatrix(BaseModel):
    specialty = models.ForeignKey(Specialty, blank=False, on_delete=models.CASCADE)
    course = models.IntegerField()
    skill = models.CharField(max_length=500, blank=False)
    description = models.CharField(max_length=500, blank=False)
    criterions = models.CharField(max_length=500, blank=False)

    def __str__(self):
        return f"{self.skill} - {self.description}"


class StudentProgress(BaseModel):
    student_id = models.IntegerField()
    skill_id = models.IntegerField()
    level = models.IntegerField()
    weaknesses = models.CharField(max_length=500, blank=True)

 