from django.contrib import messages
from django.shortcuts import render
from .forms import SearchForm
from .services import MongoMService
from django.http.response import JsonResponse, Http404
from collection.models import Collection, CollectionItem, Message


def index(request):
    try:
        if request.method == 'POST':
            form = SearchForm(request.POST)
            if form.is_valid():
                collection_id = form.cleaned_data['collection']
            else:
                context = {
                    'form': form,
                    'dictionary': None,
                    'collection_id': None
                }
                messages.add_message(request, messages.WARNING, "Collection field is required.")
                return render(request, 'index.html', context)
        else:
            form = SearchForm()
            collection_id = None
        value = request.POST.get('collection').strip()
        if Collection.objects.filter(field_id=value).exists():
            dict_ = CollectionItem.objects.filter(collection__field_id=value).order_by('item_id')
            message_list = Message.objects.filter(collection__field_id=value)
            for message in message_list:
                messages.add_message(request, messages.INFO, message.message)
        else:
            m = MongoMService()
            if collection_id:
                result_dictionary = m.MongoM(collection_id)
                for message_key in result_dictionary.get('messages', []):
                    collection_list = list()
                    try:
                        for key, value in message_key.items():
                            collection_list.append(key)
                    except:
                        collection_list.append(message_key)
                    messages.add_message(request, messages.INFO, collection_list)
                collection = Collection.objects.create(field_id=value)
                for key in result_dictionary.get('dicti', {}).keys():
                    CollectionItem.objects.create(item_id=key, collection=collection)
                for key in result_dictionary.get('messages', []):
                    Message.objects.create(message=key, collection=collection)
            else:
                result_dictionary = {'dicti': None, 'messages': None}
            dict_ = CollectionItem.objects.filter(collection__field_id=value).order_by('item_id')
    except:
        dict_ = {}
        if request.method == 'POST':
            messages.add_message(request, messages.WARNING, "Collection field is invalid.")
        form = SearchForm()
        collection_id = ""

    context = {
        'form': form,
        'dictionary': dict_,
        "collection_id": collection_id
    }
    return render(request, 'index.html', context)


def get_image_as_json(request):
    token_id = request.GET['token_id']
    collection_id = request.GET['collection_id'].strip()

    m = MongoMService()
    filename = m.Graph_vis2(collections=collection_id, token=token_id)

    return JsonResponse({'filename': filename})
