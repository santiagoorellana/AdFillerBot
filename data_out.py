'''Interfaces de salida y envio de datos'''
__version__ = '1.0'
__author__ = 'Santiago Orellana Perez'

import datetime
import asyncio
from telegram import (ReplyKeyboardMarkup, Update)
from telegram.ext import (ContextTypes)
from const import *


INSISTENCE_COUNT_MAX = 10
INSISTENCE_PAUSE_SECONDS = 0.5


def sync_create_filename(dateTime):
    dateTime = datetime.datetime.now()
    date = dateTime.strftime('%Y-%m-%d')  
    return './dinamic-grid-bot-{}.log'.format(date)


def sync_to_file_cmd(msgType, msg):
    '''Escribe mensajes en un fichero y en consola. Si el fichero no existe, lo crea. Se crea un fichero para cada dia.'''
    try:
        dateTime = datetime.datetime.now()
        fileOut = open(sync_create_filename(dateTime), 'a')
        fileOut.write('{} {} {}\n'.format(str(dateTime), str(msgType), str(msg)))
        print(str(dateTime), str(msgType), str(msg))
        fileOut.close()
    except Exception as e:
        print(str(dateTime), 'ERROR', 'sync_to_file_cmd(): {}'.format(str(e)))

        
async def to_file(msgType, msg, dateTime=None):
    '''Escribe mensajes en un fichero. Si el fichero no existe, lo crea. Se crea un fichero para cada dia.'''
    try:
        if dateTime is None:
            dateTime = datetime.datetime.now()
        fileOut = open(sync_create_filename(dateTime), 'a')
        fileOut.write('{} {} {}\n'.format(str(dateTime), str(msgType), str(msg)))
        fileOut.close()
    except Exception as e:
        print(str(dateTime), 'ERROR', 'to_file(): {}'.format(str(e)))


async def to_cmd(msgType, msg, toFile=True):
    '''Escribe mensajes de reporte en la linea de comandos y en un fichero'''
    dateTime = datetime.datetime.now()
    try:
        if isinstance(msg, str):
            if toFile:
                await to_file(str(msgType), str(msg), dateTime)
            print(str(dateTime), str(msgType), str(msg))
        elif isinstance(msg, list):
            for line in msg:
                if toFile:
                    await to_file(str(msgType), str(line), dateTime)
                print(str(dateTime), str(msgType), str(line))
    except Exception as e:
        print(str(dateTime), 'ERROR', 'to_cmd(): Failed to print message. {}'.format(str(e)))
    else:
        return True
    return False


async def show_message(context, chat_id, message):
    '''Envia mensajes al chat e insiste en reenviar si se produce error. Devuelve True si logra enviar el mensaje.'''
    error = ''
    for i in range(INSISTENCE_COUNT_MAX):
        try:
            await context.bot.send_message(chat_id, message, parse_mode = 'HTML')
        except Exception as e:
            await asyncio.sleep(INSISTENCE_PAUSE_SECONDS)
            error = e
        else:
            return True
    await to_cmd('WARNING', 'show_message(): The message could not be sent to the chat. {}'.format(str(error)))
    return False


async def processOne(text):
    '''Se le pasa el número de teléfono y trata de corregirlo y completarlo.
    Patron para telefonos de Cuba, Fijos: +537xxxxxxx  Moviles: +535xxxxxxx
    '''
    phoneText = str(text).replace(' ', '')
    if len(phoneText) == 7: 
        return '+535' + phoneText   # Asume que es un celular porque los cubanos al fijo siempre le ponene el 7 delante.
    if len(phoneText) == 8:
        return '+53' + phoneText
    elif len(phoneText) == 9 and phoneText[0] == '3':   # Tiene que ser 3, porque en caso de ser cero, es el codigo antiguo.
        return '+5' + phoneText
    elif len(phoneText) == 10 and phoneText[0] == '5' and phoneText[1] == '3':
        return '+' + phoneText
    elif len(phoneText) > 10 and phoneText[0] != '+':
        return '+' + phoneText
    else:
        return phoneText


async def sequential_filter_numbers(phoneText):
    '''Filtra el texto de manera secuencial e inserta caracter / para separar los numeros.'''
    filtered = ''
    count = 0
    for i in range(len(str(phoneText))):
        if str(phoneText)[i].isdigit():
            filtered = filtered + phoneText[i]
            count += 1
        elif count > 7:
            filtered = filtered + '/'
            count = 0
    return filtered

    
async def get_phone_numbers(text):
    '''Se le pasa una cadena de texto y trata de encontrar los números de teléfono que contiene.'''
    phoneText = await sequential_filter_numbers(str(text))
    if len(phoneText) > 12:
        phonesList = phoneText.rsplit('/')
        if len(phonesList) > 1:                                 # Si se divide por el splitter...
            result = []
            for phone in phonesList:            
                if len(phone) > 6:                              # Verifica que cada parte tenga espacio para contener un número de teléfono.
                    result.append(await processOne(phone))
            if len(result) > 1:
                return result
    return [await processOne(phoneText)]


async def emoji_of_word(word):
    '''Devuelve el emoji correspondiente a la palabra'''
    key = word.lower().rstrip().lstrip()
    if key in SETVMAS_WORDS_EMOJIS:
        return SETVMAS_WORDS_EMOJIS[key]
    return ''


async def text_emojis(text, returnText=False):
    '''Devuelve el texto embellecido con emojis.'''
    result = ''
    wordList = str(text).rsplit(' ')
    for word in wordList:
        result = result + await emoji_of_word(word)
        if returnText:
            result = result + ' ' + word
    return result
    
    

async def show_messages_ad(context, listReceivers, adJSON):
    '''Envía a cada receptor los anuncios que le corresponden según su categoría.
    Embellece los anuncios colocandoles emojis y dándoles formato.
    '''
    if not 'ad' in adJSON:
        return False
    if adJSON['ad'] is not None:
        ad = adJSON['ad']
        await to_cmd('INFO', 'ad {}: {}'.format(ad['id'], ad['title']))
        msg = '{} <b>{}</b>\n'.format(await text_emojis(ad['title']), ad['title'])
        if ad['price'] is not None:
            msg = msg + '\n{} {} {}\n'.format(EMOJI_PRICE, ad['price'], ad['currency'])
        if ad['description'] != ad['title'] and len(ad['description']) > 3:
            extra = len(ad['description']) + len(msg) + 50 - 4096   # Telegram solo admite mensajes de 4096 caracteres.
            if extra >0:
                description = ad['description'][0:-1*extra]  # Limita los textos que son muy largos.
            else:
                description = ad['description']
            msg = msg + '\n{}\n'.format(description)
        if ad['name'] is not None:
            msg = msg + '\n{} <b>{}</b>'.format(EMOJI_NAME, ad['name'])
        if ad['phone'] is not None:
            phones = await get_phone_numbers(ad['phone'])
            if len(phones) > 0:
                for phoneNumber in phones:
                    msg = msg + '\n{} {}'.format(EMOJI_PHONE, phoneNumber)
            if len(phones) > 0 and int(ad['imagesCount']) > 0:
                for phoneNumber in phones:
                    if phoneNumber.startswith('+535'):
                        msg = msg + '\n{} <a href="wa.me/{}">WhatsApp</a>'.format(EMOJI_WHATSAPP, phoneNumber[1:])
            msg = msg + '\n\n{} {}'.format(EMOJI_LOCALIDAD, ad['provinceName'])
            if 'municipalityName' in ad:
                msg = msg + '-' + ad['municipalityName']
            if 'tags' in adJSON:
                if len(adJSON['tags']) > 0:
                    msg = msg + '\n{} {}'.format(EMOJI_TAG, ' '.join(adJSON['tags']))
            
        for receiver in listReceivers:
            category = receiver['category']
            sendAd = False
            try:
                if category in SETVMAS_CATEGORIES:
                    setvmasCategoriesID = list(SETVMAS_CATEGORIES[category]['revolico_categories_id'])
                    sendAd = int(ad['subcategoryID']) in setvmasCategoriesID or 0 in setvmasCategoriesID    # El cero es para enviar todos los anuncios.
            except Exception as e:
                await to_cmd('WARNING', 'show_messages_ad(): no send. {}'.format(str(e)))
                sendAd = False
            if sendAd:
                try:
                    if int(ad['imagesCount']) > 0:
                        await context.bot.send_photo(receiver['id'], ad['images'][0]['thumb'], caption=msg, parse_mode = 'HTML')
                    else:
                        await context.bot.send_message(receiver['id'], msg, parse_mode = 'HTML')
                except Exception as e:
                    await to_cmd('WARNING', 'the message could not be sent to {}. {}'.format(str(receiver['id']), str(e)))
        return True
    else:
        return False                



async def show_keyboard(context, chat_id, message, keyboard):
    '''Envia mensajes al chat e insiste en reenviar si se produce error. Devuelve True si logra enier el mensaje.'''
    error = ''
    for i in range(INSISTENCE_COUNT_MAX):
        try:
            await context.bot.send_message(chat_id, message, reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=False))
        except Exception as e:
            await asyncio.sleep(INSISTENCE_PAUSE_SECONDS)
            error = e
        else:
            return True
    await to_cmd('ERROR', 'show_keyboard(): The keyboard could not be show. {}'.format(str(error)))
    return False

# Esto es para probar la extrccion de numeros de telefonos.
import asyncio
numbers = [
    '54396358',
    '78702227',
    '+5354399509',
    '56597798-50100403',
    '53691387- 76385706',
    '53251255 o 53969232',
    '52735318 o 76491765',
    '[+53 56602668 WhatsApp (por favor)] [+53 50098934]',
    '52410480- 52732377',
    '52829510  - 54063115 - 72026504',
    '7 6416048    5 2969358',
    '+17077609573',
    '18138340280',
    '52711498 / 41996422',
    '5310-0843',
    '599999',
    '52078860 , 72906295',
    '52848007..76209533',
    '52746583 76905579',
    '54488048 ò 76454324',
    '+5377975961 y 53337448',
    ]
async def test_get_phone_numbers():
    for num in numbers:
        print('text:', num, 'numbers', await get_phone_numbers(num))
        
#asyncio.run(test_get_phone_numbers())
