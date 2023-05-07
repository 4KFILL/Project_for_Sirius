## Как запустить

Для запуска приложения вам необходимо создать контейнер Docker с помощью следующей команды:

sh
docker run -d \
--name server \
-e POSTGRES_USER=sirius_2023 \
-e POSTGRES_PASSWORD=change_me \
-e PGDATA=/postgres_data_inside_container \
-v ~/Your/db/path/postgres_data:/postgres_data_inside_container \
-p 38746:5432 \
postgres:15.1


Также вам необходимо войти в базу данных и добавить свой собственный логин и пароль. Вот пример:

sql
CREATE EXTENSION "uuid-ossp";

CREATE TABLE IF NOT EXISTS equipment(
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    model text not null,
    manufacturer text not null,
    year_of_issue int not null,
    service_cost int not null,
    electricity_cost int not null
);

Вы должны создать телеграм-бота, используя @botfather в Telegram, и вставить токен созданного бота в строку в файле main.py:

bot = telebot.TeleBot("ВСТАВЬТЕ_СЮДА")

Наконец, вы можете запустить приложение с помощью следующей команды:

python main.py