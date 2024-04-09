# WOTMOD
## Мод для игр Мир Танков и World Of Tanks
Собирает сессионную статистику во время игры:
- Начало боя
- Выстрелы
- Попадания
- Результаты боя

Посмотреть результаты можно на сайте [wotstat.info](https://wotstat.info). В разделе инфографики доступны различные фильтры



## Общая информация
Этот репозиторий содержит всё необходимое для разработки мода.
- Когда то давно был на WGMods: https://wgmods.net/5652/ (**УСТАРЕЛО**)

## Мод
От релизной версии он отличается файлом wot_stat/common/crypto.py, сейчас в нём расположена заглушка, релизная версия кодирует отправляемый на сервер json, дабы усложнить жизнь желающим заспамить сервер фейковыми сообщениями.

### Компиляция 
На Unix системах `./build.sh -v 1.0.0.0-a.1 -d` в папке `WOTSTAT`. Флаг `-d` отвечает за дебаг версию с print_debug выводом.

## Структура
[Логгеры](WOTSTAT/res/scripts/client/gui/mods/wot_stat/logger/loggers) создают события [events](WOTSTAT/res/scripts/client/gui/mods/wot_stat/logger/events.py) и добавляют их в [eventLogger](WOTSTAT/res/scripts/client/gui/mods/wot_stat/logger/eventLogger.py), который хранит и добавляет в нужную игровую сессию [battleEventSession](WOTSTAT/res/scripts/client/gui/mods/wot_stat/logger/battleEventSession.py) это событие.


[BattleEventSession](WOTSTAT/res/scripts/client/gui/mods/wot_stat/logger/battleEventSession.py) группирует события и раз в N=5 секунд отправляет их на сервер. Каждый бой создаётся новый экземпляр `BattleEventSession(Events.OnEndLoad())`, все события внутри этого боя отправляются через этот экземпляр. Экземпляр завершает своё существование событием `Events.OnBattleResult()`.

Все остальные файлы служебные и не выполняют ключевой роли. 

## События
| Событие        | Статус | Описание                 |
| -------------- | :----: | :----------------------- |
| OnBattleStart  |   +    | Начало боя               |
| OnShot         |   +    | Факт совершения выстрела |
| OnBattleResult |   +    | Результат боя            |
| OnShotReceived |   -    | Полученное попадание     |
| OnDamage       |   -    | Информация об уроне      |


## Тестовый сервер
Мод сохраняет события на сервер, если вы хотите протестировать мод локально, вы можете запустить [тестовый сервер](https://github.com/SoprachevAK/wot-stat/tree/main/mod/serverPlaceholder) на NodeJS

1. В папке `World_of_Tanks/mods/configs/wot_stat` создать текстовый файл `config.cfg`, в который прописать 
```
{
    "eventURL": "http://localhost:5000/api/events/send",
    "initBattleURL":"http://localhost:5000/api/events/OnBattleStart"
}
```
2. Запустить serverPlaceholder `npm run serve`
3. Запустить танки
4. Готово. Теперь мод будет отправлять события на локальный сервер. Их можно посмотреть в консоле сервера. 

## Редактирование
Для корректной типизации и подсказок кода, рекоменду в корень проекда докачать следующие репозитории:

```bash
git clone https://github.com/IzeBerg/wot-src.git
git clone https://github.com/SoprachevAK/BigWorldPlaceholder.git
```

При редактировании в `vscode` установите расширение `Ruff`

## Сборка мода
1. С помощью [PjOrion](https://koreanrandom.com/forum/topic/15280-) скомпилировать (Run -> Compile py folder)
2. Запустить Zip-Packer.cmd для получения .wotmod файла
