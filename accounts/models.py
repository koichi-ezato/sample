from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, username, email, password, last_name, first_name):
        """
        ユーザ作成
        :param username:
        :param email:
        :param password:
        :param last_name:
        :param first_name:
        :return:
        """
        if not email:
            raise ValueError('User must have an email.')
        if not username:
            raise ValueError('User must have an username.')

        user = self.model(username=username,
                          email=email,
                          password=password,
                          last_name=last_name,
                          first_name=first_name)
        user.is_active = True
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, last_name, first_name):
        """
        スーパーユーザ作成
        :param username:
        :param email:
        :param password:
        :param last_name:
        :param first_name:
        :return:
        """
        user = self.create_user(username=username,
                                email=email,
                                password=password,
                                last_name=last_name,
                                first_name=first_name)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Belong(models.Model):
    """
    所属先
    """
    name = models.CharField(verbose_name='名称', max_length=10)
    delete_flg = models.BooleanField(verbose_name='削除フラグ', default=False)

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    """
    ユーザモデル
    """
    class Meta:
        verbose_name = 'ユーザ'
        verbose_name_plural = 'ユーザ'
        app_label = 'accounts'

    username = models.CharField(verbose_name='ユーザID',
                                unique=True,
                                max_length=30)
    password = models.CharField(verbose_name='パスワード',
                                max_length=128,
                                blank=True)
    last_name = models.CharField(verbose_name='苗字',
                                 max_length=30,
                                 default=None)
    first_name = models.CharField(verbose_name='名前',
                                  max_length=30,
                                  default=None)
    zip = models.CharField(verbose_name='郵便番号',
                           max_length=8,
                           default=None,
                           null=True,
                           blank=True)
    prefecture = models.CharField(verbose_name='都道府県',
                                  max_length=50,
                                  default=None,
                                  null=True,
                                  blank=True)
    city = models.CharField(verbose_name='市区町村',
                            max_length=100,
                            default=None,
                            null=True,
                            blank=True)
    address = models.CharField(verbose_name='番地',
                               max_length=100,
                               default=None,
                               null=True,
                               blank=True)
    email = models.EmailField(verbose_name='メールアドレス',
                              null=True,
                              default=None,
                              blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(verbose_name='有効フラグ',
                                    default=True)
    is_staff = models.BooleanField(verbose_name='管理サイトアクセス権限',
                                   default=False)
    belong = models.ForeignKey(to=Belong, on_delete=models.CASCADE, default=None, null=True, blank=True,
                               limit_choices_to={"delete_flg": False})

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'last_name', 'first_name']
    objects = UserManager()

    def __str__(self):
        if self.last_name and self.first_name:
            return self.last_name + ' ' + self.first_name
        else:
            return self.last_name

    def get_short_name(self):
        return self.last_name

    def get_full_name(self):
        return self.last_name + ' ' + self.first_name
