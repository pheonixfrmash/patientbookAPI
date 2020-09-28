from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
import uuid

GENDER = (
    ('male','MALE'),
    ('female', 'FEMALE'),
    ('others','OTHERS'),
)

class PbUserManager(BaseUserManager):
    def create_user(self, email,date_of_birth,gender,first_name,last_name, password=None):
        """
        Creates a user with email and other details.
        """
        if not email:
            raise ValueError('User must have an email')
        if not date_of_birth:
            raise ValueError("Please enter date of birth")
        if not gender:
            raise ValueError("Please enter your gender")
        if not first_name:
            raise ValueError("Please enter your First Name")
        if not last_name:
            raise ValueError("Please enter your Last name")
        
        user = self.model(email=self.normalize_email(email),
                          date_of_birth=date_of_birth,
                          gender=gender,
                          first_name=first_name,
                          last_name=last_name, 
            )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password,date_of_birth,gender,first_name,last_name):
        """
        Creates and saves a superuser with the given email and
        details.
        """
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            date_of_birth=date_of_birth,
            gender=gender,
            first_name=first_name,
            last_name=last_name, 
        )
        user.is_admin = True
        user.is_staff   = True
        user.is_active  = True 
        user.is_superuser = True
        user.save(using=self._db)
        return user


class PbUser(AbstractBaseUser):
    email                   = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    date_joined				= models.DateTimeField(verbose_name="date joined", auto_now_add=True, blank=True)
    last_login				= models.DateTimeField(verbose_name="last login", auto_now=True, blank=True)
    is_active               = models.BooleanField(default=True)
    is_admin                = models.BooleanField(default=False)
    is_staff				= models.BooleanField(default=False)
    is_superuser			= models.BooleanField(default=False)
    date_of_birth           = models.DateField(verbose_name="date of birth")
    first_name              = models.CharField(verbose_name="first name", max_length=100, blank=True)
    last_name               = models.CharField(verbose_name="last name", max_length=100,  blank=True)
    gender                  = models.CharField(verbose_name='gender', max_length=30,choices=GENDER, default='others')
    jwt_secret              = models.UUIDField(default=uuid.uuid4)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password','date_of_birth','gender','first_name','last_name',]
    
    objects = PbUserManager()
    
    def __str__(self):
        return self.email
    
    def has_perm(self,perm,obj=None):
            return self.is_admin
    
    def has_module_perms(self,app_label):
        return self.is_active
    
def jwt_get_secret_key(self):
       return self.jwt_secret