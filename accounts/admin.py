from django.contrib import admin
from django.contrib.auth.hashers import make_password
from django.utils.safestring import mark_safe

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        """
        モデルの保存
        :param request:
        :param obj:
        :param form:
        :param change:
        :return:
        """
        if change:
            user = User.objects.get(pk=obj.pk)
            if not user.password == obj.password:
                obj.password = make_password(obj.password)
        else:
            obj.password = make_password(obj.password)
        obj.save()

    list_display = ['username', 'name', 'email', 'merge_address']
    ordering = ['username']

    def name(self, obj):
        return obj.last_name + ' ' + obj.first_name

    name.short_description = '氏名'

    def merge_address(self, obj):
        address = ''
        if obj.zip:
            address += obj.zip + '<br>'
        if obj.prefecture:
            address += obj.prefecture + '<br>'
        if obj.city:
            address += obj.city + '<br>'
        if obj.address:
            address += obj.address

        return mark_safe(address)

    merge_address.short_description = '住所'
