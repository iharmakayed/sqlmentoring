# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
from datetime import datetime
import shutil
import bs4 as bs
import io
import string
import sqlite3



class Database():
    def __init__(self):
        self_info = 'Info'

    def clean_db(self, *args):
        try:
            conn = sqlite3.connect('files_data.db')
            for arg in args:
                conn.execute('DELETE FROM '+ arg + ';')
            conn.execute('commit')
            conn.close()
        except:
            print('data not deleted. error occurred')

    def get_data(self, tablename, limit, *columns):
        try:
            query = 'select '
            if columns[0] in ('', 'all', '*'):
                query += ' * from ' + tablename
            else:
                cols = ', '.join(columns)
                query += cols + ' from ' + tablename

            if limit == 'all' or limit == '':
                query += ' ;'
            else:
                query += ' limit ' + str(limit) + ' ;'

            conn = sqlite3.connect('files_data.db')
            get_data = conn.execute(query)

            for row in get_data:
                print(row)

            conn.close()
        except:
            print('error occurred')

    def drop_tables(self, *tables):
        try:
            conn = sqlite3.connect('files_data.db')
            for table in tables:
                conn.execute('DROP TABLE IF EXISTS '+ table + ';')
                print(table + ' dropped if existed.')
            conn.close()
        except:
            print('data not deleted. error occurred')

    def show_tables(self):
        try:
            conn = sqlite3.connect('files_data.db')
            get_data = conn.execute("SELECT name FROM sqlite_master  WHERE type = 'table' AND  name NOT LIKE 'sqlite_%' ;")

            for row in get_data:
                print(row)

            conn.close()
        except:
            print('can\'t show data. error occurred')

    def create_tables(self, talbename_1, tablename_2):
        try:
            conn = sqlite3.connect('files_data.db')
            conn.execute("""
                            create table if not exists """ + talbename_1.upper() + """
                                ( 
                                file_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                file_name text not null,
                                book_name text not null,
                                number_of_paragraph integer,
                                number_of_words integer,
                                number_of_letters integer,
                                words_with_capital_letters integer,
                                words_in_lowercase integer,
                                date_insert varchar                       
                                );    
                        """)

            conn.execute(
                """
                    create table if not exists """ + tablename_2.upper() + """
                        (
                        file_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        file_name text not null,
                        book_name text not null,
                        word text,
                        count integer,
                        count_uppercase integer,
                        date_insert varchar
                        );
    
                """

            )
            conn.close()
        except:
            print('error_occurred')

    def show_columns(self, *tablenames):
        try:
            conn = sqlite3.connect('files_data.db')
            for tablename in tablenames:
                data = conn.execute('PRAGMA table_info(' + tablename + ')')
                for line in data:
                    print(line[1])
        except:
            print('error occurred')

class Files():

    def __init__(self):
        self.info = 'Info on class'


    def create_dirs(self, path, *dirnames):
        try:
            for name in dirnames:

                if not os.path.exists(path+name):
                    os.mkdir(path+name)
                    print("Directory ", path+name, " Created ")
                else:
                    print("Directory ", path+name, " already exists")
        except:
            print('error occurred')

    def delete_dirs(self, path, *dirnames):
        try:
            for name in dirnames:

                if not os.path.exists(path + name):

                    print("Directory ", path + name, " not exists ")
                else:
                    # deletes folder with files in it:
                    shutil.rmtree(path + name)

                    # deletes only empty folders:
                    #os.rmdir(path + name)
                    print("Directory ", path + name, " removed with files in it if any.")
        except:
            print('error occurred')



    def move_files(self, path, item, dirname):
        try:
            if not os.path.exists(path + dirname):
                print("Directory ", path + dirname, " not exists ")
            else:
                if item.is_file():
                    dst = path + dirname + '/' + item.name
                    # print(dst)
                    shutil.move(item, dst)
                    print(item.name, ' was moved to ', path, dirname)
        except:
            print('error occurred')


class Book():

    def __init__(self, path, processed_files_dir = 'processed_files', incorrect_files_dir = 'incorrect_input', format = '.fb2', \
                 table_stat = 'files_stat', table_words = 'words_stat', logs_dir = 'logs', logs_file = 'logs.txt' ):
        self.path = path
        self.info = 'Info on book'
        self.processed_files_dir = processed_files_dir
        self.incorrect_files_dir = incorrect_files_dir
        self.format = format
        self.table_stat = table_stat
        self.table_words = table_words
        self.logs_dir = logs_dir
        self.logs_file = logs_file


    def word_count(self, str):
        counts = {}

        #dict()
        words = str.split()

        for word in words:

            if word in counts:
                counts[word]["counts"] += 1
                if word[0].isupper():
                    counts[word]["count_upper"] += 1
            else:
                detail = {}
                detail["counts"] = 1
                if word[0].isupper():
                    detail["count_upper"] = 1
                counts[word] = detail

        return counts



    # def files_listing(self):
    #     def convert_date(timestamp):
    #         d = datetime.utcfromtimestamp(timestamp)
    #         formated_date = d.strftime('%d %b %Y')
    #         return formated_date
    #
    #     with os.scandir(self.path) as entries:
    #         for entry in entries:
    #             if entry.is_file():
    #                 info = entry.stat()
    #                 print(f'{entry.name}\t Last Modified: {convert_date(info.st_mtime)}')

    def files_shuffle(self):

        file1 = Files()
        file1.create_dirs(self.path, self.processed_files_dir, self.incorrect_files_dir)

        with os.scandir(self.path) as entries:
            for entry in entries:
                if entry.is_file():
                    if not entry.name.endswith(self.format):
                        print(f'{entry.name}\t is wrong format file.')
                        file1.move_files(self.path, entry, self.incorrect_files_dir)


    def read_file(self, entry):

        print(entry.is_dir())

        info_item = {}
        info_item["filename"] = entry.name

        with io.open(self.path+entry.name, encoding='utf-8', mode='r') as f:
            soup = bs.BeautifulSoup(f, 'lxml')

            print('########')

            title = []

            for tag in soup.find_all('book-title'):
                title.append(tag.get_text())

            info_item["title"] = " ".join(title)

            cnt_paragraphs = 0
            for tag in soup.find_all('p'):
                cnt_paragraphs += 1

            info_item["paragraphs"] = cnt_paragraphs

            cnt_letters = 0
            for sign in soup.body.text:
            #for sign in soup.find('body').get_text():
                if sign not in string.digits and sign not in string.punctuation and sign not in string.whitespace:
                    cnt_letters += 1

            info_item["letters"] = cnt_letters

            words = soup.body.text.split()
            #words = soup.find('body').get_text().split()
            count_words = 0
            count_lowercase = 0
            count_uppercase = 0

            for word in words:
                # for cyrillic and latin alphabet only
                if (ord(word[0]) >= 65 and ord(word[0]) <= 90) or \
                    (ord(word[0]) >= 97 and ord(word[0]) <= 122) or \
                        (ord(word[0]) >= 1040 and ord(word[0]) <= 1103):
                    count_words += 1
                    if word[0].isupper():
                        count_uppercase += 1
                    elif word[0].islower():
                        count_lowercase += 1

                # for " ' « and words in them
                if ord(word[0]) == 34 or ord(word[0]) == 39 or ord(word[0]) == 171:
                    if len(word) >= 3:
                        count_words += 1
                        if word[1].isupper():
                            count_uppercase += 1
                        elif word[1].islower():
                            count_lowercase += 1


            info_item["words"] = count_words
            info_item["words_uppercase"] = count_uppercase
            info_item["words_lowercase"] = count_lowercase


            word_counts = self.word_count(soup.body.text)
            #word_counts = self.word_count(soup.find('body').get_text())

            info_item['word_counts'] = word_counts


        return info_item




    def load_to_csv(self, data):

        db1 = Database()
        db1.create_tables(self.table_stat, self.table_words)

        conn = sqlite3.connect('files_data.db')


        conn.execute("""
                    insert into """ + self.table_stat.upper() + """ (file_name, book_name, number_of_paragraph, number_of_words, 
                                                number_of_letters, words_with_capital_letters, words_in_lowercase,
                                                date_insert)
                    values(            
                    """ + str('"'+data["filename"]+'"') + ', ' + str('"'+data["title"]+'"') + ', ' + str(data["paragraphs"]) + ', ' + str(data["words"]) + ', ' \
                     + str(data["letters"]) + ', ' + str(data["words_uppercase"]) + ', ' + str(data["words_lowercase"])  \
                     + ", strftime('%Y-%m-%d %H-%M','now') );"

        )

        for item in data["word_counts"]:
            conn.execute("""
                        insert into """ + self.table_words.upper() + """ (file_name, book_name, word, count, count_uppercase, date_insert)
                        values(
                        """ + str('"'+data["filename"]+'"') + ', ' + str('"'+data["title"]+'"') + ', ' + str('"'+item+'"') + ', ' \
                         + str(data["word_counts"][item]["counts"]) + \
                          ', ' + str(data["word_counts"][item].get("count_upper",0)) + ", strftime('%Y-%m-%d %H-%M','now') );"
            )

        conn.execute('commit;')
        conn.close()

    def process_files(self):

        file1 = Files()
        file1.create_dirs(self.path, self.processed_files_dir, self.incorrect_files_dir, self.logs_dir)
        self.files_shuffle()

        with os.scandir(self.path) as entries:
            for entry in entries:
                if not entry.is_dir():
                    data = self.read_file(entry)
                    self.load_to_csv(data)
                    file1.move_files(self.path, entry, self.processed_files_dir)
                    #with open(os.path.join('logs', 'logs.txt'), encoding='utf-8', mode='a') as logs:
                    with open(self.path + '/' + self.logs_dir + '/' + self.logs_file, encoding='utf-8', mode='a') as logs:
                        logs.write('File ' + entry.name + ' processed ' + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + '\n')


book1 = Book('path_folder/')
book1.process_files()
db1 = Database()
# db1.show_tables()
db1.get_data('files_stat', 10, 'all')
db1.get_data('words_stat', 10, 'all')
# db1.drop_tables('files_stat', 'words_stat')
# file1 = Files()
# file1.delete_dirs('path_folder/', 'aa')

#book1.files_shuffle()

#book1.load_to_csv('files_stat', 'words_stat')

#book1.load_to_csv()
#book1.clean_db()

#book1.get_data()

# db1 = Database()
# #db1.get_data('FILES_PROCESSED_WORDS', 10, 'all')
# db1.show_tables()
# db1.drop_tables('files_stat', 'words_stat')
# db1.show_tables()



