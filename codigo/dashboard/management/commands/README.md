# Generador de Datos de Prueba para CharlaCar

Este comando de gestión de Django genera datos de prueba aleatorios.
## Uso

Para generar datos de prueba, ejecute:

```bash
python manage.py generate_test_data
```

### Opciones disponibles

- `--users NUMBER`: Número de usuarios a crear (por defecto: 20)
- `--rides NUMBER`: Número de viajes a crear (por defecto: 50)
- `--chats NUMBER`: Número de chats a crear (por defecto: 30)
- `--messages NUMBER`: Número de mensajes a crear (por defecto: 200)
- `--reports NUMBER`: Número de reportes a crear (por defecto: 25)
- `--payments NUMBER`: Número de pagos a crear (por defecto: 40)
- `--clean`: Elimina todos los datos existentes antes de generar nuevos datos

### Ejemplos

Generar datos con los valores predeterminados:
```bash
python manage.py generate_test_data
```

Generar un conjunto más grande de datos:
```bash
python manage.py generate_test_data --users 100 --rides 200 --messages 1000
```

Limpiar la base de datos y generar un pequeño conjunto de datos:
```bash
python manage.py generate_test_data --clean --users 10 --rides 20
```