from django.utils import timezone, dateformat


def year(request):
    today_date = dateformat.format(timezone.now(), 'Y')
    return {
        'year': today_date
    }
