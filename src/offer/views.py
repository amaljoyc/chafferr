from __future__ import unicode_literals

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import generic
from query.models import Query
from django.db.models import Q

from . import forms


class QueryList(LoginRequiredMixin, generic.ListView):
    model = Query
    paginate_by = 6
    context_object_name = "queries"
    template_name = "offer/query_list.html"
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        return super(QueryList, self).get(request, *args, **kwargs)

    def get_queryset(self):
        cat = self.request.GET.get('cat')
        find = self.request.GET.get('find')
        if cat:
            return super(QueryList, self).get_queryset().order_by('-id').filter(category__name__icontains=cat)
        elif find:
            return super(QueryList, self).get_queryset().order_by('-id').\
                filter(Q(category__name__icontains=find) | Q(subject__icontains=find) | Q(content__icontains=find))
        else:
            return super(QueryList, self).get_queryset().order_by('-id')

class DoOffer(LoginRequiredMixin, generic.TemplateView):
    template_name = "offer/offer.html"
    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        kwargs['query_id'] = request.GET.get('query')
        kwargs["offer_form"] = forms.OfferForm()
        return super(DoOffer, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        query_id = request.POST['query_id']
        offer_form = forms.OfferForm(request.POST)
        if not (offer_form.is_valid()):
            messages.error(request, "There was a problem with the form. "
                                    "Please check the details.")
            offer_form = forms.OfferForm()
            return super(DoOffer, self).get(request, offer_form=offer_form)

        offer = offer_form.save(commit=False)
        offer.user = user
        offer.query = Query.objects.get(id=query_id)
        offer.save()

        messages.success(request, "Offer saved!")
        return redirect("offer:do_offer")