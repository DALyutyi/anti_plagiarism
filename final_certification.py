# для работы с русским текстом необходимо установить pymorphy2
!pip install pymorphy2

# для сравнения расстояния между последовательностями установим библиотеку textdistance
!pip install textdistance

# импортируем неободимые библиотеки
import re
import os
from pymorphy2 import MorphAnalyzer
import nltk
import textdistance
import glob
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

# загрузим необхоимые компоненты nltk
nltk.download('punkt')      # для токенизации
nltk.download('stopwords')  # для фильтрации на стоп-лова

# определим функцию проводящую токенизации и лемматизации текста, которая возвращет список из слов
def get_words_tok(text):
  tokenized = list()
  morph = MorphAnalyzer()
  word_text = nltk.word_tokenize(text)
  for i in word_text:
    txt = re.findall(r"[а-яё]+", i.lower())
    for j in txt:
      if j not in stopwords.words("russian") and len(j) > 2:
        tokenized.append(morph.parse(j)[0].normal_form)
  return tokenized

# определим функцию проводящую токенизации и лемматизации текста, которая возвращает список из предложений
def get_sent_tok(text):
  tokenized = list()
  morph = MorphAnalyzer()
  sent_text = nltk.sent_tokenize(text)
  for i in sent_text:
    tok_sen = []
    txt = re.findall(r"[а-яё]+", i.lower())
    for j in txt:
      if j not in stopwords.words("russian") and len(j) > 2:
        tok_sen.append(morph.parse(j)[0].normal_form)
    tokenized.append(" ".join(tok_sen))
  return tokenized

# определим функцию для чтения файла
def get_file(link):
  with open(link, "r", encoding="utf-8") as file:
    return file.read()

# оперделим функию для сохранения файла
"""
функция имеет один именованный параметр flag, 
в случае если передать в функцию аргумент flag=True на первой строке файла добавится
информация о сходстве данного файла с файлом из нашей базы_даных_курсовых_работ
функция универсальна и может сохранять как список так и строку
"""
def save_file(link, text, flag=False):
  with open(link, "w", encoding="utf-8") as file:
    if flag:
      file.write(f"содержит {result[1]}% сходства с работой '{file_name_2}'\n")
    if type(text) is list:
      for i in text:
        file.write(i)
        file.write(" ")
    else:
      file.write(text)


# определим функцию проверки на плагиат
"""
В функции присутсвтует 4 вида метрик для определния сходства между текстами.
Мы будем использовать косинусное сходство
"""
def get_plagiarism(text_1, text_2):
  cosine = textdistance.cosine(text_1, text_2)
  # bag = textdistance.bag(text_1, text_2)
  # levenshtein = textdistance.levenshtein(text_1, text_2)
  # jaccard = textdistance.jaccard(text_1, text_2)
  # данный критерий можно ужесточить и возвращать True при меньшем сходстве
  return cosine > 0.30, round(cosine * 100)


# для начала обработаем каждый текст и приведём его в читабельный для машины вид
# данная операция выполняется единожды для побработки  первого файла, далее программа будет обращаться к папку обработанные_работы
way_to_files = glob.glob("/content/drive/MyDrive/programming/МЭО/Lessons/итоговая_аттестация/база_данных_курсовых_работ/*.txt")


# посмотрим верно ли отработал glob
way_to_files


# проведем предобработку текстов базы курсовых работ
for way in way_to_files:
  text = get_file(way)
  text = get_words_tok(text)
  
  # чтобы не менять исходные файлы, сохраним предобработанные файлы в другрую директорию
  new_way = f"/content/drive/MyDrive/programming/МЭО/Lessons/итоговая_аттестация/обработанные_работы{way[way.rfind('/'):]}"
  save_file(new_way, text)

# теперь прочитаем наш проверяемый текст
# напишем код, который сможет проверять, если это необходимо несколько текстов.
links_1 = glob.glob("/content/drive/MyDrive/programming/МЭО/Lessons/итоговая_аттестация/проверяемые_работы/*.txt")
for link_1 in links_1:
  # прочитаем проверяемый файл
  text_check = get_file(link_1)

  # токенизируем его
  text_1 = get_words_tok(text_check)

  # имя первого файла для удобства
  file_name_1 = f"{link_1[link_1.rfind('/')+1:]}"

  # если в папку обработанные_работы добавятся новые файлы, то при заходе на внутренний цикл нужно заново получить ссылку на файлы этой папки
  links_2 = glob.glob("/content/drive/MyDrive/programming/МЭО/Lessons/итоговая_аттестация/обработанные_работы/*.txt")
  # список в котором хранятся порядковые номера файлов
  count_file = list(map(lambda x: str(x)[x.rfind("/") + 1:x.find(".")], links_2))

  for link_2 in links_2:
    # имя второго файла для удобства
    file_name_2 = f"{link_2[link_2.rfind('/')+1:]}"
    # прочитаем файл из базы данных в список слов
    text_2 = get_file(link_2).split()
    # сравним два файла
    result = get_plagiarism(text_1, text_2)
    # если файлы схожи ,более чем на 30%  файл считается плагиатом
    if result[0]:
      print(f"""Обнаружен плагиат!
Проверяемая работа '{file_name_1}' содержит {result[1]}% сходства с работой '{file_name_2}'
Исходный файл перемещён в папку 'плагиат'""")
      save_file(f"/content/drive/MyDrive/programming/МЭО/Lessons/итоговая_аттестация/плагиат/{file_name_1}", text_check, flag=True)
      os.remove(link_1)
      break
  # необязательный оператор условный else цикла for. В случае не штатного завершения цикла, оператор не сработает
  else:
    """
    получаем новое имя файла для сохранения на диск. для этого используем:
    * max() для поиска наибольшего порядкового номера
    * map() для изменения значения строки на целое списка count_file
    * lambda меняет это значение
    """
    new_file_name = f"{max(map(lambda x: int(x), count_file)) + 1}.{link_1[link_1.rfind('/')+1:]}"
    link_3 = "/content/drive/MyDrive/programming/МЭО/Lessons/итоговая_аттестация/база_данных_курсовых_работ/"
    print(f"""Плагиат не обнаружен!
Исходный файл '{file_name_1}' удалён из папки 'проверяемые_работы' и сохранён в папке 'база_данных_курсовых_работ'
Предобработанный файл '{new_file_name}' сохранён в папке 'обработанные_работы'""")
    save_file(f"{link_3}{new_file_name}", text_check)
    save_file(f"{link_2[:link_2.rfind('/')]}/{new_file_name}", text_1)
    os.remove(link_1)

 