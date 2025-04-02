from django.utils.deprecation import MiddlewareMixin
from swawlambi_app.models import VisitorCounter

class VisitorMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.session.get('has_visited'):
            visitor, created = VisitorCounter.objects.get_or_create(id=1)
            visitor.count += 1
            visitor.save()
            request.session['has_visited'] = True  # Mark the session
