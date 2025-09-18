import os
import numpy as np
from django.core.management.base import BaseCommand
from movie.models import Movie
from openai import OpenAI
from dotenv import load_dotenv

class Command(BaseCommand):
    help = "Compare two movies and optionally a prompt using OpenAI embeddings"

    def handle(self, *args, **kwargs):
        # Configuración fácil de modificar
        MOVIE_TITLE_1 = "The Knockout"
        MOVIE_TITLE_2 = "La captura"
        PROMPT = "Pelea de boxeo en un ring con mucha gente animando y aventura"

        # Cargar API key
        load_dotenv('../openAI.env')
        client = OpenAI(api_key=os.environ.get('openai_apikey'))


        # Mostrar todos los títulos disponibles en la base de datos
        self.stdout.write("\n=== Títulos disponibles en la base de datos ===")
        for m in Movie.objects.all():
            self.stdout.write(repr(m.title))

        # Buscar películas y manejar errores
        # Buscar películas de forma insensible a mayúsculas/minúsculas y espacios
        movie1 = Movie.objects.filter(title__iexact=MOVIE_TITLE_1.strip()).first()
        if not movie1:
            self.stderr.write(f"No se encontró la película: {MOVIE_TITLE_1}")
            return
        movie2 = Movie.objects.filter(title__iexact=MOVIE_TITLE_2.strip()).first()
        if not movie2:
            self.stderr.write(f"No se encontró la película: {MOVIE_TITLE_2}")
            return

        # Mostrar películas seleccionadas
        self.stdout.write("\n=== Películas seleccionadas ===")
        self.stdout.write(f"Película 1: {movie1.title}")
        self.stdout.write(f"Descripción 1: {movie1.description}")
        self.stdout.write(f"Película 2: {movie2.title}")
        self.stdout.write(f"Descripción 2: {movie2.description}\n")

        def get_embedding(text):
            response = client.embeddings.create(
                input=[text],
                model="text-embedding-3-small"
            )
            return np.array(response.data[0].embedding, dtype=np.float32)

        def cosine_similarity(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

        # Embeddings de las películas
        emb1 = get_embedding(movie1.description)
        emb2 = get_embedding(movie2.description)

        # Similitud entre películas
        similarity = cosine_similarity(emb1, emb2)
        self.stdout.write(f"\U0001F3AC Similaridad entre '{movie1.title}' y '{movie2.title}': {similarity:.4f}")

        # Comparar prompt contra todas las películas
        self.stdout.write("\n=== Prompt de búsqueda ===")
        self.stdout.write(f"Prompt: {PROMPT}\n")
        prompt_emb = get_embedding(PROMPT)

        similarities = []
        for movie in Movie.objects.all():
            emb = get_embedding(movie.description)
            sim = cosine_similarity(prompt_emb, emb)
            similarities.append((movie.title, sim))

        # Ordenar por similitud descendente y mostrar las top 10
        similarities.sort(key=lambda x: x[1], reverse=True)
        self.stdout.write("\nPelículas más similares al prompt:")
        for title, sim in similarities[:10]:
            self.stdout.write(f"{title}: {sim:.4f}")