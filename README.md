## Desarrollo

![Diagrama gantt](https://i.imgur.com/RC3e00j.png)
![Diagrama gantt](https://i.imgur.com/1zgPOLy.png)

## Flujo de desarrollo recomendado

1. Para el desarrollo rapido y con cambios en tiempo real sin todas las funcionalidades de la aplicacion:
python .\manage.py runserver
2. Para el desarrollo con todas las funcionalidades de la aplicacion:
python -m daphne -p 8000 blablacar.asgi:application