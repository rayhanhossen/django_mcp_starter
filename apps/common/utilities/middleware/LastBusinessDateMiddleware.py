from django.utils.deprecation import MiddlewareMixin
from datetime import datetime, timedelta
import calendar
from django.db import connections
from common.cache.QueryCaching import cached_execute_query

class LastBusinessDateMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if not request.session.get('last_business_date', None):
            request.session['last_business_date'] = self.last_business_day(datetime.today()) # "2023-12-31"

    def last_business_day(self, date):

        if not isinstance(date, datetime):
            date = datetime.strptime(date, '%Y-%m-%d')

        day_before = date - timedelta(days=1)
        _, last_day = calendar.monthrange(day_before.year, day_before.month)
        is_month_close = (day_before.day == last_day)

        if is_month_close:
            return day_before.strftime('%Y-%m-%d')
        else:
            is_weekend = day_before.weekday() in [4, 5]

        if not is_weekend:
            query = """
                select * from holiday
                where %(date)s between from_date and to_date and office_id is null and approval_type = 'APPROVED'
            """
            params = {
                'date': day_before.strftime('%Y-%m-%d')
            }

            results = cached_execute_query(connections['live'], query, params)

            is_holiday = len(results) != 0

            if not is_holiday:
                return day_before.strftime('%Y-%m-%d')
            else:
                return self.last_business_day(day_before)
        else:
            return self.last_business_day(day_before)