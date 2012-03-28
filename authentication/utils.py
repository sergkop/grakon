from django.shortcuts import redirect

def authenticated_redirect(view_name):
    """ Decorator for views which redirects to a given view if user is authenticated """
    def view_decorator(view):
        def new_view(request, *args, **kwargs):
            if request.user.is_authenticated():
                return redirect(view_name)
            return view(request, *args, **kwargs)
        return new_view

    return view_decorator
