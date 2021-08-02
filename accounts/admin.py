from django.contrib import admin
from django.contrib.auth.hashers import make_password
from django.utils.safestring import mark_safe

from import_export import resources
from import_export import fields
from import_export.admin import ExportMixin
from import_export.formats import base_formats


from .models import User, Belong


class IsActiveListFilter(admin.SimpleListFilter):
    title = '有効フラグ'
    parameter_name = 'is_active'

    def lookups(self, request, model_admin):
        return (
            ('True', '有効'),
            ('False', '無効')
        )

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(is_active=True)
        elif self.value() == 'False':
            return queryset.filter(is_active=False)
        else:
            return queryset.all()


class UserResource(resources.ModelResource):
    custom_field = fields.Field(column_name='カスタムフィールド')

    def dehydrate_custom_field(self, data: User):
        return '{0:%Y/%-m/%-d}'.format(data.date_joined)

    def after_export(self, queryset, data, *args, **kwargs):
        data.headers = []

    class Meta:
        model = User
        fields = ['custom_field']


class InputFilter(admin.SimpleListFilter):
    template = 'admin/input_filter.html'

    def lookups(self, request, model_admin):
        # Dummy, required to show the filter.
        return ((),)

    def choices(self, changelist):
        # Grab only the "all" option.
        all_choice = next(super().choices(changelist))
        all_choice['query_parts'] = (
            (k, v)
            for k, v in changelist.get_filters_params().items()
            if k != self.parameter_name
        )
        yield all_choice


class NameFilter(InputFilter):
    parameter_name = 'last_name'
    title = '苗字'

    def queryset(self, request, queryset):
        if self.value() is not None:
            last_name = self.value()

            if last_name is None:
                return

            return queryset.filter(last_name__icontains=last_name)


class EmailFilter(InputFilter):
    parameter_name = 'email'
    title = 'メールアドレス'

    def queryset(self, request, queryset):
        if self.value() is not None:
            email = self.value()

            if email is None:
                return

            return queryset.filter(email__icontains=email)


@admin.register(User)
class UserAdmin(ExportMixin, admin.ModelAdmin):
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
    list_filter = [IsActiveListFilter, NameFilter, EmailFilter]
    actions = None
    search_fields = ['name', 'email']
    # list_display_links = None

    resource_class = UserResource
    formats = [base_formats.CSV]
    base_formats.CSV.CONTENT_TYPE = 'text/csv; charset=CP932'

    def get_export_filename(self, request, queryset, file_format):
        filename = "%s.%s" % ("Sample",
                              file_format.get_extension())
        return filename

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


@admin.register(Belong)
class BelongAdmin(admin.ModelAdmin):
    list_display = ['name', 'delete_flg']
