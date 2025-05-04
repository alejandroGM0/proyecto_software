# ==========================================
# Autor: David Colás Martín
# ==========================================
from django import forms

from .constants import MAX_RATING, MIN_RATING
from .models import Review


class ReviewForm(forms.ModelForm):
    """
    Formulario para crear y editar reseñas.
    """

    # Generar opciones de rating dinámicamente usando las constantes
    RATING_CHOICES = [(i, "⭐" * i) for i in range(MIN_RATING, MAX_RATING + 1)]

    rating = forms.ChoiceField(
        choices=RATING_CHOICES, widget=forms.RadioSelect, label="Puntuación"
    )

    comment = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Comparte tu experiencia sobre este viaje...",
            }
        ),
        label="Comentario",
        required=False,
    )

    class Meta:
        model = Review
        fields = ["rating", "comment"]

    def clean_rating(self):
        # Convertimos el valor a entero (viene como string del formulario)
        rating = int(self.cleaned_data["rating"])

        # Validamos que esté dentro del rango permitido
        if not (MIN_RATING <= rating <= MAX_RATING):
            raise forms.ValidationError(
                f"La puntuación debe estar entre {MIN_RATING} y {MAX_RATING}."
            )

        return rating
