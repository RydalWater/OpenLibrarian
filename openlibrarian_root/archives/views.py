from django.shortcuts import render
from utils.Session import async_get_session_info, async_logged_in

# About Page
async def about(request):
    """View for the About page of the website."""
    context = await async_get_session_info(request)
    # TODO: Update about page content
    return render(request, 'archives/about.html', context)

# 404 Page
def page_not_found_view(request, exception):
    """View for the 404 page of the website."""
    return render(request, 'archives/404.html', status=404)
