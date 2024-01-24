# well-yogapetz
### Функциональность:
1. Коннект новых аккаунтов по инвайтам
2. Выполнение всех заданий
3. Выполнение дейли заданий (пост дейли твита и клейм метидации)
4. Апдейт и получение инвайтов от использованных аккаунтов ранее
5. Клейм дейли книжек (если есть баланс)
6. Клейм всех доступных книжек (если есть баланс)
7. Сбор и получение статистики книжек по аккаунтам


### Как работает софт
При первом запуске, а иммено при модуле запуске "выполнение всех заданий", используемый токен + ключ записывается в базу данных, которая создается и хранится у вас в папке с проектом. После внесения в БД, токен+ключ связываются, можно выполнять дейли задания, клеймить дейли и все книжки, получать статистику по книжкам, генерировать инвайты от аккаунта. Прокси идут по кругу, то есть на 100 аккаунтов можно вставить 10 прокси и получится 10к1 прокси. Также все известные ошибки записываются в специальный текстовик.
#### Досутпно несколько модулей:
1. Выполнение всех заданий.

Подключение аккаунта через инвайт, подключение к нему кошелька, выполнение заданий, сохранение в БД токена+ключ.  

2. Выполнение дейли заданий.

Аккаунт берется из БД, выполняет дейли задания (медитация + дейли пост), минтит дейли книжку.

3. Минт книжек.

Аккаунт берется из БД, минитит все доступные книжки (не считая дейли)

4. Статистика всех книг на аккаунтах.

Аккаунты берутся из БД, обновляется информация о всех книжках на аккаунте, получение общей и индивидуальной статистики по аккаунту.

5.  Обновление инвайтов.

Обновление и получение инвайтов аккаунтов из БД, использованные инвайты записаны не будут.

6.  Обновление токена.

Если токен твиттера сломался, можно заменить его в БД.


### Первый запуск
* Установка библиотек (requirements.txt)
* В папку `data`, в соотвестующие файлы закидываем токены, ключи (**КОЛ-ВО ТОКЕНОВ ДОЛЖНО РАВНЯТЬСЯ КОЛ-ВО КЛЮЧАМ**), прокси (формат: http://log:pass@ip:port), дейли твиты (твиты, которые будет постить ваш акк), инвайты (без инвайтов первый запуск не получится, также кол-во инвайтов должно равнятся кол-во токенам).
* Запустить `main`

Пример: сделать один аккаунт руками, получить оттуда 5 инвайтов, на эти 5 инвайтов сделать 5 аккаунтов софтом, получить 25 инвайтов и запустить софт и так по кругу.



Инвайты:
* 2A3CJ
* V76S6
* SHN9L
* NC63V
* 6PCGK
* 62JTQ
* UGXU6
* TM9KF
* P6Q77
