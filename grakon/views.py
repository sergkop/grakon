import json

from django.core.urlresolvers import reverse
from django.views.generic.base import TemplateView

from elements.models import RESOURCE_CHOICES

class CodeDataView(TemplateView):
    template_name = 'code_data.js'

    # TODO: cache it
    def get_context_data(self, **kwargs):
        ctx = super(CodeDataView, self).get_context_data(**kwargs)

        ctx.update({
            'resources': json.dumps(RESOURCE_CHOICES, ensure_ascii=False),
            'get_subregions_url': reverse('get_subregions'),
        })
        return ctx

code_data = CodeDataView.as_view()
