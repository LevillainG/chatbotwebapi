from django.urls import path
from .views import ArticleListView, ArticleDetailView, ChatbotView, SetLanguageView, HomeView, RagView

urlpatterns = [
    path('', HomeView.as_view(), name='home'), #home page
    path('articles/', ArticleListView.as_view(), name='article_list'),
    path('articles/<int:pk>/', ArticleDetailView.as_view(), name='article_detail'),
    path('set_language/', SetLanguageView.as_view(), name='set_language'),
    path('chatbot/', ChatbotView.as_view(), name='chatbot'),
    path('rag/', RagView.as_view(), name='rag'),
]
