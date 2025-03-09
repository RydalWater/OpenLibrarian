from django.conf import settings

def test_mode(request):
    return {
        'test_mode': settings.TEST_MODE,
    }