def user_role(request):
    role = "User"

    if request.user.is_authenticated:
        if request.user.is_staff:
            role = "Admin"
        elif request.user.groups.filter(name="Faculty").exists():
            role = "Faculty"
        elif request.user.groups.filter(name="Student").exists():
            role = "Student"

    return {
        "user_role": role
    }