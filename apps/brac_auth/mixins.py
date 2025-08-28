# from django.contrib.auth.mixins import UserPassesTestMixin
# from django.conf import settings
#
# class RoleCheckMixin(UserPassesTestMixin):
#
#     def test_func(self):
#
#         if self.request.session.get('_auth_user_backend') != 'django.contrib.auth.backends.ModelBackend':
#             allowed_roles_all = settings.ALLOWED_ROLES + "," + settings.ALL_DATA_VIEW_PERMITTED_ROLES
#             return self.request.user.groups.filter(name__in=allowed_roles_all.split(",")).exists()
#         else:
#             return True

from django.contrib.auth.mixins import UserPassesTestMixin
from asgiref.sync import sync_to_async
from django.conf import settings


class RoleCheckMixin(UserPassesTestMixin):

    async def test_func(self):
        # Access session using sync_to_async
        user_backend = await sync_to_async(lambda: self.request.session.get('_auth_user_backend'))()
        if user_backend != 'django.contrib.auth.backends.ModelBackend':
            allowed_roles_all = settings.ALLOWED_ROLES + "," + settings.ALL_DATA_VIEW_PERMITTED_ROLES
            role_permission = await sync_to_async(lambda: self.request.user.groups.filter(name__in=allowed_roles_all.split(",")).exists())()
            project_permission = await sync_to_async(lambda: self.request.session.get('permitted_project'))()
            office_permission = await sync_to_async(lambda: self.request.session.get('permitted_offices'))()
            is_head_office = (project_permission == 'ALL') and (office_permission == 'ALL')
            is_permitted = role_permission or is_head_office
            return is_permitted
        else:
            return True
