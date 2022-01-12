### Foodgram, «Продуктовый помощник».

## В этом сервисе можно:
##### создавать рецепты,
##### добавлять рецепты в избранное,
##### добавлять рецепты в список покупок, а потом скачивать их,
##### подписываться на авторов рецептов.

## Что бы поставить этот проект у себя на серевере надо:

## скопировать этот проект на свой компьютер:
```sh
git clone https://github.com/nu-shtosh/foodgram-project-react.git
не забудь создать .env
```

## войти на свой сервер скопировать docker-compose, nginx, .env:
```sh
scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yml
scp nginx.conf <username>@<host>:/home/<username>/nginx.conf
scp .env <username>@<host>:/home/<username>/.env
```
## установать docker: 
```sh
sudo apt install docker.io 
``````
## уствновить docker-compose:
```sh
sudo apt install docker-compose
```
## собрать контейнер:
```sh
sudo docker-compose up -d --build
```
## собрать статику и сделать миграции:
```sh
sudo docker-compose exec backend python manage.py collectstatic --noinput
sudo docker-compose exec backend python manage.py makemigrations --noinput
sudo docker-compose exec backend python manage.py migrate --noinput
```
## загрузить стандартный набор тегов и ингредиентов:
```sh
sudo docker-compose exec backend python manage.py load_ing
sudo docker-compose exec backend python manage.py load_tags
```
## посмотреть админку можно через этот логин:
##### http://84.201.177.196/
##### login: admin@ya.ru
##### password: admin


![Python](https://camo.githubusercontent.com/a1b2dac5667822ee0d98ae6d799da61987fd1658dfeb4d2ca6e3c99b1535ebd8/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f707974686f6e2d3336373041303f7374796c653d666f722d7468652d6261646765266c6f676f3d707974686f6e266c6f676f436f6c6f723d666664643534)
![Django](https://camo.githubusercontent.com/5473e0d3006bb7e662bdf754d830a026ce050be61f1cbbd4689783ae49950b93/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f646a616e676f2d2532333039324532302e7376673f7374796c653d666f722d7468652d6261646765266c6f676f3d646a616e676f266c6f676f436f6c6f723d7768697465)
![DjangoREST](https://camo.githubusercontent.com/cbef21adebc167fac6552145a03c9e12ae03b8afd5e4f7de52379a98297de3fe/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f444a414e474f2d524553542d6666313730393f7374796c653d666f722d7468652d6261646765266c6f676f3d646a616e676f266c6f676f436f6c6f723d776869746526636f6c6f723d666631373039266c6162656c436f6c6f723d67726179)
![Nginx](https://camo.githubusercontent.com/cf56166218460a063162d778334b2489fc8c568fa9b330689850e9a7eed9be72/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f6e67696e782d2532333030393633392e7376673f7374796c653d666f722d7468652d6261646765266c6f676f3d6e67696e78266c6f676f436f6c6f723d7768697465)
![Postgres](https://camo.githubusercontent.com/29e7fc6c62f61f432d3852fbfa4190ff07f397ca3bde27a8196bcd5beae3ff77/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f706f7374677265732d2532333331363139322e7376673f7374796c653d666f722d7468652d6261646765266c6f676f3d706f737467726573716c266c6f676f436f6c6f723d7768697465)
![Docker](https://camo.githubusercontent.com/6b7f701cf0bea42833751b754688f1a27b6090fdf90bf2b226addff01be817f0/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f646f636b65722d2532333064623765642e7376673f7374796c653d666f722d7468652d6261646765266c6f676f3d646f636b6572266c6f676f436f6c6f723d7768697465)
