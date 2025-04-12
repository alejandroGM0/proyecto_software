#!/bin/bash

echo "Generando datos de demostración para CharlaCar..."

# Ejecutar el comando de Django para generar datos de prueba
python manage.py generate_test_data --users 30 --rides 80 --chats 40 --messages 300 --reports 50 --payments 60

echo "¡Datos generados exitosamente!"
