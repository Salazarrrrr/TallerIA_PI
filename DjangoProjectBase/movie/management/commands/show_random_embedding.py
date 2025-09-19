import numpy as np
from django.core.management.base import BaseCommand
from movie.models import Movie
import random

class Command(BaseCommand):
    help = 'Muestra los primeros valores del embedding de una película aleatoria.'

    def handle(self, *args, **kwargs):
        movies = list(Movie.objects.all())
        if not movies:
            self.stdout.write(self.style.ERROR('No hay películas en la base de datos.'))
            return
        movie = random.choice(movies)
        if not hasattr(movie, 'emb') or movie.emb is None:
            self.stdout.write(self.style.ERROR(f'La película "{movie.title}" no tiene embedding.'))
            return
        embedding_vector = np.frombuffer(movie.emb, dtype=np.float32)
        self.stdout.write(f'Película: {movie.title}')
        self.stdout.write(f'Primeros valores del embedding: {embedding_vector[:10]}')
