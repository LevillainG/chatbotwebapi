# main/views.py
import logging
import openai
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import translation
from django.utils.translation import activate, gettext as _
from django.conf import settings
from django.views import View

#For GPT
from django.http import JsonResponse, HttpResponseBadRequest
from transformers import pipeline

#Models
from main.models import Article  # Importe le modèle Article 

logger = logging.getLogger(__name__)

#Views
class ArticleListView(View):
    def get(self, request):
        articles = Article.objects.all()
        return render(request, 'main/article_list.html', {'articles': articles})
        
class ArticleDetailView(View):
    def get(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        return render(request, 'main/article_detail.html', {'article': article})

class ChatbotView(View):
    def get(self, request):
        return render(request, 'main/chatbot.html')

    def post(self, request):
        logger.debug(f"Request method: {request.method}")
        user_message = request.POST.get('message')
        if user_message:
            logger.debug(f"User message: {user_message}")
            try:
                api_token = settings.HUGGINGFACE_API_TOKEN
                headers = {"Authorization": f"Bearer {api_token}"}
                data = {"inputs": user_message}
                response = requests.post(
                    "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3",
                    headers=headers,
                    json=data
                )
                response_json = response.json()
                logger.debug(f"Chatbot response: {response_json}")
                if response.status_code == 200:
                    return JsonResponse({'response': response_json[0]['generated_text']})
                else:
                    return JsonResponse({'error': 'Failed to generate response'}, status=response.status_code)
            except Exception as e:
                logger.error(f"Error generating response: {e}")
                return JsonResponse({'error': 'Failed to generate response'}, status=500)
        return HttpResponseBadRequest("No message provided")


class SetLanguageView(View):
    def get(self, request):
        language = request.GET.get('language')
        if language:
            activate(language)
            response = redirect(request.META.get('HTTP_REFERER', '/'))
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)
            return response
        return redirect('/')

    
class HomeView(View):
    def get(self, request):
        return render(request, 'main/home.html')

class SearchView(View):
    def get(self, request):
        query = request.GET.get('q', '')
        articles = Article.objects.filter(title__icontains=query) if query else []
        return render(request, 'main/search.html', {'articles': articles, 'query': query})


