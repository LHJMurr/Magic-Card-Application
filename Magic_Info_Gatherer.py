import requests
import json
import threading
import time
import pandas as pd
import tkinter as tk

def cleanColors(colors):
    cleanColors = []
    for color in colors:
        if color == 'W':
            cleanColors.append('White')
        elif color == 'U':
            cleanColors.append('Blue')
        elif color == 'B':
            cleanColors.append('Black')
        elif color == 'R':
            cleanColors.append('Red')
        elif color == 'G':
            cleanColors.append('Green')
        elif colors == '':
            cleanColors.append('Colorless')
        else:
            cleanColors.append(color)
    return ' '.join(cleanColors)

def cleanCardType(cardTypeLine):
    typeWords = cardTypeLine.split(' ')
    parsedType = []
    # Remove dash if present
    while '—' in typeWords:
        typeWords.remove('—')
    # Determine Legend Status
    if 'Legendary' in typeWords:
        isLegendary = 'Legendary '
        typeWords.remove('Legendary')
    else:
        isLegendary = ''
    # Determine Creature Type
    if 'Creature' in typeWords:
        while len(typeWords) != 0:
            word = typeWords.pop(0)
            parsedType.append(word)
    for word in typeWords:
        if word == 'Instant':
            parsedType.append('Instant')
        elif word == 'Sorcery':
            parsedType.append('Sorcery')
        elif word == 'Enchantment':
            parsedType.append('Enchantment')
        elif word == 'Artifact':
            parsedType.append('Artifact')
        elif word == 'Planeswalker':
            parsedType.append('Planeswalker')
        elif word == 'Land':
            parsedType.append('Land')

    return isLegendary + ' '.join(parsedType)

def loadCards(cardslist, filename = 'cardlist'):
    with open(filename) as file:
        alpha = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ,./;:-' "
        cards = []
        for line in file:
            card = ''
            for letter in line:
                if letter in alpha:
                    card += letter
            if card[-1] == ' ': # Cut Hanging Spaces
                card = card[:-1]
            cardslist.append(card)

def get_card_info(cardname, queue = [], err = []):
    payload = {'fuzzy': cardname}
    API = requests.get('https://api.scryfall.com/cards/named', payload)
    API_json = json.loads(API.text)
    queue.append(API_json)
    if API_json['object'] == 'error':
        err.append(cardname)

def json_info(API_json):
    try:
        OfficialName = API_json['name']
    except:
        OfficialName = ''
    try:
        cardTypeLine = API_json['type_line']
        cleanTypeLine = cleanCardType(cardTypeLine)
    except:
        cleanTypeLine = ''
    try:
        cardCMC = API_json['cmc']
    except:
        cardCMC = ''
    try:
        cardColors = API_json['color_identity']
        cleanColorList = cleanColors(cardColors)
    except:
        cleanColorList = ''
    try:
        TCG_Price = API_json['prices']['usd']
    except:
        TCG_Price = ''
    try:
        rarity = API_json['rarity']
    except:
        rarity = ''
    try:
        cardImage = API_json['image_uris']['png']
    except:
        cardImage = ''
    try:
        cardSet = API_json['set']
    except:
        cardSet = ''

    collectedInformation = [OfficialName, cleanColorList, rarity, cardCMC, cleanTypeLine, TCG_Price, cardSet,
                            cardImage, len(cleanColorList.split(' '))]
    return collectedInformation

def add_info(dictionary, info):
    count = 0
    for key in dictionary.keys():
        dictionary[key].append(info[count])
        count += 1

def make_collection(cardlist, in_progress = True):
    # Clear and create a new CSV file
    output_dict = {
        'Name':[],
        'Colors':[],
        'Rarity':[],
        'CMC':[],
        'Type':[],
        'Price':[],
        'Set':[],
        'Image Link':[],
        'NumColors':[]
    }
    # Start download threads
    cardlist_json = []
    errors = []
    threads = []
    for card in cardlist:
        t = threading.Thread(target=get_card_info, args=(card,cardlist_json, errors))
        threads.append(t)
        t.start()

    added_cards = []
    if in_progress:
        # Parse cards while downloading
        Done = False
        while not Done:
            try:
                card = cardlist_json.pop(0)
                to_add = json_info(card)
                add_info(output_dict, to_add)
                #print(f"\tAdded Card {card['name']}")
                added_cards.append(card['name'])
            except:
                for thread in threads:
                    if thread.is_alive():
                        thread.join()
                        break
            flag = False
            for thread in threads:
                if thread.is_alive() or cardlist_json != []:
                    flag = True
                    break
            if flag == False:
                Done = True

    if not in_progress:
        # Wait for cards to download then Parse
        for thread in threads:
            thread.join()
        # Once download is complete, parse each card
        for card in cardlist_json:
            to_add = json_info(card)
            add_info(output_dict, to_add)
            try:
                #print(f"\tAdded Card {card['name']}")
                added_cards.append(card['name'])
            except:
                pass
    return output_dict, errors

def make_csv(dict, outname = 'Magic_Card_Collection.csv', filters = ['NumColors','Colors','CMC','Rarity']):
    # Create a dataframe object
    df = pd.DataFrame(dict)
    df.sort_values(by='Name', ascending=True, inplace=True) # Alphabetize
    df.sort_values(by=filters, inplace=True)
    df.set_index('Name', inplace=True)
    df.drop(columns=['NumColors'], inplace=True)
    df.to_csv(outname)

def run(outname, cardslist, feedback):
    start = time.perf_counter()
    added, errors = make_collection(cardlist=cardslist, in_progress=True)
    end = time.perf_counter()

    make_csv(added, outname=outname)

    # Tkinter feedback label
    try:
        feedback_label.destroy()
    except:
        pass
    finally:
        feedback_label = tk.Label(feedback, text=f'Added cards to {outname}\nErrors found in cards {errors}')
        feedback_label.grid(row=0, column=0, padx=5, pady=5)

if __name__ == '__main__':
    run(outname = 'franscards.csv', filename = 'f_cards')