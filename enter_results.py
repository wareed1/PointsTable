"""
 enter_results_2.py:  Enter Event Card Results
         Wayne Reed
         July, 2016
         Updated August, 2018

         A Python program for data entry of the results of the
         Bluefins swim meet
"""
from tkinter import Label, Entry, Button, OptionMenu, StringVar, Tk, \
                    PhotoImage, mainloop, END, \
                    messagebox as tkMessageBox
from tkinter.ttk import Separator
#from time import gmtime, strftime
import csv
import os
import filemgr

# pylint: disable=C0103

POINTS_TABLE_TITLE = "Points Table - Data Entry"
SWIMMER_NUMBER_LABEL_TEXT = "Swimmer Number"
EVENT_LABEL_TEXT = "Event"
LANE_LABEL_TEXT = "Lane"
TIME_LABEL_TEXT = "Time"
MINUTES_REMINDER_LABEL_TEXT = "minutes (M)"
SECONDS_REMINDER_LABEL_TEXT = "seconds (SS.SS) -- zero-pad, e.g., 03.09 or 00.00"
VALID_LABEL_TEXT = "Valid"
VALID_LIST = ['OK', 'DQ', 'DNF']
SAVE_ENTRY_BUTTON_TEXT = "Save Entry"
SWIMMER_NAME_LABEL_TEXT = "Swimmer"
AGE_CATEGORY_LABEL_TEXT = "Category"
CLUB_LABEL_TEXT = "Club"
CLASS_LABEL_TEXT = "Class"
CLASS_LIST = ['N', 'C', 'T']
SAVE_SWIMMTER_BUTTON_TEXT = "Save Swimmer"
GENERATE_RESULTS_BUTTON_TEXT = "Generate Results"
QUIT_BUTTON_TEXT = "Quit"
ENTRY_MODE_LABEL_TEXT = "Entry Mode"
ENTRY_MODE_LIST = ['Events', 'Free Relays', 'Clubs']
RELOAD_SWIMMERS_BUTTON_TEXT = "Reload Swimmers"

FONT_SIZE = 25
SMALL_FONT_SIZE = 10
FONT = "Ariel"
CONFIG_FILE = "ms.conf"

# Grid layout
# ROWS
SWIMMER_NO_ROW = 0
NEXT_AVAILABLE_ROW = 0
ENTRY_MODE_TEXT_ROW = 0
ENTRY_MODE_ROW = 0
EVENT_ROW = 1
LANE_ROW = 2
TIME_ROW = 3
TIME_HINT_ROW = 4
VALID_ROW = 5
BUTTONS_1_ROW = 6
SEPARATOR_ROW = 7
SWIMMER_NAME_ROW = 8
TEAM_CHECKBOX_ROW = 8
CATEGORY_ROW = 9
ICON_ROW = 9
CLUB_ROW = 10
CLASS_ROW = 11
BUTTONS_2_ROW = 12
HELP_TEXT_ROW = 12
# COLUMNS
LABEL_COLUMN = 0
HELP_TEXT_COLUMN = 0
PRIME_ENTRY_COLUMN = 1
SAVE_BUTTON_COLUMN = 1
SECOND_ENTRY_COLUMN = 2
ICON_COLUMN = 3
GENERATE_BUTTON_COLUMN = 2
NEXT_AVAILABLE_COLUMN = 2
RELOAD_SWIMMERS_BUTTON_COLUMN = 2
ENTRY_MODE_TEXT_COLUMN = 2
QUIT_BUTTON_COLUMN = 3

ICON_ROW_SPAN = 3
ICON_COLUMN_SPAN = 2

def check_age():
    """ Validate swimmer age to category """
    eventClass = event_var.get()
    parts = eventClass.split(',')
    if len(parts) == 3:
        # now it gets complicated
        # events AA and BB have a category that does not match
        # swimmer categories.  Take this fact into consideration
        # in the validation
        # To make logic easier to understand, we'll compute the
        # correct match and fail if it's not true
        matched_age = parts[1] == age_category_var.get() or \
           (parts[1] == "Boys 8 & Under" and age_category_var.get() == "Boys 6 & Under") or \
           (parts[1] == "Girls 8 & Under" and age_category_var.get() == "Girls 6 & Under") or\
           (parts[1] == "Boys 8 & Under" and age_category_var.get() == "Boys 7 & 8") or \
           (parts[1] == "Girls 8 & Under" and age_category_var.get() == "Girls 7 & 8")
        if not matched_age:
            tkMessageBox.showinfo("!!! WARNING !!!", \
                           "Age category mismatch for swimmer:  " + \
                                 parts[1] + " != " + age_category_var.get(), parent=master)
def cb_get_swimmer(event):
    """ Match the swimmer number to swimmer name """
    swimmer_number = swimmer_number_entry.get()
    element = 0
    swimmer_reference = -1
    while element < len(swimmers_data):
        if swimmer_number == swimmers_data[element][0]:
            swimmer_reference = element
            # done: last iteration of search
            element = len(swimmers_data)
        else:
            element += 1
    swimmer_name_entry.delete(0, END)
    if swimmer_reference == -1:
        swimmer_name_entry.insert(END, 'NOT FOUND')
    else:
        swimmer_name_entry.insert(END, swimmers_data[swimmer_reference][1])
        age_category_var.set(swimmers_data[swimmer_reference][3])
        club_var.set(swimmers_data[swimmer_reference][2])
        class_var.set(swimmers_data[swimmer_reference][4])
    if do_age_check == "True":
        check_age()

def generate_results():
    """ Produce the meet results """
    return_code = os.system("python ms2.py")
    if results_warning == "True":
        if return_code != 0:
            tkMessageBox.showinfo( \
                "Error", "Results generation failed, check Command Prompt window for details", \
                parent=master)

def clear_entry():
    """ Erase fields filled in """
    swimmer_number_entry.delete(0, END)
    lane_entry.delete(0, END)
    minutes_entry.delete(0, END)
    seconds_entry.delete(0, END)
    swimmer_name_entry.delete(0, END)
    valid_var.set(VALID_LIST[0])
    if leave_swimmer_category != "True":
        age_category_var.set('')
    club_var.set('')
    class_var.set('')

def save_results_to_file():
    """ Save the internal database to file """
    try:
        filename = filemgr.get_value("raw_results_file")
        file_descriptor = open(filename, 'w', newline='')
        csv_writer = csv.writer(file_descriptor)
        for item in results_data:
            csv_writer.writerow(item)
        file_descriptor.close()
        tkMessageBox.showinfo("Confirmation", "Saved", parent=master)
        clear_entry()

    except IOError:
        print("file " + filename + " could not be opened")
        exit(2)

def validate_data_entry():
    """ Ensure all fields on screen are populated """
    missing_field = not lane_entry.get() or \
            not minutes_entry.get() or \
            not seconds_entry.get() or \
            not swimmer_number_entry.get() or \
            not event_var.get() or \
            not swimmer_name_entry.get() or \
            swimmer_name_entry.get() == "NOT FOUND" or \
            not valid_var.get() or \
            not age_category_var.get() or \
            not club_var.get() or \
            not class_var.get()
    if missing_field:
        tkMessageBox.showinfo("Error", "Complete data entry before saving", parent=master)
        return False
    return True

def save_results():
    """ Save the information from the event card populated on the screen """
	# validate that all mandatory fields have values
    if not validate_data_entry():
        return
    #    event number,event description,swimmer,swimmer number,club,class,time,valid,lane,version
    parts = event_var.get().split(',')
    if len(parts) != 3:
        tkMessageBox.showinfo("Error", "Events data corrupted!", parent=master)
        return
    # check that the entry isn't a duplicate if attempting to save
    duplicate = False
    for item in results_data:
        if item[0] == parts[0] and item[4] == swimmer_number_entry.get():
            duplicate = True
            break
    if duplicate:
        tkMessageBox.showinfo( \
            "Error", "Record already exists for this swimmer in this event", \
            parent=master)
        return
    line = [parts[0], \
            parts[1], \
            parts[2], \
            swimmer_name_entry.get(), \
            swimmer_number_entry.get(), \
            club_var.get(), \
            class_var.get(), \
            minutes_entry.get() + ":" + seconds_entry.get(), \
            valid_var.get(), \
            lane_entry.get(), \
            "v2"]
    results_data.append(line)
    save_results_to_file()

def get_next_available_swimmer_number():
    """ Find next available swimmer number not related to a club """
    next_available = 1
    for item in swimmers_data:
        if int(item[0]) > int(next_available):
            next_available = item[0]
    next_available = str(int(next_available) + 1)
    return next_available

def load_swimmers_data():
    """ Get the list of swimmers """
    swimmers_filename = filemgr.get_value("swimmers_file")
    filemgr.read_file(swimmers_filename, swimmers_data, filemgr.MULTI_DIMENSION)
    next_available = get_next_available_swimmer_number()
    show_next_available(next_available)

def reload_swimmers():
    """ Read in the file containing the list of swimmers:
        Used when file edited offline (e.g., to change an age category) """
    # reload file
    del swimmers_data[:]
    load_swimmers_data()
    tkMessageBox.showinfo("Reload", "Done", parent=master)

def write_swimmer_database_to_file():
    """ Update swimmer list stored in file """
    try:
        swimmers_filename = filemgr.get_value("swimmers_file")
        file_descriptor = open(swimmers_filename, 'w')
        for item in swimmers_data:
            file_descriptor.write(item[0] + ',' + \
                                  item[1] + ',' + \
                                  item[2] + ',' + \
                                  item[3] + ',' + \
                                  item[4] + '\n')
        file_descriptor.close()
        tkMessageBox.showinfo("Confirmation", "Saved", parent=master)
        # reload file
        del swimmers_data[:]
        load_swimmers_data()

    except IOError:
        print("file " + swimmers_filename + " could not be opened")
        exit(2)

def focus_after_saving_swimmer():
    """
    Reposition cursor after saving swimmer, reposition based on entry mode
    """
    # check "entry" dropdown for where to position
    if entry_mode_var.get() == ENTRY_MODE_LIST[2]:
        # club mode entry
        swimmer_name_entry.focus()
        swimmer_name_entry.delete(0, END)
        age_category_var.set('')
        class_var.set('')
        show_next_club_swimmer(club_var.get())
    else:
        # assume event mode entry
        # assume that now we want to enter results, reposition to lane
        lane_entry.focus()

def save_swimmer():
    """
    Add a new swimmer to the list of participants
	Or update the swimmer information if record already exists
    """
    missing_field = not swimmer_number_entry.get() or \
                    not swimmer_name_entry.get() or \
                    not club_var.get() or \
                    not age_category_var.get() or \
                    not class_var.get()
    if missing_field:
        tkMessageBox.showinfo("Error", "Missing information", parent=master)
    else:
        # determine if new record or an update to an existing record
        found = False
        index = 0
        while index < len(swimmers_data) and not found:
            if swimmers_data[index][0] == swimmer_number_entry.get():
                # end search
                found = True
            else:
                index += 1
        if found:
            # update the record
            swimmers_data[index][1] = swimmer_name_entry.get() # swimmer name
            swimmers_data[index][2] = club_var.get()
            swimmers_data[index][3] = age_category_var.get()
            swimmers_data[index][4] = class_var.get()
        else:
            # new record
            new_record = [swimmer_number_entry.get(), \
                          swimmer_name_entry.get(), \
                          club_var.get(), \
                          age_category_var.get(), \
                          class_var.get()]
            if class_var.get() == CLASS_LIST[2]:
                # if a team, put at end of database
                swimmers_data.append(new_record)
            else:
                # find next available swimmer number for the club
                swimmer_number, index = get_next_available_swimmer_number_for_club(club_var.get())
                if swimmer_number == -1:
                    # did not find a place, add to end of database
                    swimmers_data.append(new_record)
                else:
                    # insert at free space
                    swimmers_data.insert(index, new_record)
        write_swimmer_database_to_file()
        focus_after_saving_swimmer()

def update_from_event_number():
    """ update cursor from event number entry """
    if master.focus_get() == event_entry:
        event_no = event_entry.get().upper()
        if event_no != "":
            # update the event displayed
            match = event_no + ','
            found = False
            for item in events_data:
                if item.find(match) == 0:
                    event_var.set(item)
                    event_entry.delete(0, END)
                    swimmer_number_entry.focus()
                    found = True
                    break
            if not found:
                tkMessageBox.showinfo("Error", "No event: " + event_no, parent=master)

def update_from_club():
    """ update cursor from club entry """
    club = club_entry.get()
    if club == "" and club_var.get() != "":
        # save swimmer
        save_swimmer()
    elif club != "":
        # update the club displayed
        idx = -1
        for club_idx, item in enumerate(clubs_data):
            if item.lower().find(club.lower()) == 0:
                if idx == -1:
                    # first one found
                    idx = club_idx
                else:
                    # not unique
                    idx = len(clubs_data)
        # if non-unique entry found, do nothing
        # user can add more characters to make match unique
        if idx == -1:
            tkMessageBox.showinfo("Error", "No club starting with: " + club, parent=master)
            club_entry.delete(0, END)
        elif idx != len(clubs_data):
            # unique entry found, show it
            club_var.set(clubs_data[idx])
            club_entry.delete(0, END)
            club_entry.focus()

def cb_reposition_cursor(event):
    """ Move cursor based on field of focus """
    # event number
    if master.focus_get() == event_entry:
        update_from_event_number()
    # club
    elif master.focus_get() == club_entry:
        update_from_club()
    # swimmer number --> lane
    elif master.focus_get() == swimmer_number_entry:
        lane_entry.focus()
    # lane --> time in minutes
    elif master.focus_get() == lane_entry:
        minutes_entry.focus()
    # time in minutes --> time in seconds
    elif master.focus_get() == minutes_entry:
        seconds_entry.focus()
    # time in seconds --> swimmer number
    elif master.focus_get() == seconds_entry:
        save_results()
        if entry_mode_var.get() == 'Free Relays':
            next_available = get_next_available_swimmer_number()
            swimmer_number_entry.delete(0, END)
            swimmer_number_entry.icursor(0)
            swimmer_number_entry.insert(END, next_available)
            swimmer_name_entry.focus()
            idx = CLASS_LIST.index('T')
            class_var.set(CLASS_LIST[idx])
        else:
            swimmer_number_entry.focus()
    # swimmer --> club
    elif master.focus_get() == swimmer_name_entry:
        club_entry.focus()

def show_next_available(swimmer_number):
    """ Update next available swimmer number on screen """
    next_available_var.set("Next Available: " + str(swimmer_number))

def get_next_available_swimmer_number_for_club(club):
    """
    Find the location in the database for a new swimmer for a club
    """
    # scan swimmer database for club
    # we want to track two values:  free swimmer number and
    # where to put that swimmer in the database (to keep clubs together)
    index = 1
    swimmer_number = -1
    done = False
    while not done:
        # we have found a free swimmer number when swimmer number for previous entry + 1
        # is less than swimmer number for current entry
        if swimmers_data[index - 1][2] == club and \
            int(swimmers_data[index][0]) > int(swimmers_data[index - 1][0]) + 1:
            # found a free space
            swimmer_number = int(swimmers_data[index - 1][0]) + 1
            done = True
        elif index == len(swimmers_data) - 1:
            # exhausted search
            done = True
        else:
            index = index + 1
    return swimmer_number, index

def show_next_club_swimmer(club):
    """ Get next available swimmer number for club """
    swimmer_number, _ = get_next_available_swimmer_number_for_club(club)
    if swimmer_number == -1:
        # we did not find an available swimmer number
        tkMessageBox.showinfo( \
            "Error", "Could not find an available swimmer number for the selected club", \
            parent=master)
        return False
    # update screen
    swimmer_number_entry.delete(0, END)
    swimmer_number_entry.insert(END, str(swimmer_number))
    swimmer_name_entry.focus()
    show_next_available(str(swimmer_number))
    return True

def change_mode_to_free_relay_entry():
    """
    Put points table into free relay entry mode
    """
    idx = CLASS_LIST.index('T')
    class_var.set(CLASS_LIST[idx])
    if event_var.get() != "":
        # get category
        parts = event_var.get().split(',')
        if len(parts) == 3:
            category = parts[1]
            idx = categories_data.index(category)
            age_category_var.set(categories_data[idx])
        swimmer_number_entry.delete(0, END)
        next_available = get_next_available_swimmer_number()
        swimmer_number_entry.insert(END, next_available)
        show_next_available(str(next_available))
        club_var.set("")
        swimmer_name_entry.focus()

def change_mode_to_clubs_entry():
    """
    Put points table into swimmer entry mode for a specific club
    """
    # Data entry for a swim club
    # Is the club set?
    club = club_var.get()
    if club == '':
        tkMessageBox.showinfo("Error", "Set club before entering this entry mode", \
                              parent=master)
        # reset to event mode
        entry_mode_var.set(ENTRY_MODE_LIST[0])
    else:
        # set swimmer number
        if not show_next_club_swimmer(club):
            # reset to event mode
            entry_mode_var.set(ENTRY_MODE_LIST[0])

def cb_ready_entry_mode(event):
    """ set up for data entry mode change """
    if event == "Free Relays":
        change_mode_to_free_relay_entry()
    elif event == "Clubs":
        change_mode_to_clubs_entry()
    # This mode may have been selected or may have been forced from another mode
    if entry_mode_var.get() == ENTRY_MODE_LIST[0]:
        # Event entry mode
        swimmer_number_entry.delete(0, END)
        class_var.set("")
        club_var.set("")
        age_category_var.set("")
        swimmer_number_entry.focus()
        next_available = get_next_available_swimmer_number()
        show_next_available(next_available)


def cb_list_teams(event):
    """ Show teams to find swimmer number for event """
    team_list = []
    category = ""
    event = event_var.get()
    if event != "":
        # get category
        parts = event.split(',')
        if len(parts) == 3:
            category = parts[1]
    for swimmer in swimmers_data:
        if swimmer[4] == 'T':
            if category == "":
                # show all teams
                item = swimmer[0] + ',' + swimmer[1] + ',' + swimmer[2] + ',' + swimmer[3]
                team_list.append(item)
            else:
                # show only teams for the applicable age category
                if category in swimmer:
                    item = swimmer[0] + ',' + swimmer[1] + ',' + swimmer[2]
                    team_list.append(item)
    if not team_list:
        team_list.append("No teams!")
    tkMessageBox.showinfo("List of Teams", "\n".join(team_list), parent=master)

def cb_help_for_change_swimmer(event):
    """ Provide help text to change swimmer information """
    edit_swimmer_text = "To change a swimmer:\n" + \
                        "- enter the swimmer number;\n" + \
                        "- press <Enter> to fill in the fields;\n" + \
                        "- make any desired changes\n" + \
                        "  (do not change the swimmer number);\n" + \
                        "- and press 'Save Swimmer' button to save the changes."
    tkMessageBox.showinfo("Info", edit_swimmer_text, parent=master)

def cb_help_for_change_result(event):
    """ Provide help text to edit an event result """
    edit_results_text = "To retrieve an event result:\n" + \
                        "- enter the swimmer number;\n" + \
                        "- enter or the select the event number;\n" + \
                        " - press <CTRL-R> to retrieve the event record.\n" + \
                        "\n" + \
                        "!!! The 'Save Entry' button must be grey to\n" + \
                        "    update or delete an event result.\n" +\
                        "\n" +\
                        "To update the retrieved event record:\n" +\
                        "- make any desired changes\n" + \
                        "- when ready to save, press <CTRL-U> to update" +\
                        "- click on 'Yes' when prompted to update and confirm.\n" +\
                        "\n" +\
                        "To delete the retrieved event record:\n" +\
                        "- press <CTRL-D> to delete;" +\
                        "- click on 'Yes' when prompted to delete and confirm."
    tkMessageBox.showinfo("Info", edit_results_text, parent=master)

def get_swimmer_number_and_event():
    """ Get the swimmer number and the event number from the entry fields """
    swimmer_number = swimmer_number_entry.get()
    event_number = event_var.get()
    parts = event_number.split(',')
    if len(parts) > 1:
        event_number = parts[0]
    else:
        event_number = ''
    if swimmer_number == '':
        tkMessageBox.showinfo("Error", "Enter swimmer number", parent=master)
        swimmer_number_entry.focus()
    elif event_number == '':
        tkMessageBox.showinfo("Error", "Enter event number", parent=master)
        event_entry.focus()
    return swimmer_number, event_number

def find_swimmer_in_database(swimmer_number):
    """ Get the index of the swimmer in the database """
    swimmer_idx = -1
    for index, item in enumerate(swimmers_data):
        if item[0] == swimmer_number:
            swimmer_idx = index
            break
    return swimmer_idx

def find_swimmer_and_event_in_results(swimmer_number, event_number):
    """ Get the index of a matching entry in the results database """
    event_idx = -1
    for index, item in enumerate(results_data):
        if item[0] == event_number and item[4] == swimmer_number:
            event_idx = index
            break
    return event_idx

def populate_event_fields(results_idx):
    """ Show saved results on Points Table """
    # delete any shown fields before populating
    lane_entry.delete(0, END)
    lane_entry.insert(0, results_data[results_idx][9])
    swimmer_name_entry.delete(0, END)
    swimmer_name_entry.insert(0, results_data[results_idx][3])
    club_var.set(results_data[results_idx][5])
    age_category_var.set(results_data[results_idx][6])
    class_var.set(results_data[results_idx][8])
    parts = results_data[results_idx][7].split(':')
    if len(parts) == 2:
        minutes_entry.delete(0, END)
        minutes_entry.insert(0, parts[0])
        seconds_entry.delete(0, END)
        seconds_entry.insert(0, parts[1])

def cb_retrieve_results_entry(event):
    """ Show an entered result """
    swimmer_number, event_number = get_swimmer_number_and_event()
    if swimmer_number != '' and event_number != '':
        # find swimmer number in swimmers databases
        swimmer_idx = find_swimmer_in_database(swimmer_number)
        if swimmer_idx == -1:
            tkMessageBox.showinfo("Error", "No swimmer number: " + swimmer_number, parent=master)
        else:
            # find event number and swimmer number in results databases
            results_idx = find_swimmer_and_event_in_results(swimmer_number, event_number)
            if results_idx == -1:
                tkMessageBox.showinfo("Error", "No matching event for the swimmer number: " + \
                                      swimmer_number, parent=master)
            else:
                populate_event_fields(results_idx)
                save_entry_button.config(state='disabled')
                # set cursor on Lane entry
                lane_entry.focus()

def cb_delete_results_entry(event):
    """ Delete an entry from the results database """
    if save_entry_button['state'] != 'disabled':
        tkMessageBox.showinfo("Error", "Retrieve record first", parent=master)
    else:
        response = tkMessageBox.askyesno("Delete", "Delete this entry?", parent=master)
        if response:
            response = tkMessageBox.askokcancel("Confirm", "Click OK to confirm", parent=master)
            if response:
                swimmer_number, event_number = get_swimmer_number_and_event()
                results_idx = find_swimmer_and_event_in_results(swimmer_number, event_number)
                if results_idx != -1:
                    # given how we got here, the index should never be -1
                    del results_data[results_idx]
                    save_results_to_file()
        #save_entry_button_var.set('Save Entry')
        save_entry_button.config(state='normal')

def cb_update_results_entry(event):
    """ Update an entry from the results database """
    if save_entry_button['state'] != 'disabled':
        tkMessageBox.showinfo("Error", "Retrieve record first", parent=master)
    else:
        response = tkMessageBox.askyesno("Update", "Update this entry?", parent=master)
        if response:
            response = tkMessageBox.askokcancel("Confirm", "Click OK to confirm", parent=master)
            if response:
                swimmer_number, event_number = get_swimmer_number_and_event()
                results_idx = find_swimmer_and_event_in_results(swimmer_number, event_number)
                if results_idx != -1:
                    # given how we got here, the index should never be -1
                    del results_data[results_idx]
                    save_results()
        #save_entry_button_var.set('Save Entry')
        save_entry_button.config(state='normal')

# main
master = Tk()
master.wm_title(POINTS_TABLE_TITLE)
# read the configuration file
filemgr.read_file(CONFIG_FILE, filemgr.CONFIG_DATA, filemgr.MULTI_DIMENSION)
# get the list of clubs
clubs_data = []
clubs_filename = filemgr.get_value("clubs_file")
filemgr.read_file(clubs_filename, clubs_data, filemgr.SINGLE_DIMENSION)
# get the list of events
events_data = []
events_filename = filemgr.get_value("events_file")
filemgr.read_file(events_filename, events_data, filemgr.SINGLE_DIMENSION)
# get the list of age categores
categories_filename = filemgr.get_value("categories_file")
# get the unprocessed event results
results_data = []
results_filename = filemgr.get_value("raw_results_file")
filemgr.read_file(results_filename, results_data, filemgr.MULTI_DIMENSION)

# new features:  override with configuration file setting
do_age_check = filemgr.get_value("do_age_check")
leave_swimmer_category = filemgr.get_value("leave_swimmer_category")
show_reload_button = filemgr.get_value("reload_swimmers_button")
results_warning = filemgr.get_value("results_warning")
first_event = filemgr.get_value("first_event")

# show next available swimmer number on screen
# this label needs to be defined before loading swimmer database
next_available_var = StringVar()
Label(master, textvariable=next_available_var, font=(FONT, FONT_SIZE), anchor='e').\
      grid(row=NEXT_AVAILABLE_ROW, column=NEXT_AVAILABLE_COLUMN, sticky='W')

# get the list of categories
categories_data = []
filemgr.read_file(categories_filename, categories_data, filemgr.SINGLE_DIMENSION)

# get swimmers
swimmers_data = []
load_swimmers_data()

# Swimmer club image on screen
image1 = PhotoImage(file=filemgr.get_value("image_file"))
#image_entry = Label(master, image=image1)
#image_entry.image = image1
#image_entry.grid(row=ICON_ROW, column=ICON_COLUMN, rowspan=ICON_ROW_SPAN, \
#            columnspan=ICON_COLUMN_SPAN, sticky='NEWS')

background_label = Label(master, image=image1)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# swimmer number data entry on screen
Label(master, text=SWIMMER_NUMBER_LABEL_TEXT, font=(FONT, FONT_SIZE), \
      anchor='e').grid(row=SWIMMER_NO_ROW, column=LABEL_COLUMN, sticky='E', padx=4, pady=4)
swimmer_number_entry = Entry(master, font=(FONT, FONT_SIZE), width=18)
swimmer_number_entry.grid(row=SWIMMER_NO_ROW, column=PRIME_ENTRY_COLUMN, sticky='W')
swimmer_number_entry.bind('<Return>', cb_get_swimmer)
swimmer_number_entry.bind('<Tab>', cb_get_swimmer)
swimmer_number_entry.focus()

# event data entry/selection on screen
Label(master, text=EVENT_LABEL_TEXT, font=(FONT, FONT_SIZE), \
      anchor='e').grid(row=EVENT_ROW, column=LABEL_COLUMN, sticky='E', pady=4)
event_var = StringVar()
if first_event == 'True':
    event_var.set(events_data[0])
else:
    event_var.set('')
event_dropdown = OptionMenu(master, event_var, None, *events_data)
event_dropdown.configure(font=(FONT, FONT_SIZE))
event_dropdown.grid(row=EVENT_ROW, column=PRIME_ENTRY_COLUMN, columnspan=2, \
                    sticky='W', padx=4, pady=4)
event_entry = Entry(master, font=(FONT, FONT_SIZE), width=4)
event_entry.grid(row=EVENT_ROW, column=SECOND_ENTRY_COLUMN, sticky='E', padx=1)

# lane number data entry on screen
Label(master, text=LANE_LABEL_TEXT, anchor='e', \
      font=(FONT, FONT_SIZE)).grid(row=LANE_ROW, column=LABEL_COLUMN, sticky='E', padx=4, pady=4)
lane_entry = Entry(master, font=(FONT, FONT_SIZE), width=18)
lane_entry.grid(row=LANE_ROW, column=PRIME_ENTRY_COLUMN, sticky='W')

# time data entry on screen
Label(master, text=TIME_LABEL_TEXT, anchor='e', \
      font=(FONT, FONT_SIZE)).grid(row=TIME_ROW, column=LABEL_COLUMN, sticky='E', padx=4, pady=4)
Label(master, text=MINUTES_REMINDER_LABEL_TEXT, anchor='w', \
      font=(FONT, SMALL_FONT_SIZE)).grid(row=TIME_HINT_ROW, \
                                         column=PRIME_ENTRY_COLUMN, sticky='WE')
Label(master, text=SECONDS_REMINDER_LABEL_TEXT, anchor='w', \
      font=(FONT, SMALL_FONT_SIZE)).grid(row=TIME_HINT_ROW, column=SECOND_ENTRY_COLUMN, sticky='WE')
minutes_entry = Entry(master, font=(FONT, FONT_SIZE), width=18)
minutes_entry.grid(row=TIME_ROW, column=PRIME_ENTRY_COLUMN, sticky='W')
seconds_entry = Entry(master, font=(FONT, FONT_SIZE), width=18)
seconds_entry.grid(row=TIME_ROW, column=SECOND_ENTRY_COLUMN, sticky='W')

# results data entry validity selection on screen
Label(master, text=VALID_LABEL_TEXT, anchor='e', \
      font=(FONT, FONT_SIZE)).grid(row=VALID_ROW, column=LABEL_COLUMN, sticky='E', padx=4, pady=4)
valid_var = StringVar()
valid_dropdown = OptionMenu(master, valid_var, *VALID_LIST)
valid_dropdown.configure(font=(FONT, FONT_SIZE))
valid_dropdown.grid(row=VALID_ROW, column=PRIME_ENTRY_COLUMN, sticky='E', pady=4)
valid_var.set(VALID_LIST[0])

# Save entry button on screen
save_entry_button_var = StringVar()
save_entry_button_var.set(SAVE_ENTRY_BUTTON_TEXT)
save_entry_button = Button(master, textvariable=save_entry_button_var, command=save_results, \
       font=(FONT, FONT_SIZE))
save_entry_button.grid(row=BUTTONS_1_ROW, column=SAVE_BUTTON_COLUMN, sticky='W', pady=4)

# Generate results button on screen
Button(master, text=GENERATE_RESULTS_BUTTON_TEXT, command=generate_results, \
       font=(FONT, FONT_SIZE)).grid(row=BUTTONS_1_ROW, \
                                   column=GENERATE_BUTTON_COLUMN, sticky='W', pady=4)

# separate results entry from swimmer entry on screen
sep = Separator(master, orient="horizontal")
sep.grid(row=SEPARATOR_ROW, column=0, columnspan=3, sticky='WE', pady=14)

# swimmer name data entry on screen
Label(master, text=SWIMMER_NAME_LABEL_TEXT, font=(FONT, FONT_SIZE), \
      anchor='e').grid(row=SWIMMER_NAME_ROW, column=LABEL_COLUMN, sticky='E', padx=4, pady=4)
swimmer_name_entry = Entry(master, font=(FONT, FONT_SIZE))
swimmer_name_entry.grid(row=SWIMMER_NAME_ROW, column=PRIME_ENTRY_COLUMN, columnspan=2, sticky='WE')

# age category selection on screen
Label(master, text=AGE_CATEGORY_LABEL_TEXT, font=(FONT, FONT_SIZE), \
      anchor='e').grid(row=CATEGORY_ROW, column=LABEL_COLUMN, sticky='E', padx=4, pady=4)
age_category_var = StringVar()
age_category_dropdown = OptionMenu(master, age_category_var, None, *categories_data)
age_category_dropdown.configure(font=(FONT, FONT_SIZE))
age_category_dropdown.grid(row=CATEGORY_ROW, column=PRIME_ENTRY_COLUMN, sticky='E', pady=4)

# club data entry/selection on screen
Label(master, text=CLUB_LABEL_TEXT, font=(FONT, FONT_SIZE), \
      anchor='e').grid(row=CLUB_ROW, column=LABEL_COLUMN, sticky='E', padx=4, pady=4)
club_var = StringVar()
club_dropdown = OptionMenu(master, club_var, None, *clubs_data)
club_dropdown.configure(font=(FONT, FONT_SIZE))
club_dropdown.grid(row=CLUB_ROW, column=PRIME_ENTRY_COLUMN, sticky='E', pady=4)
club_entry = Entry(master, font=(FONT, FONT_SIZE), width=5)
club_entry.grid(row=CLUB_ROW, column=SECOND_ENTRY_COLUMN, sticky='W', padx=10)

# class selection on screen
Label(master, text=CLASS_LABEL_TEXT, font=(FONT, FONT_SIZE), \
    anchor='e').grid(row=CLASS_ROW, column=LABEL_COLUMN, sticky='E', padx=4, pady=4)
CLASS_LIST = ['N', 'C', 'T']
class_var = StringVar()
class_dropdown = OptionMenu(master, class_var, *CLASS_LIST)
class_dropdown.configure(font=(FONT, FONT_SIZE))
class_dropdown.grid(row=CLASS_ROW, column=PRIME_ENTRY_COLUMN, sticky='E', pady=4)

# Save swimmer button on screen
Button(master, text=SAVE_SWIMMTER_BUTTON_TEXT, command=save_swimmer, \
       font=(FONT, FONT_SIZE)).grid(row=BUTTONS_2_ROW, \
                                    column=SAVE_BUTTON_COLUMN, sticky='W', pady=4)

# Quit button on screen
Button(master, text=QUIT_BUTTON_TEXT, command=master.quit, \
       font=(FONT, FONT_SIZE)).grid(row=BUTTONS_2_ROW, \
                                    column=QUIT_BUTTON_COLUMN, sticky='E', pady=4)

# Help guidance on screen
help_text = "F1 for team list\n" + \
            "F3 for help to change swimmer information\n" + \
            "F4 for help to update or delete results record\n" + \
            "Ctrl-R to retrieve a results record\n"
Label(master, text=help_text, anchor='e', \
      font=(FONT, SMALL_FONT_SIZE)).grid(row=HELP_TEXT_ROW, \
                                         column=HELP_TEXT_COLUMN, sticky='W', padx=4, pady=4)

# Entry mode selection on screen
Label(master, text=ENTRY_MODE_LABEL_TEXT, font=(FONT, SMALL_FONT_SIZE), \
    anchor='ne').grid(row=ENTRY_MODE_TEXT_ROW, column=ENTRY_MODE_TEXT_COLUMN, sticky='E', \
                      padx=4, pady=4)
entry_mode_var = StringVar()
entry_mode_dropdown = OptionMenu(master, entry_mode_var, *ENTRY_MODE_LIST, \
                                 command=cb_ready_entry_mode)
entry_mode_dropdown.configure(font=(FONT, FONT_SIZE))
entry_mode_dropdown.grid(row=ENTRY_MODE_ROW, column=QUIT_BUTTON_COLUMN, sticky='E', pady=4)
entry_mode_var.set(ENTRY_MODE_LIST[0])

# Reload swimmers button on screen
Button(master, text=RELOAD_SWIMMERS_BUTTON_TEXT, command=reload_swimmers, \
   font=(FONT, FONT_SIZE)).grid(row=BUTTONS_2_ROW, \
                                    column=RELOAD_SWIMMERS_BUTTON_COLUMN, sticky='W', pady=4)

# bind special keys to functions
master.bind('<Return>', cb_reposition_cursor)
master.bind('<F1>', cb_list_teams)
master.bind('<F3>', cb_help_for_change_swimmer)
master.bind('<F4>', cb_help_for_change_result)
master.bind('<Control-r>', cb_retrieve_results_entry)
master.bind('<Control-d>', cb_delete_results_entry)
master.bind('<Control-u>', cb_update_results_entry)

mainloop()
