from accounts.models import Branch


def app_context(request):
    return {
        "SCHOOL_NAME": "ECOME Finance",
        "ALL_BRANCHES": Branch.objects.all() if request.user.is_authenticated else [],
    }
