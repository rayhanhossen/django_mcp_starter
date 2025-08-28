from django.views import View
# from django.contrib.auth.mixins import LoginRequiredMixin
from .mixins import RoleCheckMixin
from django.shortcuts import redirect, reverse
from django.contrib.auth import logout as auth_logout
from urllib.parse import urlencode
from django.conf import settings

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required



class LoginView(View):
    provider = None

    def get(self, request, *args, **kwargs):
        redirect_url = reverse('social:begin', args=[self.provider])
        if self.provider == 'brac':
            query_params = {'next': request.GET.get('next', '/')}
        else:
            query_params = {'next': '/'}
        redirect_url = f"{redirect_url}?{urlencode(query_params)}"
        return redirect(redirect_url)

class LogoutView(View):
    # def get(self, request, *args, **kwargs):
    #     auth_logout(request)  # Logs out the user
    #     return redirect('/')

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.session.get('_auth_user_backend') != 'django.contrib.auth.backends.ModelBackend':

                # Get OIDC endpoint for the user
                backend_name = request.session.get('social_auth_last_login_backend')
                oidc_endpoint = f"SOCIAL_AUTH_{backend_name.upper()}_OIDC_ENDPOINT"

                # Construct Keycloak logout URL
                keycloak_logout_url = (
                    f"{getattr(settings, oidc_endpoint)}/protocol/openid-connect/logout"
                )

                redirect_uri = request.build_absolute_uri('/')  # Redirect to homepage after logout

                # Prepare query parameters for Keycloak logout
                query_params = {
                    'post_logout_redirect_uri': redirect_uri,
                    'client_id': request.session['access_token']['azp'],
                }

                # Redirect to Keycloak logout URL
                keycloak_logout_with_params = f"{keycloak_logout_url}?{urlencode(query_params)}"

                # Log out from Django
                auth_logout(request)

                return redirect(keycloak_logout_with_params)

            else:
                auth_logout(request)
                return redirect('/')

class RolePermittedView(RoleCheckMixin,View):
    @method_decorator(login_required)

    async def dispatch(self, request, *args, **kwargs):

        user_test_result = await self.test_func()
        if not user_test_result:
            return self.handle_no_permission()

        if request.method.lower() in self.http_method_names:
            handler = getattr(
                self, request.method.lower(), self.http_method_not_allowed
            )
        else:
            handler = self.http_method_not_allowed
        return await handler(request, *args, **kwargs)

    @staticmethod
    def filter_office_manipulation(request, office_string):
        if request.session['permitted_offices'] == 'ALL':
            return office_string
        elif request.session['permitted_offices'] == '':
            return '-1'
        else:
            if office_string == '':
                return ",".join(map(str, request.session['permitted_offices']))
            else:
                office_list = map(int, office_string.split(","))
                filtered_office = set(request.session['permitted_offices']).intersection(set(office_list))
                return ','.join(map(str, filtered_office))

    @staticmethod
    def filter_project_manipulation(request, project_string):

        if request.session['permitted_project'] == 'ALL':
            return project_string
        elif request.session['permitted_project'] == '':
            return '-1'
        else:
            if project_string == '':
                return ",".join(map(str, request.session['permitted_project']))
            else:
                project_list = map(int, project_string.split(","))
                filtered_project = set(request.session['permitted_project']).intersection(set(project_list))

                return ','.join(map(str, filtered_project))