# signals.py
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from social_django.models import UserSocialAuth
import jwt
from django.contrib.auth.models import Group
from django.db import connections
from django.conf import settings
from .models import CustomPermittedSSOUsers
from django.dispatch import Signal
import logging

logger = logging.getLogger(__name__)

manage_user_permission_completed = Signal()
post_login_operations_completed = Signal()


def extract_project_permission(username):
    cursor = connections['live'].cursor()
    query = """select distinct eom.employee_project_id from application_user au
            inner join employee_core_info eci on au.username = eci.pin_no
            inner join employee_project_mapping eom on eci.id = eom.employee_info_id
            where au.username ~ '^[0]*""" + username + """$';"""

    cursor.execute(query)
    query_set = cursor.fetchall()
    permitted_project = [row[0] for row in query_set]

    if 9 in permitted_project:
        permitted_project = 'ALL'

    return permitted_project


def extract_office_permission(username):
    cursor = connections['live'].cursor()
    query = """select distinct eom.office_info_id from application_user au
            inner join employee_core_info eci on au.username = eci.pin_no
            inner join employee_office_mapping eom on eci.id = eom.employee_info_id
            where au.username ~ '^[0]*""" + username + """$';"""

    cursor.execute(query)
    query_set = cursor.fetchall()
    permitted_offices = [row[0] for row in query_set]

    if 2 in permitted_offices:
        permitted_offices = 'ALL'

    return permitted_offices


def assign_roles(user, roles):
    for role in roles:
        try:
            group, _ = Group.objects.get_or_create(name=role)
            group.user_set.add(user)
        except Exception as e:
            logger.error(f"Error assigning role {role} to user {user.username}: {e}")


@receiver(user_logged_in)
def manage_user_permission(sender, request, user, **kwargs):

    backend = request.session.get('_auth_user_backend')
    if backend != 'django.contrib.auth.backends.ModelBackend':
        provider_mapping = {
            'brac_auth.backend.KeycloakOAuth2_BRAC': 'brac',
            'brac_auth.backend.KeycloakOAuth2_EXTERNAL': 'external'
        }

        provider = provider_mapping.get(backend)

        if provider:
            try:
                social_user = UserSocialAuth.objects.get(user=user, provider=provider)

                # Keeping decoded access token in the session
                access_token = social_user.extra_data['access_token']
                decoded_token = jwt.decode(access_token, options={"verify_aud": False, "verify_signature": False})
                request.session['access_token'] = decoded_token

                # Printing decoded token for debugging purpose in both development and production
                # Do not remove it if it is not absolutely necessary
                print("Decoded Token: ", decoded_token)
                logger.warning(f"Decoded Token (Warning): {decoded_token}")

                # Removing old groups
                user.groups.filter(name__iregex=r'SSO_[a-zA-Z]*').delete()

                # Combining all the roles from access token
                client_id = decoded_token.get('azp', '')
                realm_roles = decoded_token.get('realm_access', {}).get('roles', [])
                resource_access = decoded_token.get('resource_access', {}).get(client_id, {}).get('roles', [])
                realm_authorities = decoded_token.get('authorities', [])
                sso_roles = ['SSO_' + role for role in realm_roles] + \
                            ['SSO_RES_' + role for role in resource_access] + \
                            ['SSO_AUTH_' + role for role in realm_authorities]

                # Assigning roles from access token to the user
                assign_roles(user, sso_roles)

                if set(settings.ALL_DATA_VIEW_PERMITTED_ROLES.split(",")) & set(sso_roles):
                    request.session['permitted_offices'] = 'ALL'
                    request.session['permitted_project'] = 'ALL'

                else:
                    username = decoded_token['preferred_username'].lstrip("0")
                    custom_user = CustomPermittedSSOUsers.objects.filter(sso_username=username).first()

                    if custom_user:
                        assign_roles(user, ['SSO_AUTOALLOWED'])
                        request.session['permitted_offices'] = 'ALL' \
                            if custom_user.override_office_permission else extract_office_permission(username)
                        request.session['permitted_project'] = 'ALL' \
                            if custom_user.override_project_permission else extract_project_permission(username)
                    else:
                        request.session['permitted_offices'] = extract_office_permission(username)
                        request.session['permitted_project'] = extract_project_permission(username)

                request.session["sso_oidc_endpoint"] = getattr(settings, "SOCIAL_AUTH_"+provider.upper()+"_OIDC_ENDPOINT", "")


            except UserSocialAuth.DoesNotExist:
                logger.warning(f"UserSocialAuth entry not found for user {user.username} and provider {provider}.")

            except Exception as e:
                logger.error(f"Error processing permissions for user {user.username}: {e}")

    else:
        request.session['permitted_offices'] = 'ALL'
        request.session['permitted_project'] = 'ALL'
    request.session["auth_user_backend"] = backend
    manage_user_permission_completed.send(sender=sender, request=request, user=user)


import pandas as pd

@receiver(manage_user_permission_completed)
def post_login_operations(sender, request, user, **kwargs):

    preselected_filters = {}

    # permitted_project = '' if request.session['permitted_project'] == 'ALL' else ','.join(request.session['permitted_project'])
    # permitted_office = '' if request.session['permitted_offices'] == 'ALL' else ','.join(request.session['permitted_offices'])

    # permitted_project = request.session['permitted_project']
    # permitted_office = request.session['permitted_offices']
    #
    # query = """select * from func_demarcation_filter_data_agami(%(project)s,'', '','',%(branch)s)"""
    # params = {
    #     'project': '' if permitted_project == 'ALL' else ','.join(permitted_project),
    #     'branch': '' if permitted_office == 'ALL' else ','.join(permitted_office)
    # }
    #
    # with connections['warehouse'].cursor() as cursor:
    #     cursor.execute(query, params)
    #     results = cursor.fetchall()
    #
    # results = pd.DataFrame(
    #     list(results),
    #     columns=["project_info_id", "project_code", "project_name", "division_id", "division_code", "division_name", "region_id", "region_code", "region_name", "area_id", "area_code", "area_name", "branch_id", "branch_code", "branch_name"]
    # )


    # default project
    # if permitted_project == 'ALL':
    #     preselected_filters['project'] = '2'
    # elif len(permitted_project) == 1:
    #     preselected_filters['project'] = permitted_project
    # else:
    #     preselected_filters['project'] = ''
    from datetime import date, timedelta
    from dateutil.relativedelta import relativedelta

    preselected_filters['project'] = {
        'id': 2,
        'text': '[60] Progoti'
    }
    preselected_filters['division'] = ''
    preselected_filters['region'] = ''
    preselected_filters['area'] = ''
    preselected_filters['branch'] = ''
    preselected_filters['member_category'] = ''
    preselected_filters['from_date'] = (date.today() - relativedelta(months=5)).replace(day=1).strftime('%Y-%m-%d')
    preselected_filters['to_date'] = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')

    request.session['preselected_filters'] = preselected_filters

    post_login_operations_completed.send(sender=sender, request=request, user=user)

