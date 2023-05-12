#!/usr/bin/env python
# coding: utf-8

# # Лабораторная работа №4, Вариант №5, ИВТ-3, 2 курс, Мартынов В.В.

# <h3>Задание №1</h3>
# <p>Напишите скрипт, читающий во всех mp3-файлах указанной
# директории ID3v1-теги и выводящий информацию о каждом файле в
# виде: [имя исполнителя] - [название трека] - [название альбома].
# Если пользователь при вызове скрипта задает ключ -d, то выведите
# для каждого файла также 16-ричный дамп тега. Скрипт должен
# также автоматически проставить номера треков и жанр (номер
# жанра задается в параметре командной строки), если они не
# проставлены. Используйте модуль struct.
# ID3v1-заголовки располагаются в последних 128 байтах mp3-файла.
# Структура заголовка отражена в табл. 2.</p>
# 
# <hr>
# 
# <table>
#     <tr>
#         <th>Поле</th>
#         <th>Длина (байт)</th>
#         <th>Описание</th>
#     </tr>
#     <tr>
#         <td>header</td>
#         <td>3</td>
#         <td>3 символа: "TAG"</td>
#     </tr>
#     <tr>
#         <td>title</td>
#         <td>30</td>
#         <td>30 символов названия трека</td>
#     </tr>
#     <tr>
#         <td>artist</td>
#         <td>30</td>
#         <td>30 символов имени исполнителя</td>
#     </tr>
#     <tr>
#         <td>album</td>
#         <td>30</td>
#         <td>30 символов названия альбома</td>
#     </tr>
#     <tr>
#         <td>year</td>
#         <td>4</td>
#         <td>4 символа года издания</td>
#     </tr>
#     <tr>
#         <td>comment</td>
#         <td>28 ил 30</td>
#         <td>Комментарий</td>
#     </tr>
#     <tr>
#         <td>zero-byte</td>
#         <td>1</td>
#         <td>Если в теге хранится номер трека, то этот байт
# зарезервирован под 0.</td>
#     </tr>
#     <tr>
#         <td>track</td>
#         <td>1</td>
#         <td>Номер трека альбома или 0. Имеет смысл, если
# предыдущий байт равен 0</td>
#     </tr>
#     <tr>
#         <td>genre</td>
#         <td>1</td>
#         <td>Индекс в списке жанров или 255.</td>
#     </tr>
# </table>
# 
# <hr>

# In[1]:


import os
import struct
import re
import sys

def read_id3v1_tag(file_path):
    with open(file_path, 'rb') as f:
        f.seek(-128, 2)
        tag_bytes = f.read(128)

    splited_tag_code = list(struct.unpack('>3s30s30s30s4s28sbBB', tag_bytes))
        
    if splited_tag_code[0] != b'TAG':
        print(f"False tag: {tag_bytes[:3]}")
        return None
    
    title = (splited_tag_code[1].replace(b'\x00', b'')).decode('utf-8')
    artist = (splited_tag_code[2].replace(b'\x00', b'')).decode('utf-8')
    album = (splited_tag_code[3].replace(b'\x00', b'')).decode('utf-8')
    year = (splited_tag_code[4].replace(b'\x00', b'')).decode('utf-8')
    comment = (splited_tag_code[5].replace(b'\x00', b'')).decode('utf-8')
    is_num_tag = splited_tag_code[6]
    num_track = splited_tag_code[7]
    genre = splited_tag_code[8]
    
    return {
        'title': title,
        'artist': artist,
        'album': album,
        'year': year,
        'comment': comment,
        'is_num_tag': is_num_tag,
        'num_track': num_track,
        'genre': genre
    }, tag_bytes

def write_tags(file_path, tag):
    with open(file_path, 'rb+') as f:
        f.seek(-128, 2)
        
        struct_data = struct.pack('>128s',
                        b'TAG' +
                        tag['title'].encode('utf-8').ljust(30, b'\x00') + 
                        tag['artist'].encode('utf-8').ljust(30, b'\x00') +
                        tag['album'].encode('utf-8').ljust(30, b'\x00') +
                        tag['year'].encode('utf-8').ljust(4, b'\x00') +
                        tag['comment'].encode('utf-8').ljust(28, b'\x00') +
                        bytes([0]) +
                        bytes([tag['num_track']]) +
                        bytes([tag['genre']]))
        
        f.write(struct_data)
                
def auto_fix_tag(file_path, genre_number, num_of_track):
    tag, _ = read_id3v1_tag(file_path)

    if tag is None:
        return False

    if not bool(re.match("[A-Za-z0-9]", tag['title'])):
        tag['title'] = 'Unknown Title'
    
    if not bool(re.match("[A-Za-z0-9]", tag['artist'])):
        tag['artist'] = 'Unknown Artist'
    
    if not bool(re.match("[A-Za-z0-9]", tag['album'])):
        tag['album'] = 'Unknown Album'
        
    if not bool(re.match("[A-Za-z0-9]", tag['comment'])):
        tag['comment'] = "No comments"

    if int(tag['num_track']) == 0:
        tag['num_track'] = num_of_track

    if tag['genre'] == 255:
        tag['genre'] = genre_number
        
    write_tags(file_path, tag)
    
    return True

def print_info(tag):
    print(f'\n New music found!')
    print('{0} - {1} - {2}'.format(tag['artist'], tag['title'], tag['album']))
    
#     Test print GENRE and NUM to debug
#     print('{0} - {1} - {2} - GENRE[{3}] - NUM[{4}])'.format(tag['artist'], tag['title'], tag['album'], tag['genre'], tag['num_track']))

def mainFunc(argv):
    
    cmd_commands = ['-dir', '-g']
    
    sorted_argum = [f'{str(os.getcwd())}', 1]
        
    for i in range(1, len(argv)):
        for j in range(len(cmd_commands)):
            if argv[i] == cmd_commands[j]:
                sorted_argum[j] = (type(sorted_argum[j]))(argv[i+1])
                break
    
    source = sorted_argum[0]
    genre_number = sorted_argum[1]
    dump = False
    
    if '-d' in argv:
        dump = True
    
    num_of_track = 0
    
    for file_name in os.listdir(source):
        if not file_name.lower().endswith('.mp3'):
            continue
            
        num_of_track += 1
            
        file_path = os.path.join(source, file_name)
        
        is_exist = auto_fix_tag(file_path, genre_number, num_of_track)
        
        if not is_exist:
            print('No tag in the file!')
            break
        
        tag, saved_dump = read_id3v1_tag(file_path)
        print_info(tag)

        if dump:
            print(f'\nDUMP: {saved_dump}')

if __name__ == '__main__':

#     Test in ipynb
#     argv_ex = ['name.py', '-dir', 'C:\\', '-d', '-g', 5]
#     mainFunc(argv_ex)

    mainFunc(sys.argv)

