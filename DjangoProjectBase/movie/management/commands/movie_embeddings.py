import os
import numpy as np
from django.core.management.base import BaseCommand
from movie.models import Movie
from openai import OpenAI
from dotenv import load_dotenv

class Command(BaseCommand):
    help = "Generar y almacenar embeddings para todas las películas en la base de datos"

    def handle(self, *args, **kwargs):
        load_dotenv('../openAI.env')
        client = OpenAI(api_key=os.environ.get('openai_apikey'))

        peliculas = Movie.objects.all()
        self.stdout.write(f"Se encontraron {peliculas.count()} películas en la base de datos")

        def obtener_embedding(texto):
            respuesta = client.embeddings.create(
                input=[texto],
                model="text-embedding-3-small"
            )
            return np.array(respuesta.data[0].embedding, dtype=np.float32)

        for pelicula in peliculas:
            try:
                emb = obtener_embedding(pelicula.description)
                pelicula.emb = emb.tobytes()
                pelicula.save()
                self.stdout.write(self.style.SUCCESS(f"Embedding almacenado para: {pelicula.title}"))
            except Exception as e:
                self.stderr.write(f"No se pudo generar el embedding para {pelicula.title}: {e}")

        self.stdout.write(self.style.SUCCESS("Finalizó la generación de embeddings para todas las películas"))
