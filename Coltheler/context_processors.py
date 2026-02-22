from .services.base_service import BaseService


def sidebar_profile(request):
    if not request.user.is_authenticated:
        return {}

    details = BaseService.get_user_details(request.user.id)
    return {"sidebar_profile_pic": details.get("profile_pic")}
