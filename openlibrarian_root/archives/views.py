from django.shortcuts import render
from utils.Releases import get_release_info

# About Page
async def about(request):
    """View for the About page of the website."""
    # TODO: Update about page content to include more about the project
    return render(request, 'archives/about.html')

async def updates(request):
    """View for the Updates page of the website."""
    release_info = await get_release_info()
    context = {
        'release_info': release_info
    }
    return render(request, 'archives/updates.html', context)

def privacy(request):
    """View for the Privacy page of the website."""
    return render(request, 'archives/privacy.html')

# 404 Page
def page_not_found_view(request, exception):
    """View for the 404 page of the website."""
    return render(request, 'archives/404.html', status=404)
