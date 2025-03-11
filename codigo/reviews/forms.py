from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    """
    Formulario para crear y editar reseñas.
    """
    RATING_CHOICES = [
        (1, '⭐'),
        (2, '⭐⭐'),
        (3, '⭐⭐⭐'),
        (4, '⭐⭐⭐⭐'),
        (5, '⭐⭐⭐⭐⭐'),
    ]
    
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect,
        label="Puntuación"
    )
    
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Comparte tu experiencia sobre este viaje...'
        }),
        label="Comentario",
        required=False
    )
    
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        
    def clean_rating(self):
        # Convertimos el valor a entero (viene como string del formulario)
        return int(self.cleaned_data['rating'])