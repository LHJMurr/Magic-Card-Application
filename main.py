import tkinter as tk
import cv2 as cv
from PIL import Image, ImageTk
import time
import os
import csv
from pytesseract import pytesseract
import Magic_Info_Gatherer
import Scan_Functions


# For testing:
# C:\Users\gamer\PycharmProjects\MITAI\Magic Cards\f_cards.txt
# C:\Users\gamer\PycharmProjects\MITAI\Magic Cards\franscards.csv
# C:\Users\gamer\PycharmProjects\MagicCardApplication\Test_Directory\TestDatabase.csv

# Window Functions
def home_window():
    ''' Create the home window '''
    global root_image
    global scan_button
    global manual_button
    global help_button
    global view_button
    global clear_button
    global create_button
    global status_label
    # The first window
    home_window = tk.Tk()
    home_window.title('Magic Card Databaser v1.0')
    home_window.iconbitmap('Text and Images/Logo.ico')
    home_window.resizable(False, False)

    # Add image header
    root_image = ImageTk.PhotoImage(Image.open('Text and Images/Root_Image.png'))
    image_label = tk.Label(home_window, image=root_image)
    image_label.grid(row=0, column=0, columnspan=3, padx=30, pady=30)

    # Add manually or scan / help button / card management buttons
    scan_button = tk.Button(home_window, text='Add Cards from Scan', bd=5, relief='raised', padx=30, pady=5, command=scan_window)
    manual_button = tk.Button(home_window, text='Add Cards from File', bd=5, relief='raised', padx=30, pady=5, command=file_window)
    help_button = tk.Button(home_window, text='How to Use this App', bd=5, relief='raised', padx=30, pady=5, command=help_window)
    view_button = tk.Button(home_window, text='View Added Cards', bd=5, relief='raised', padx=30, pady=5, command=view_window)
    clear_button = tk.Button(home_window, text='Clear Added Cards', bd=5, relief='raised', padx=30, pady=5, command=clear_window)
    create_button = tk.Button(home_window, text='Create Database', bd=5, relief='raised', padx=30, pady=5, command=create_window)
    # Place Buttons
    scan_button.grid(row=1, column=0, padx=10, pady=5)
    manual_button.grid(row=1, column=1, padx=10, pady=5)
    help_button.grid(row=1, column=2, padx=10, pady=5)
    view_button.grid(row=2, column=0, padx=10, pady=5)
    clear_button.grid(row=2, column=1, padx=10, pady=5)
    create_button.grid(row=2, column=2, padx=10, pady=5)
    # Check is home window is closed and destroy all windows if so
    home_window.protocol('WM_DELETE_WINDOW', home_window.destroy)

    tk.mainloop()

def help_window():
    ''' Function for opening the help window '''
    disable_main_buttons()
    # Create help window
    help_window = tk.Toplevel()
    help_window.iconbitmap('Text and Images/Logo.ico')
    help_window.resizable(False, False)
    # Add the page content
    headers = ['What is this App?', 'How to Use','Adding from a File', 'Adding from a Scan']
    section_files = ['Text and Images/help_text_1.txt','Text and Images/help_text_4.txt',
                     'Text and Images/help_text_2.txt','Text and Images/help_text_3.txt']
    row_count = 0
    for i in range(len(headers)):
        add_section(headers[i], section_files[i], help_window, row_count)
        row_count += 2
    # Check if the window was closed. If so, close it and enable buttons again.
    help_window.protocol("WM_DELETE_WINDOW", lambda: enable_main_buttons(help_window))

def view_window():
    ''' Function for opening the view window '''
    global added_cards
    global view_index
    disable_main_buttons()
    # Create help window
    view_window = tk.Toplevel()
    view_window.iconbitmap('Text and Images/Logo.ico')
    view_window.resizable(False, False)
    # Header
    header = tk.Label(view_window, text='Added Cards', font=('Helvetica', 20, 'bold'))
    header.grid(row=0, column=0, columnspan=3, padx=10)
    # Card Frame
    card_frame = tk.Frame(view_window)
    # Add Cards
    batched_lists = list(batch(added_cards, 20))
    view_arrays = list(batch(batched_lists, 5))
    if view_arrays == []: # Empty Added Cards
        view_arrays = [[[]]] # Empty Tensor
    view_index = 0
    card_frame.grid(row=1, column=1)
    # Forwards and back buttons
    forwards = tk.Button(view_window, text = '>', padx=10, pady=5, relief='raised', bd=5,
                         command=lambda: forwards_view_button(view_arrays, card_frame, forwards, backwards))
    backwards = tk.Button(view_window, text = '<', padx=10, pady=5, relief='raised', bd=5,
                          command=lambda: backwards_view_button(view_arrays, card_frame, forwards, backwards))
    backwards['state'] = tk.DISABLED # Start at index = 0
    # Check usability
    if len(view_arrays) <= 1:
        forwards['state'] = tk.DISABLED
    display_cards(view_arrays[0], card_frame)  # Initial Frame

    forwards.grid(row=2, column=2, padx=3, pady=3)
    backwards.grid(row=2, column=0, padx=3, pady=3)

    # Check if the window was closed. If so, close it and enable buttons again.
    view_window.protocol("WM_DELETE_WINDOW", lambda: enable_main_buttons(view_window))

def clear_window():
    ''' Function for opening the clear window '''
    global added_cards
    global clear_feedback
    disable_main_buttons()
    # Create help window
    clear_window = tk.Toplevel()
    clear_window.iconbitmap('Text and Images/Logo.ico')
    clear_window.resizable(False, False)
    # Add a header anf labelframe
    header = tk.Label(clear_window, text='Clear Added Cards', font=('Helvetica', 20, 'bold'))
    header.grid(row=0, column=0, columnspan=1)
    clear_frame = tk.LabelFrame(clear_window, text='')
    clear_frame.grid(row=1, column=0, pady=5)
    # Option to selectivly clear cards by name
    card_entry = tk.Entry(clear_frame)
    card_entry.grid(row=0, column=0, pady=5, padx=10)
    clear_selected = tk.Button(clear_frame, text='Clear Selected', bd=5, relief='raised', padx=30, pady=5,
                               command=lambda: clear_entered_card(card_entry.get()))
    clear_selected.grid(row=1, column=0, pady=5, padx=10)

    # Option to clear all cards
    clear_all = tk.Button(clear_frame, text='Clear All', bd=5, relief='raised', padx=30, pady=5, command=clear_added)
    clear_all.grid(row=2, column=0, pady=5, padx=10)

    # User Feedback Label
    clear_feedback = tk.Label(clear_window, text='Card(s) Cleared!')

    # Check if the window was closed. If so, close it and enable buttons again.
    clear_window.protocol("WM_DELETE_WINDOW", lambda: enable_main_buttons(clear_window))

def file_window():
    ''' Function for opening the file window '''
    global added_cards
    disable_main_buttons()
    # Create help window
    file_window = tk.Toplevel()
    file_window.iconbitmap('Text and Images/Logo.ico')
    file_window.resizable(False, False)
    # Add Header
    header = tk.Label(file_window, text='Add Cards from File', font=('Helvetica', 20, 'bold'))
    header.grid(row=0, column=0, columnspan=1, padx=10)

    # Add a error frame for user feedback
    error_frame = tk.Frame(file_window)

    # Add a filename selector and a add button as well as a frame
    file_frame = tk.LabelFrame(file_window, text='Select File')
    filename_entry = tk.Entry(file_frame)
    add_button = tk.Button(file_frame, text='Add from File', bd=5, relief='raised', padx=30, pady=5,
                           command=lambda: from_file(filename_entry.get(), added_cards, error_frame))
    filename_entry.grid(row=0, column=0, pady=5)
    add_button.grid(row=1, column=0, padx=5, pady=5)
    file_frame.grid(row=1, column=0, pady=10)

    # Check if the window was closed. If so, close it and enable buttons again.
    file_window.protocol("WM_DELETE_WINDOW", lambda: enable_main_buttons(file_window))

def create_window():
    ''' Function for opening the create window '''
    global added_cards
    disable_main_buttons()
    # Create help window
    create_window = tk.Toplevel()
    create_window.iconbitmap('Text and Images/Logo.ico')
    create_window.resizable(False, False)
    # Add Header
    header = tk.Label(create_window, text='Create Database', font=('Helvetica', 20, 'bold'))
    header.grid(row=0, column=0, columnspan=1, padx=10)
    # Frame and Entry for the outgoing file location
    outgoing_frame = tk.LabelFrame(create_window, text='Outgoing File Location')
    outgoing_entry = tk.Entry(outgoing_frame)
    outgoing_entry.grid(row=0, column=0, padx=5, pady=5)
    outgoing_frame.grid(row=1, column=0, pady=5)
    create_feedback_frame = tk.Frame(create_window)
    create_feedback_frame.grid(row=3, column=0, pady=5)
    # Create Button
    create_database_button = tk.Button(create_window, text='Create!', bd=5, relief='raised', padx=30, pady=5,
                                       command=lambda: Magic_Info_Gatherer.run(outname=outgoing_entry.get(),
                                                                               cardslist=added_cards, feedback=create_feedback_frame))
    create_database_button.grid(row=2, column=0, padx=5, pady=5)

    # Check if the window was closed. If so, close it and enable buttons again.
    create_window.protocol("WM_DELETE_WINDOW", lambda: enable_main_buttons(create_window))

def scan_window():
    ''' Function for opening the scan window '''
    global added_cards
    global scan_error_label
    global scan_error_frame
    disable_main_buttons()
    # Create help window
    scan_window = tk.Toplevel()
    scan_window.iconbitmap('Text and Images/Logo.ico')
    scan_window.resizable(False, False)
    # Add Header
    header = tk.Label(scan_window, text='Add Cards from Scan', font=('Helvetica', 20, 'bold'))
    header.grid(row=0, column=0, columnspan=2)
    # Create a label and a LabelFrame to store the image from the webcam
    webcam_frame = tk.LabelFrame(scan_window, text='')
    webcam_image = tk.Label(webcam_frame)
    webcam_frame.grid(row=1, column=0, padx=5, pady=5, columnspan=2)
    webcam_image.grid(row=0, column=0, padx=5, pady=5)
    # Create the Video Capture object
    video_capture = cv.VideoCapture(0)
    # Error Frame for the user
    scan_error_frame = tk.LabelFrame(scan_window, text='Last Scanned Card')
    scan_error_frame.grid(row=2, column=0, padx=5, pady=5)
    # Remove Last Added Button
    remove_last = tk.Button(scan_window, text='Remove Last Added', padx=20, pady=5, bd=5, relief='raised',
                            command=remove_last_card)
    remove_last.grid(row=2, column=1, pady=5, padx=5)
    # Manual Entry
    manual_entry_frame = tk.LabelFrame(scan_window, text='Manual Entry')
    manual_entry = tk.Entry(manual_entry_frame)
    manual_entry.grid(row=0, column=0, padx=5, pady=5)
    manual_entry_frame.grid(row=3, column=0, pady=5)
    manual_entry_button = tk.Button(scan_window, text='Add Card', padx=20, pady=5, bd=5, relief='raised',
                            command=lambda: add_manual_card(manual_entry.get(), manual_entry))
    manual_entry_button.grid(row=3, column=1, pady=5, padx=5)



    # Show the video and establish variables
    waiting = False
    wait_cycle = 0
    #attempts = 0
    while True:
        isTrue, frame = video_capture.read() # Get the image
        if isTrue: # If we get a reading
            if waiting:
                try:
                    # Add a targeting rectangle
                    cv.rectangle(frame, pt1=(20, frame.shape[0] // 2 - 30),
                                 pt2=(frame.shape[1] - 50, frame.shape[0] // 2 + 30), thickness=1, color=(0, 0, 255))
                    cv.putText(frame, text='Waiting...', org=(20, frame.shape[0] // 2 - 40),
                               fontFace=cv.FONT_HERSHEY_COMPLEX,
                               fontScale=0.5, color=(0, 0, 255), thickness=1)
                    show_webcam_image(frame, webcam_image, webcam_frame)
                    # Leave Condition
                    wait_cycle += 1
                    if wait_cycle >= 80:
                        wait_cycle = 0
                        waiting = False
                except:
                    break # If we leave in the waiting loop, break.
            else:
                # Find the edges
                blur = cv.GaussianBlur(frame, ksize=(5, 5), sigmaX=5)
                t1 = 21
                t2 = 23
                canny = cv.Canny(blur, threshold1=t1, threshold2=t2)
                masked_image = Scan_Functions.get_titlebox(canny, frame)
                # Add a targeting rectangle
                cv.rectangle(frame, pt1=(20, frame.shape[0] // 2 - 30),
                             pt2=(frame.shape[1] - 50, frame.shape[0] // 2 + 30), thickness=1, color=(0, 0, 0))
                cv.putText(frame, text='Place Card Title Box Here', org=(20, frame.shape[0] // 2 - 40),
                           fontFace=cv.FONT_HERSHEY_COMPLEX,
                           fontScale=0.5, color=(0, 0, 0), thickness=1)
                # Attempt to read
                try:
                    if masked_image is None:
                        raise Exception
                    show_webcam_image(masked_image, webcam_image, webcam_frame)
                    #attempts += 1
                    predicted_word = Scan_Functions.read_titlebox(masked_image)
                    if predicted_word:
                        if predicted_word not in added_cards:
                            added_cards.append(predicted_word)  # Add the card if not already added
                            waiting = True
                            # User feedback
                            try:
                                scan_error_label.destroy()
                            except:
                                pass
                            finally:
                                scan_error_label = tk.Label(scan_error_frame,
                                                           text=f'Added Card {predicted_word}', font=(15))
                                scan_error_label.grid(row=0, column=0, padx=5, pady=5)
                        else:
                            waiting = True
                            # User feedback
                            try:
                                scan_error_label.destroy()
                            except:
                                pass
                            finally:
                                scan_error_label = tk.Label(scan_error_frame,
                                                            text=f'Card {predicted_word} Already Scanned!', font=(15))
                                scan_error_label.grid(row=0, column=0, padx=5, pady=5)
                    # elif attempts >= 30:
                    #     attempts = 0
                    #     waiting = True
                    #     # User feedback
                    #     try:
                    #         scan_error_label.destroy()
                    #     except:
                    #         pass
                    #     finally:
                    #         scan_error_label = tk.Label(scan_error_frame,
                    #                                     text=f'Could Not Scan Card', font=(15))
                    #         scan_error_label.grid(row=0, column=0, padx=5, pady=5)
                    #         scan_error_frame.grid(row=2, column=0, padx=5, pady=5)
                except:
                    try:
                        show_webcam_image(frame, webcam_image, webcam_frame)
                    except: # If there is no frame anymore (i.e. the window is closed)
                        break
        else:
            print('Webcam Error')
            break

    video_capture.release()
    enable_main_buttons(scan_window)

# Helper/Button Functions
def disable_main_buttons():
    ''' Disable all buttons to stop window spamming '''
    global scan_button
    global manual_button
    global help_button
    global view_button
    global clear_button
    global create_button
    scan_button['state'] = tk.DISABLED
    manual_button['state'] = tk.DISABLED
    help_button['state'] = tk.DISABLED
    view_button['state'] = tk.DISABLED
    clear_button['state'] = tk.DISABLED
    create_button['state'] = tk.DISABLED

def enable_main_buttons(window):
    ''' Enable all buttons again to allow for window opening.
     Called upon closing a derivitive window of home. The window to be closed is the keyword "window"'''
    global scan_button
    global manual_button
    global help_button
    global view_button
    global clear_button
    global create_button
    scan_button['state'] = tk.NORMAL
    manual_button['state'] = tk.NORMAL
    help_button['state'] = tk.NORMAL
    view_button['state'] = tk.NORMAL
    clear_button['state'] = tk.NORMAL
    create_button['state'] = tk.NORMAL
    window.destroy()

def add_section(header, text_file, window, row_count):
    tk_header = tk.Label(window, text=header, font=('Helvetica', 20, 'bold'))
    tk_header.grid(row=row_count, column=0)
    with open(text_file) as f:
        section_text = ''
        for line in f:
            section_text += line
        section_label = tk.Label(window, text=section_text)
        section_label.grid(row=row_count + 1, column=0)

def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]

def display_cards(array, frame):
    ''' Display the array of cards in the given frame. '''
    global child_view_frame
    child_view_frame = tk.Frame(frame)
    for i in range(len(array)):
        label_txt = '\n'.join(array[i])
        label = tk.Label(child_view_frame, text=label_txt)
        label.grid(row=0, column=i)
    child_view_frame.pack()

def forwards_view_button(array_list, frame, for_button, back_button):
    ''' for_button = the button itself. index = the CURRENT index of the array '''
    global view_index
    global child_view_frame
    view_index += 1
    # Clear the current frame and display the new one
    child_view_frame.destroy()
    display_cards(array_list[view_index], frame)
    # Disable / Enable
    if view_index + 1 == len(array_list):
        for_button['state'] = tk.DISABLED
    if view_index == 1:
        back_button['state'] = tk.NORMAL

def backwards_view_button(array_list, frame, for_button, back_button):
    ''' for_button = the button itself. index = the CURRENT index of the array '''
    global view_index
    global child_view_frame
    view_index -= 1
    # Clear the current frame and display the new one
    try:
        child_view_frame.destroy()
    except:
        pass
    display_cards(array_list[view_index], frame)
    # Disable / Enable
    if view_index <= 0:
        back_button['state'] = tk.DISABLED
    if view_index == len(array_list):
        for_button['state'] = tk.NORMAL

def clear_added():
    global added_cards
    global clear_feedback
    if added_cards != []:
        added_cards = []
        clear_feedback.grid(row=2, column=0, pady=5)
    else:
        try:
            clear_feedback.grid_remove()
        except:
            pass

def clear_entered_card(cardname):
    global added_cards
    global clear_feedback
    if cardname in added_cards:
        added_cards.remove(cardname)
        clear_feedback.grid(row=4, column=0, pady=5)
    else:
        try:
            clear_feedback.grid_remove()
        except:
            pass

def from_file(directory, cardslist, error_frame):
    ''' Add the cardnames in the given .csv or .txt file '''
    global add_error_label

    if os.path.exists(directory):
        extension = os.path.splitext(directory)[1]
        if extension not in ['.csv', '.txt']:
            try:
                add_error_label.destroy()
            except:
                pass
            finally:
                add_error_label = tk.Label(error_frame, text='Invalid Filetype. Use formatted .txt or .csv files only.')
                add_error_label.grid(row=0, column=0, padx=5, pady=5)
                error_frame.grid(row=2, column=0, padx=5, pady=5)
        elif extension == '.csv':
            # From a csv file
            with open(directory) as csv_file:
                csv_reader = csv.reader(csv_file)
                try: # If there is anything in the file, try this
                    if next(csv_reader) == ['Name', 'Colors', 'Rarity', 'CMC', 'Type', 'Price', 'Set', 'Image Link']:
                        for line in csv_reader:
                            cardslist.append(line[0])
                        try:
                            add_error_label.destroy()
                        except:
                            pass
                        finally:
                            add_error_label = tk.Label(error_frame, text='Added Cards Successfully!')
                            add_error_label.grid(row=0, column=0, padx=5, pady=5)
                            error_frame.grid(row=2, column=0, padx=5, pady=5)
                    else:
                        try:
                            add_error_label.destroy()
                        except:
                            pass
                        finally:
                            add_error_label = tk.Label(error_frame, text='.csv file is not properly formatted. See "How to use this App" for details.')
                            add_error_label.grid(row=0, column=0, padx=5, pady=5)
                            error_frame.grid(row=2, column=0, padx=5, pady=5)
                except: # Empty file = not properly formatted
                    try:
                        add_error_label.destroy()
                    except:
                        pass
                    finally:
                        add_error_label = tk.Label(error_frame,
                                                   text='.csv file is not properly formatted. See "How to use this App" for details.')
                        add_error_label.grid(row=0, column=0, padx=5, pady=5)
                        error_frame.grid(row=2, column=0, padx=5, pady=5)
        else:
            # From a text file
            Magic_Info_Gatherer.loadCards(cardslist, directory)
            try:
                error_label.destroy()
            except:
                pass
            finally:
                error_label = tk.Label(error_frame, text='Added Cards Successfully!')
                error_label.grid(row=0, column=0, padx=5, pady=5)
                error_frame.grid(row=2, column=0, padx=5, pady=5)
    else:
        try:
            error_label.destroy()
        except:
            pass
        finally:
            error_label = tk.Label(error_frame, text="Path Doesn't Exist")
            error_label.grid(row=0, column=0, padx=5, pady=5)
            error_frame.grid(row=2, column=0, padx=5, pady=5)

def show_webcam_image(image, image_label, image_frame):
    ''' Show an image in a tkinter label and update '''
    cv.imwrite('webcam_image.png', image)  # Save as a png in the cwd
    tkinter_frame = ImageTk.PhotoImage(Image.open('webcam_image.png'))  # Convert to tkinter image
    image_label['image'] = tkinter_frame
    image_frame.update()

def remove_last_card():
    global scan_error_label
    if len(added_cards) >= 1:
        removed = added_cards.pop()
        try:
            scan_error_label.destroy()
        except:
            pass
        finally:
            scan_error_label = tk.Label(scan_error_frame, text=f'Card {removed} Removed', font=(15))
            scan_error_label.grid(row=0, column=0, padx=5, pady=5)
    else:
        try:
            scan_error_label.destroy()
        except:
            pass
        finally:
            scan_error_label = tk.Label(scan_error_frame, text=f'Added Cards are Empty!', font=(15))
            scan_error_label.grid(row=0, column=0, padx=5, pady=5)

def add_manual_card(cardname, entrybox):
    global scan_error_label
    if cardname != '':
        added_cards.append(cardname)
        entrybox.delete(0, 'end')
        try:
            scan_error_label.destroy()
        except:
            pass
        finally:
            scan_error_label = tk.Label(scan_error_frame, text=f'Added Card {cardname}', font=(15))
            scan_error_label.grid(row=0, column=0, padx=5, pady=5)
    else:
        try:
            scan_error_label.destroy()
        except:
            pass
        finally:
            scan_error_label = tk.Label(scan_error_frame, text='Entry Box is Empty', font=(15))
            scan_error_label.grid(row=0, column=0, padx=5, pady=5)

if __name__ == '__main__':
    # Establish pytesseract
    t_path = r'C:\Users\gamer\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
    pytesseract.tesseract_cmd = t_path
    # Start Application
    added_cards = []
    home_window()
    try: # Try to remove the webcam image. Just to clean the cwd.
        os.remove(os.path.join(os.getcwd(), 'webcam_image.png'))
    except:
        pass