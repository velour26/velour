from django.views.generic import TemplateView
from .models import Subscriber


class ConfirmView(TemplateView):
    template_name = 'pages/newsletter_confirm.html'

    def get_context_data(self, token=None, **kwargs):
        ctx = super().get_context_data(**kwargs)
        sub = Subscriber.objects.filter(confirm_token=token).first()
        if sub:
            sub.is_confirmed = True
            sub.confirm_token = ''
            sub.save(update_fields=['is_confirmed', 'confirm_token'])
            ctx['success'] = True
        else:
            ctx['success'] = False
        return ctx


class UnsubscribePageView(TemplateView):
    template_name = 'pages/newsletter_unsubscribe.html'
