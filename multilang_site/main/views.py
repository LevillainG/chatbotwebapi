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

#For LLM
#from langchain.vectorstores.base import VectorStore
#from langchain.vectorstores.faiss import FAISS

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


class RagView(View):
    def get(self, request):
        return render(request, 'main/rag.html')

    def post(self, request):
        user_message = request.POST.get('message')
        if not user_message:
            return HttpResponseBadRequest("No message provided")

        # Load the FAISS index and article IDs
        index = faiss.read_index("article_index.faiss")
        with open("article_ids.txt", "r") as f:
            article_ids = [int(line.strip()) for line in f]

        # Tokenize and get embedding for the user's message
        tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
        model = AutoModel.from_pretrained("distilbert-base-uncased")

        inputs = tokenizer(user_message, return_tensors="pt")
        with torch.no_grad():
            user_embedding = model(**inputs).last_hidden_state[:, 0, :].numpy()

        # Retrieve the most relevant article
        D, I = index.search(user_embedding, k=1)
        article_id = article_ids[I[0][0]]
        article = Article.objects.get(id=article_id)

        # Generate a response using the article content
        gen_tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
        gen_model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")

        inputs = gen_tokenizer(user_message + " " + article.content, return_tensors="pt")
        summary_ids = gen_model.generate(inputs['input_ids'], max_length=50, min_length=25, length_penalty=2.0, num_beams=4, early_stopping=True)
        response = gen_tokenizer.decode(summary_ids[0], skip_special_tokens=True)

        return JsonResponse({'response': response})


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


