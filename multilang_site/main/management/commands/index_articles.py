import torch
import faiss
import numpy as np
from django.core.management.base import BaseCommand
from transformers import AutoTokenizer, AutoModel
from main.models import Article

class Command(BaseCommand):
    help = 'Index articles using FAISS'

    def handle(self, *args, **kwargs):
        articles = Article.objects.all()
        texts = [article.content for article in articles]

        tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
        model = AutoModel.from_pretrained("distilbert-base-uncased")

        # Tokenize and get embeddings
        inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():  # Ensure torch is used here
            embeddings = model(**inputs).last_hidden_state[:, 0, :].numpy()

        # Create FAISS index
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)

        # Save the index
        faiss.write_index(index, "article_index.faiss")

        # Save article IDs
        with open("article_ids.txt", "w") as f:
            for article in articles:
                f.write(f"{article.id}\n")

        self.stdout.write(self.style.SUCCESS('Successfully indexed articles'))

