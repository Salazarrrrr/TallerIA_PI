import os
from django.core.management.base import BaseCommand
from movie.models import Movie

class Command(BaseCommand):
	help = "Asigna imágenes a las películas desde media/movie/images/ y actualiza la base de datos."

	def handle(self, *args, **kwargs):
		images_folder = os.path.join('media', 'movie', 'images')
		updated_count = 0

		for movie in Movie.objects.all():
			# Se asume que el nombre de la imagen es m_{titulo}.png
			image_filename = f"m_{movie.title}.png"
			image_path = os.path.join(images_folder, image_filename)

			if os.path.exists(image_path):
				# Guardar la ruta relativa en el campo image
				movie.image = os.path.join('movie', 'images', image_filename)
				movie.save()
				updated_count += 1
				self.stdout.write(self.style.SUCCESS(f"Imagen asignada: {movie.title}"))
			else:
				self.stderr.write(f"Imagen no encontrada para: {movie.title}")

		self.stdout.write(self.style.SUCCESS(f"Proceso terminado. {updated_count} películas actualizadas."))
