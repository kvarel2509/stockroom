from django.views import generic

from stockroom.forms import GenerateDataForm
from stockroom.logic.search_engine_for_ways_to_relocate.entities import SearchRequestData
from stockroom.use_cases import get_client_list, get_client_holder_product_batches, \
	get_available_stockroom_baskets_for_relocate_product_batch, find_way_for_relocate


class ClientListView(generic.TemplateView):
	template_name = 'stockroom/client_list.html'

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		client_list = get_client_list()
		ctx['client_list'] = client_list.data.get('clients')
		return ctx


class ClientHolderProductBatchListView(generic.TemplateView):
	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		client_pk = self.get_client_pk()
		client_holder_product_batches = get_client_holder_product_batches(client_pk)
		ctx['client'] = client_holder_product_batches.data.get('client')
		ctx['client_holder_product_batches'] = client_holder_product_batches.data.get('product_batches')
		return ctx

	def get_client_pk(self):
		return self.kwargs.get('pk')


class RelocationListView(generic.TemplateView):
	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		product_batch_pk = self.get_product_batch_pk()
		stockroom_baskets = get_available_stockroom_baskets_for_relocate_product_batch(product_batch_pk)
		ctx['stockroom_baskets'] = stockroom_baskets.data.get('stockroom_baskets')
		short_way_search_request_data = SearchRequestData(
			product_batch_pk=product_batch_pk,
			method_alias='short_way',
			amount=self.get_amount(),
			options_count=1
		)
		cheap_way_search_request_data = SearchRequestData(
			product_batch_pk=product_batch_pk,
			method_alias='short_way',
			amount=self.get_amount(),
			options_count=1
		)
		ctx['short_way'] = find_way_for_relocate(short_way_search_request_data).data.get('ways')
		ctx['cheap_way'] = find_way_for_relocate(cheap_way_search_request_data).data.get('ways')
		return ctx

	def get_product_batch_pk(self):
		return self.kwargs.get('pk')

	def get_amount(self):
		return self.request.GET.get('amount')


class GenerateDataFormView(generic.FormView):
	form_class = GenerateDataForm

	def form_valid(self, form):
		pass