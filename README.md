filetree_mapreduce
==================

Простой Mapreduce на Python для обработки дерева файлов.

Входные данные складываются в файлы в папке files/ в формате
foobar.com  /foo/bar/  File1.java
barbaz.com  /bar/baz/  File1.java
foobar.com  /foo/      File2.java


На выходе получаеются деревья файлов для данных источников. Пример вывода:
```source[barbaz.com]
|___ dir[bar]
|    |___ dir[baz]
|         |___ file[File1.java]
|         |___ file[File3.java]
source[foobar.com]
|___ dir[foo]
|    |___ dir[bar]
|         |___ file[File1.java]
|         |___ file[File3.java]
|    |___ file[File2.java]
|    |___ file[File4.java]
|    |___ file[File4.java]```

Запуск скрипта на сервере: 
python file_tree.py files/
запуск диспетчера  
python mincemeat.py -p changeme [server address]
Адресс локальной машины можно узнать например с помощью socket.gethostbyname(socket.gethostname()).

Использована реализация mapreduce mincemeatpy [https://github.com/michaelfairley/mincemeatpy] и дерево pyTree [https://github.com/caesar0301/pyTree].
