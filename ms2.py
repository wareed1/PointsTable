"""
 ms.py:  Meet Summary
         Wayne Reed
         December, 2014
		 Updated:  July, 2017

         A Python program to parse the CSV results of the
         Bluefins swim meet and compile a list of winners
         including medals and overall club results

         Format of raw results file:
           event number,event description,swimmer name,swimmer number,competetive,time,\
                 valid,lane,version
           Example:
		   AA,Girls 8 & Under,100m IM,Natalie Van Winckle,509,Prescott,N,2:31.46,OK,3,v2

         Format of swimmers file:
           swimmer number,swimmer name,club,age category,competitive
           Example:
             22,Amanda Reed,Kemptville,Girls 13 & 14,N
           Added to each swimmer record:
             no. of events entered, points, results for each event
           Results for each event:
             event name, place, time


         Format of events file:
           event designator,category,event description
           Example:
             AA,Girls 8 & Under,100m IM

         Format of medals file:
           category

         To generate the participation labels, we need labels-input.txt
         created and placed in the labels subdirectory.  See the README.txt
         file in the labels subdirectory for details on participation label
         generation.

         FIXME:   should support an empty results file even though it's not
                  likely a real event issue
"""

import sys
import filemgr

# constants to make list indexing more readable
# raw results data
RD_EVNO = 0
RD_CATG = 1
RD_EVNT = 2
RD_NAME = 3
RD_SWIM = 4
RD_CLUB = 5
RD_COMP = 6
RD_TIME = 7
RD_VALD = 8
RD_LANE = 9
RD_VERS = 10
# final results data
FD_EVNO = 0
FD_CATG = 1
FD_EVNT = 2
FD_NAME = 3
FD_SWIM = 4
FD_CLUB = 5
FD_COMP = 6
FD_TIME = 7
FD_VALD = 8
FD_PLAC = 9
FD_PNTS = 10
# swimmers data
SD_SWIM = 0
SD_NAME = 1
SD_CLUB = 2
SD_CATG = 3
SD_COMP = 4
SD_NUME = 5
SD_TTLP = 6
SD_ENO1 = 7
SD_CAT1 = 8
SD_EVT1 = 9
SD_TME1 = 10
SD_PLC1 = 11
SD_ENO2 = 12
SD_CAT2 = 13
SD_EVT2 = 14
SD_TME2 = 15
SD_PLC2 = 16
SD_ENO3 = 17
SD_CAT3 = 18
SD_EVT3 = 19
SD_TME3 = 20
SD_PLC3 = 21
# events data
ED_EVNO = 0
ED_CATG = 1
ED_EVNT = 2
# club data
CD_PLAC = 0
CD_CLUB = 1
CD_NONC = 2
CD_COMP = 3
CD_TTLS = 4
CD_TTLP = 5
CD_PTPS = 6
# medal data
MD_CATG = 0
MD_NAME = 1
MD_CLUB = 2
MD_TTLP = 3

CONFIG_FILE = "ms.conf"

class Results:
    """
    An object that formulates the swim meet results
    """
    config_file = "ms.conf"
    records = ''
    swimmers = ''
    events = ''
    results_data = []
    swimmers_data = []
    events_data = []
    medals_data = []
    interim_results_data = []
    final_results_data = []
    clubs_data = []
    new_category_events = []
    events_index = 0
    arguments = ''

    def add_event_results(self, event_results, competetive):
        """ Add place and points for an event """
        if not competetive:
            points = 6
        else:
            points = 0
        event_results.sort(key=lambda elem: (elem[FD_COMP], elem[FD_TIME], elem[FD_VALD]))
        place = 1
        for index, result_record in enumerate(event_results):
            if not competetive:
                adjust_placement = result_record[FD_VALD] == 'OK' and \
                       (result_record[FD_COMP] == 'N' or \
                        'Open' in result_record[FD_CATG])
            else:
                adjust_placement = result_record[FD_VALD] == 'OK' and \
                       (result_record[FD_COMP] == 'C' or \
                        result_record[FD_COMP] == 'T') and \
                       'Open' not in result_record[FD_CATG]
            if adjust_placement:
                # add place
                self.copy_record(result_record, place, points)
                # only adjust place and points if not tie with next swimmer
                if index < len(event_results) - 1 and \
                   result_record[FD_TIME] != event_results[index + 1][FD_TIME]:
                    place += 1
                    if points > 0:
                        points -= 1
        return event_results

    def add_place_and_points(self):
        """ Complete the results with place and points for swimmers
            in each event """
        for event_index in range(len(self.events_data)):
            # assemble all results for this event
            event_results = []
            for r_index in range(len(self.interim_results_data)):
                if self.interim_results_data[r_index][FD_EVNO] == \
                   self.events_data[event_index][ED_EVNO]:
                    event_results.append(self.interim_results_data[r_index])
            if self.interim_results_data:
                # sort and save the valid results, non-competetive, lowest time results
                event_results = self.add_event_results(event_results, False)
                # sort and save the valid results, competetive, lowest time results
                event_results = self.add_event_results(event_results, True)
                place = 0
                points = 0
                # save the invalid results
                for _, result_record in enumerate(event_results):
                    if result_record[FD_VALD] != 'OK':
                        self.copy_record(result_record, place, points)
                del event_results[:]

    def add_medal_result(self, category, swimmer, club, points):
        """ Find category and add swimmer to list of medalists """
        for index in range(len(self.medals_data)):
            if self.medals_data[index][0] == category:
                if len(self.medals_data[index]) == 1:
                    # first entry
                    self.medals_data[index].append(swimmer)
                    self.medals_data[index].append(club)
                    self.medals_data[index].append(points)
                    return
                # a tie
                new_record = []
                new_record.append(category)
                new_record.append(swimmer)
                new_record.append(club)
                new_record.append(points)
                self.medals_data.insert(index, new_record)

    def compile_club_results(self):
        """ For each swim club, count points """
        #
        # Steps to take to compile club results:
        #    Sort swimmer results on:
        #       club
        #    Each club result record is:
        #       club name
        #       number of non-competitive swimmers
        #       number of competitive swimmers
        #       total number of swimmers
        #       total number of points
        #       points per swimmer
        sorted_list = sorted(self.swimmers_data, key=lambda x: x[SD_CLUB])
        club = ''
        for index, club_entry in enumerate(sorted_list):
            if not club or club != club_entry[SD_CLUB]:
                club = club_entry[SD_CLUB]
                record = []
                record.append(0)
                record.append(club_entry[SD_CLUB])
                record.append(0)
                record.append(0)
                record.append(0)
                record.append(0)
                record.append(0)
                self.clubs_data.append(record)
            if club_entry[SD_COMP] == 'N' and club_entry[SD_NUME] > 0:
                self.clubs_data[-1][CD_NONC] += 1
                self.clubs_data[-1][CD_TTLS] += 1
                self.clubs_data[-1][CD_TTLP] += club_entry[6]
            elif club_entry[SD_COMP] == 'C' and club_entry[SD_NUME] > 0:
                self.clubs_data[-1][CD_COMP] += 1
                self.clubs_data[-1][CD_TTLS] += 1
            else:
                # no error with this version
                pass
        for index in range(len(self.clubs_data)):
            if self.clubs_data[index][CD_NONC] == 0:
                points_per_swimmer = 0
            else:
                points_per_swimmer = float(self.clubs_data[index][CD_TTLP]) /\
                                           float(self.clubs_data[index][CD_NONC])
            self.clubs_data[index][CD_PTPS] = points_per_swimmer
        self.clubs_data.sort(key=lambda x: x[CD_PTPS])
        finish = len(self.clubs_data)
        for index in range(len(self.clubs_data)):
            self.clubs_data[index][CD_PLAC] = finish
            finish -= 1

    @staticmethod
    def compile_in_reverse_order(event_finishers, event_number, event_results_text):
        """ Assemble the results in reverse order to make it
            easier for the announcer to present """
        competitive = ''
        for index, finisher in enumerate(event_finishers):
            if finisher[FD_PLAC] > 0 and \
               finisher[FD_PLAC] <= 6:
                # highlight competitive swimmers
                if finisher[FD_COMP] == 'C' and not competitive:
                    competitive = finisher[FD_COMP]
                    if 'Open' not in event_finishers[index][FD_CATG] and \
                       (event_number < '67' or event_number == 'AA' \
                        or event_number == 'BB'):
                        event_results_text.append('\tCOMPETITIVE CATEGORY:')
                record = '%3s' % str(finisher[FD_PLAC]) + '\t\t' +\
                         '%-25s' % finisher[FD_NAME] + '\t\t' +\
                         '%15s' % finisher[FD_CLUB]
                event_results_text.append(record)
        return event_results_text

    def compile_medal_results(self):
        """ For each medal category, find top swimmer(s) """
        #
        # Steps to take to compile medal results:
        #    Sort final results on:
        #        reverse swimmer category and number of points
        #
        sorted_list = sorted(self.swimmers_data, key=lambda x: (x[SD_CATG], \
                             x[SD_TTLP]), reverse=True)
        category = ''
        points = 0
        for index, swimmer_entry in enumerate(sorted_list):
            if swimmer_entry[SD_TTLP] != 0:
                # swimmer has some points
                if not category or swimmer_entry[SD_CATG] != category:
                    category = swimmer_entry[SD_CATG]
                    points = swimmer_entry[SD_TTLP]
                    self.add_medal_result(category, swimmer_entry[SD_NAME], \
                                          swimmer_entry[SD_CLUB], points)
                elif sorted_list[index][SD_TTLP] == points:
                    # duplicate
                    self.add_medal_result(category, swimmer_entry[SD_NAME], \
                                          swimmer_entry[SD_CLUB], points)

    def compile_swimmer_results(self):
        """ For each swimmer, expand to full results """
        #
        # Steps to take for each swimmer:
        #    Add number of events entered
        #    Add total points accumulated
        #    Add results for each event:
        #        event number
        #        event name
        #        place
        #        time
        #
        for r_index in range(len(self.final_results_data)):
            s_index = self.find_swimmer_by_number(\
                      self.final_results_data[r_index][FD_SWIM])
            if s_index == -1:
                exception_text = "cannot find swimmer #" + \
                                 self.final_results_data[r_index][FD_SWIM]
                raise LookupError(exception_text)
            events = self.swimmers_data[s_index][SD_NUME] + 1
            self.swimmers_data[s_index][SD_NUME] = events
            points = self.swimmers_data[s_index][SD_TTLP] + \
                     self.final_results_data[r_index][FD_PNTS]
            self.swimmers_data[s_index][SD_TTLP] = points
            self.swimmers_data[s_index].append(self.final_results_data[r_index][FD_EVNO])
            self.swimmers_data[s_index].append(self.final_results_data[r_index][FD_CATG])
            self.swimmers_data[s_index].append(self.final_results_data[r_index][FD_EVNT])
            self.swimmers_data[s_index].append(self.final_results_data[r_index][FD_TIME])
            self.swimmers_data[s_index].append(self.final_results_data[r_index][FD_PLAC])

    def copy_record(self, record, place, points):
        """ Add place and points and copy record to final results """
        record.append(place)
        record.append(points)
        self.final_results_data.append(record)

    def create_club_results_file(self, filename, title):
        """ Create the file with the information for the
            announcer to present the club results """
        club_results_text = []
        club_results_text.append('\t\t\t\t\t\t\t' + title)
        club_results_text.append('\t\t\t\t\t\t\t\tClub Results')
        club_results_text.append(\
            '-------------------------------------------------------------------------')
        club_results_text.append(\
            '\t\t\t\t\t\t\tNO. OF\tNO. OF\t  TTL\t\t CLUB\t  PTS PER')
        club_results_text.append(\
            'PLACE\tCLUB\t\t\t\tNON-C\tCOMPT\tSWIMMERS\tPOINTS\t  SWIMMER')
        club_results_text.append(\
            '-------------------------------------------------------------------------')
        for index in range(len(self.clubs_data)):
            record = '%3s' % str(self.clubs_data[index][CD_PLAC]) + '\t\t' +\
                     '%-15s' % self.clubs_data[index][CD_CLUB] + '\t\t' +\
                     '%5s' % str(self.clubs_data[index][CD_NONC]) + '\t' +\
                     '%5s' % str(self.clubs_data[index][CD_COMP]) + '\t' +\
                     '%5s' % str(self.clubs_data[index][CD_TTLS]) + '\t\t' +\
                     '%5s' % str(self.clubs_data[index][CD_TTLP]) + '\t\t' +\
                     '%5.2f' % self.clubs_data[index][CD_PTPS]
            club_results_text.append(record)
        club_results_text.append(\
            '-------------------------------------------------------------------------')
        filemgr.write_file(filename, club_results_text)

    def create_event_results_file(self, filename, title):
        """ Create the file with the information for the
            announcer to present the event results """
        event_results_text = []
        event_number = self.final_results_data[0][FD_EVNO]
        event_name = self.final_results_data[0][FD_EVNT]
        event_category = self.final_results_data[0][FD_CATG]
        event_results_text.append('\t\t\t\t\t' + title)
        event_results_text.append('\t\t\t\t\t\tEvent Results')
        event_finishers = []
        r_index = 0
        for r_index in range(len(self.final_results_data)):
            # if this record is the last or the next record is for a different event
            if r_index == (len(self.final_results_data) - 1) or \
               self.final_results_data[r_index + 1][FD_EVNO] != event_number:
                event_finishers.append(self.final_results_data[r_index])
                event_results_text.append('')
                event_results_text.append(\
                    'Event #' + event_number + ': ' + event_category + ', ' + event_name)
                event_results_text.append(\
                    '-------------------------------------------------------')
                event_results_text.append('PLACE\tSWIMMER\t\t\t\t\t\t\t\t\tCLUB')
                event_results_text.append(\
                    '-------------------------------------------------------')
                # sort and save the valid results, non-competetive, lowest time results
                event_finishers.sort(key=lambda elem: \
                    (elem[FD_VALD], elem[FD_COMP], elem[FD_TIME]), reverse=True)
                event_results_text = self.compile_in_reverse_order(event_finishers,\
                                                                   event_number, \
                                                                   event_results_text)
                del event_finishers[:]
                # if not at the end of the event results, set up for next one
                if r_index != (len(self.final_results_data) - 1):
                    event_number = self.final_results_data[r_index + 1][FD_EVNO]
                    event_name = self.final_results_data[r_index + 1][FD_EVNT]
                    event_category = self.final_results_data[r_index + 1][FD_CATG]
            else:
                event_finishers.append(self.final_results_data[r_index])
        event_results_text.append('-------------------------------------------------------')
        filemgr.write_file(filename, event_results_text)

    def create_medal_results_file(self, filename, title):
        """ Create the file with the information for the
            announcer to present the medal results """
        medal_results_text = []
        medal_results_text.append('\t\t\t\t\t\t\t' + title)
        medal_results_text.append('\t\t\t\t\t\t\t\t\tMedalists')
        medal_results_text.append(\
            '--------------------------------------------------------------------------')
        medal_results_text.append(\
            '\tCATEGORY\t\t\tSWIMMER\t\t\t\t\t\tCLUB\t\t\tPOINTS')
        medal_results_text.append(\
            '--------------------------------------------------------------------------')
        for index in range(len(self.medals_data)):
            if len(self.medals_data[index]) == 1:
                # only the header, no swimmers
                record = '%-20s' % self.medals_data[index][MD_CATG] + '\t' +\
                         "No finishers in this category"
            else:
                record = '%-20s' % self.medals_data[index][MD_CATG] + '\t' +\
                         '%-25s' % self.medals_data[index][MD_NAME] + '\t' +\
                         '%-15s' % self.medals_data[index][MD_CLUB] + '\t' +\
                         '%5s' % str(self.medals_data[index][MD_TTLP])
            if index == 0 or self.medals_data[index][MD_CATG] != \
               self.medals_data[index - 1][MD_CATG]:
                # separate categories with line spacing to make easier to read
                medal_results_text.append('')
            medal_results_text.append(record)
        medal_results_text.append(\
            '--------------------------------------------------------------------------')
        filemgr.write_file(filename, medal_results_text)

    def create_meet_results_file(self, filename):
        """ Create the summary file of the event results, CSV format """
        meet_results_text = []
        meet_results_text.append(\
            'EVNT#,CATEGORY,EVENT,SWIMMER,NUMBER,CLUB,CLASS,TIME,ACCEPT,PLACE,POINTS')
        for index in range(len(self.final_results_data)):
            record = self.final_results_data[index][FD_EVNO] + ',' +\
                     self.final_results_data[index][FD_CATG] + ',' +\
                     self.final_results_data[index][FD_EVNT] + ',' +\
                     self.final_results_data[index][FD_NAME] + ',' +\
                     self.final_results_data[index][FD_SWIM] + ',' +\
                     self.final_results_data[index][FD_CLUB] + ',' +\
                     self.final_results_data[index][FD_COMP] + ',' +\
                     self.final_results_data[index][FD_TIME] + ',' +\
                     self.final_results_data[index][FD_VALD] + ',' +\
                     str(self.final_results_data[index][FD_PLAC]) + ',' +\
                     str(self.final_results_data[index][FD_PNTS])
            meet_results_text.append(record)
        filemgr.write_file(filename, meet_results_text)

    def create_labels_file(self, filename):
        """ Create the file with the information for the
            participation labels """
        labels_text = []
        for index in range(len(self.swimmers_data)):
            # add swimmer information
            record = self.swimmers_data[index][SD_NAME] + ' (' +\
                     self.swimmers_data[index][SD_SWIM] + ') : ' +\
                     self.swimmers_data[index][SD_CLUB] + ',' +\
                     self.swimmers_data[index][SD_CATG] + ','
            # add event results
            if len(self.swimmers_data[index]) >= SD_PLC1 + 1:
                place_text = self.format_place(self.swimmers_data[index][SD_PLC1])
                record += place_text + ' ' + \
                self.swimmers_data[index][SD_EVT1] + ' [' +\
                self.swimmers_data[index][SD_TME1] + ']'
            if len(self.swimmers_data[index]) >= SD_PLC2 + 1:
                place_text = self.format_place(self.swimmers_data[index][SD_PLC2])
                record += ',' + place_text + ' ' + \
                self.swimmers_data[index][SD_EVT2] + ' [' +\
                self.swimmers_data[index][SD_TME2] + ']'
            if len(self.swimmers_data[index]) >= SD_PLC3 + 1:
                place_text = self.format_place(self.swimmers_data[index][SD_PLC3])
                record += ',' + place_text + ' ' + \
                self.swimmers_data[index][SD_EVT3] + ' [' +\
                self.swimmers_data[index][SD_TME3] + ']'
            labels_text.append(record)
        filemgr.write_file(filename, labels_text)

    def create_swimmers_page(self, filename):
        """ Create a web page of individual swimmer results """
        swimmers_results_text = []
        pt_all_text = []
        club = ''
        sorted_list = sorted(self.swimmers_data, key=lambda x: x[SD_CLUB])
        for _, swimmer in enumerate(sorted_list):
            if not club or club != swimmer[SD_CLUB]:
                if club != swimmer[SD_CLUB]:
                    swimmers_results_text.append('</table>')
                    swimmers_results_text.append('</body>\n</html>')
                club = swimmer[SD_CLUB]
                swimmers_results_text.append('<font size="6" color="green">')
                swimmers_results_text.append('<br>Club:' + club + '<br>')
                swimmers_results_text.append('</font>')
                swimmers_results_text.append('<!DOCTYPE html>\n<html>\n<head>\n<style>')
                swimmers_results_text.append('table, th, td {\nborder: 1px solid black;\n}')
                swimmers_results_text.append('TD{font-family: Arial; font-size: 16pt;}')
                swimmers_results_text.append('TH{font-family: Arial; font-size: 18pt;}')
                swimmers_results_text.append('</style>\n</head>\n<body>')
                swimmers_results_text.append('<table style=width:100%>')
                swimmers_results_text.append('<tr>')
                swimmers_results_text.append('<th>' + 'SWIMMER' + '</th>' +\
                             '<th>' + 'NUMBER' + '</th>' +\
                             '<th>' + 'CATEGORY' + '</th>' +\
                             '<th>' + 'CLASS' + '</th>' +\
                             '<th>' + '# EVENTS' + '</th>' +\
                             '<th>' + 'POINTS' + '</th>')
                swimmers_results_text.append('</tr>')
            # only show results for swimmers that entered one or more events
            if swimmer[SD_NUME] > 0:
                swimmers_results_text.append('<tr>')
                record = '<td align="center">' + swimmer[SD_NAME] + '</td>' +\
                         '<td align="center">' + swimmer[SD_SWIM] + '</td>' +\
                         '<td align="center">' + swimmer[SD_CATG] + '</td>' +\
                         '<td align="center">' + swimmer[SD_COMP] + '</td>' +\
                         '<td align="center">' + str(swimmer[SD_NUME]) + '</td>' +\
                         '<td align="center">' + str(swimmer[SD_TTLP]) + '</td>'
                swimmers_results_text.append(record)
                swimmers_results_text.append('</tr>')
        swimmers_results_text.append('</table>')
        swimmers_results_text.append('</body>\n</html>')
        for _, line in enumerate(swimmers_results_text):
            pt_all_text.append(line)
        del swimmers_results_text[:]
        pt_all_text.insert(0, '<br><br>')
        pt_all_text.insert(0, '</font>')
        pt_all_text.insert(0, '<span style="margin-left:0em">' + MEET_NAME + '</span>')
        pt_all_text.insert(0, '<font size="5" color="blue">')
        pt_all_text.insert(0, '<br>')
        filemgr.write_file(filename, pt_all_text)

    def create_swimmers_results_file(self, filename, title):
        """ For each swim club, summarize results for each swimmer """
        #
        # Steps to take to compile club results:
        #    Sort swimmer results on:
        #       club
        swimmers_results_text = []
        swimmers_results_text.append('\t\t\t\t\t\t\t' + title)
        swimmers_results_text.append('\t\t\t\t\t\t\t\t\tSwimmers')
        sorted_list = sorted(self.swimmers_data, key=lambda x: x[SD_CLUB])
        club = ''
        for _, club_entry in enumerate(sorted_list):
            if not club or club != club_entry[SD_CLUB]:
                club = club_entry[SD_CLUB]
                swimmers_results_text.append('\n\t\tClub:  ' + club)
                swimmers_results_text.append(\
                    '----------------------------------------------------------\
-----------------------------------------------------------\
-----------------------------------------------------------\
-----------------------------------------------------------\
------------------------------------')
                swimmers_results_text.append(\
                    '\tSWIMMER\t\t\t\t\tNUMBER\t\tCATEGORY\t\t\t\
COMP\tEVTS\tPTS\tEVT 1\tCATEGORY 1\t\t\tEVENT 1\t\t\t\tTIME 1\t\
PLACE 1\tEVT 2\tCATEGORY 2\t\t\tEVENT 2\t\t\t\tTIME 2\tPLACE 2\t\
EVT 3\tCATEGORY 3\t\t\tEVENT 3\t\t\t\tTIME 3\tPLACE 3')
                swimmers_results_text.append(\
                    '----------------------------------------------------------\
-----------------------------------------------------------\
-----------------------------------------------------------\
-----------------------------------------------------------\
------------------------------------')
            record = '%-25s' % club_entry[SD_NAME] + '\t' +\
                     '%5s' % club_entry[SD_SWIM] + '\t' +\
                     '%-20s' % club_entry[SD_CATG] + '\t' +\
                     '%3s' % club_entry[SD_COMP]  + '\t' +\
                     '%6s' % str(club_entry[SD_NUME]) + '\t' +\
                     '%6s' % str(club_entry[SD_TTLP])
            if club_entry[SD_NUME] > 0:
                record = record + '%6s' % club_entry[SD_ENO1] + '\t' +\
                     '%-16s' % club_entry[SD_CAT1] + '\t' +\
                     '%-16s' % club_entry[SD_EVT1] + '\t' +\
                     '%-10s' % club_entry[SD_TME1] + '\t' +\
                     '%3s' % str(club_entry[SD_PLC1])
            if club_entry[SD_NUME] > 1:
                record = record + '%6s' % club_entry[SD_ENO2] + '\t' +\
                     '%-16s' % club_entry[SD_CAT2] + '\t' +\
                     '%-16s' % club_entry[SD_EVT2] + '\t' +\
                     '%-10s' % club_entry[SD_TME2] + '\t' +\
                     '%3s' % str(club_entry[SD_PLC2])
            if club_entry[SD_NUME] > 2:
                record = record + '%6s' % club_entry[SD_ENO3] + '\t' +\
                     '%-16s' % club_entry[SD_CAT3] + '\t' +\
                     '%-16s' % club_entry[SD_EVT3] + '\t' +\
                     '%-10s' % club_entry[SD_TME3] + '\t' +\
                     '%3s' % str(club_entry[SD_PLC3])
            swimmers_results_text.append(record)
        filemgr.write_file(filename, swimmers_results_text)

    def create_pt_monitor_file(self, filename):
        """ Create the file with the information for the points table team
            to validate event results on input """
        pt_monitor_text = []
        pt_all_text = []
        event_number = self.final_results_data[0][FD_EVNO]
        event_name = self.final_results_data[0][FD_EVNT]
        event_category = self.final_results_data[0][FD_CATG]
        event_finishers = []
        r_index = 0
        for r_index in range(len(self.final_results_data)):
            # if this record is the last or the next record is for a different event
            if r_index == (len(self.final_results_data) - 1) or \
               self.final_results_data[r_index + 1][FD_EVNO] != event_number:
                event_finishers.append(self.final_results_data[r_index])
                pt_monitor_text.insert(0, '<font size="4" color="green">')
                pt_monitor_text.insert(0, 'Event #' + event_number + ': ' + \
                                          event_category + ', ' + event_name + '<br>')
                pt_monitor_text.insert(0, '</font>')
                pt_monitor_text.insert(0, '<!DOCTYPE html>\n<html>\n<head>\n<style>')
                pt_monitor_text.insert(0, 'table, th, td {\nborder: 1px solid black;\n}')
                pt_monitor_text.insert(0, 'TD{font-family: Arial; font-size: 16pt;}')
                pt_monitor_text.insert(0, 'TH{font-family: Arial; font-size: 18pt;}')
                pt_monitor_text.insert(0, '</style>\n</head>\n<body>')
                pt_monitor_text.insert(0, '<table style=width:100%>')
                pt_monitor_text.insert(0, '<tr>')
                pt_monitor_text.insert(0, '<th>' + 'SWIMMER / TEAM' + '</th>' +\
                             '<th>' + 'CLUB' + '</th>' +\
                             '<th>' + 'TIME' + '</th>' +\
                             '<th>' + 'PLACE' + '</th>' +\
                             '<th>' + 'CLASS' + '</th>' +\
                             '<th>' + 'OK?' + '</th>')
                pt_monitor_text.insert(0, '</tr>')
                for _, finisher in enumerate(event_finishers):
                    pt_monitor_text.insert(0, '<tr>')
                    record = '<td align="center">' + \
                             finisher[FD_NAME] + '</td>' +\
                             '<td align="center">' + \
                             finisher[FD_CLUB] + '</td>' +\
                             '<td align="center">' + \
                             finisher[FD_TIME] + '</td>' +\
                             '<td align="center">' + \
                             str(finisher[FD_PLAC]) + '</td>' +\
                             '<td align="center">' + \
                             finisher[FD_COMP] + '</td>' +\
                             '<td align="center">' + \
                             finisher[FD_VALD] + '</td>'
                    pt_monitor_text.insert(0, record)
                    pt_monitor_text.insert(0, '</tr>')
                pt_monitor_text.insert(0, '</table>')
                pt_monitor_text.insert(0, '</body>\n</html>')
                del event_finishers[:]
                for _, line in enumerate(pt_monitor_text):
                    pt_all_text.insert(0, line)
                del pt_monitor_text[:]
                # if not at the end of the event results, set up for next one
                if r_index != (len(self.final_results_data) - 1):
                    event_number = self.final_results_data[r_index + 1][FD_EVNO]
                    event_name = self.final_results_data[r_index + 1][FD_EVNT]
                    event_category = self.final_results_data[r_index + 1][FD_CATG]
            else:
                event_finishers.append(self.final_results_data[r_index])
        pt_all_text.insert(0, '<br><br>')
        pt_all_text.insert(0, '</font>')
        pt_all_text.insert(0, '<span style="margin-left:0em">' + MEET_NAME + '</span>')
        pt_all_text.insert(0, '<font size="5" color="blue">')
        pt_all_text.insert(0, '<br>')
        filemgr.write_file(filename, pt_all_text)

    def find_swimmer_by_number(self, swimmer_number):
        """ Match the swimmer number to swimmer name
            and return the index of the match """
        element = 0
        swimmer_reference = -1
        while element < len(self.swimmers_data):
            if swimmer_number == self.swimmers_data[element][SD_SWIM]:
                swimmer_reference = element
                # done: last iteration of search
                element = len(self.swimmers_data)
            else:
                element += 1
        return swimmer_reference

    def find_event_index(self, event):
        """ Match the event to index in the list of events
            and return the index of the match """
        element = 0
        event_reference = -1
        while element < len(self.events_data):
            if event == self.events_data[element][ED_EVNO]:
                event_reference = element
                # done: last iteration of search
                element = len(self.events_data)
            else:
                element += 1
        return event_reference

    @staticmethod
    def format_place(place):
        """ Produce text for place finished """
        if place == 0:
            return 'n/a'
        if place == 1:
            return '1st'
        if place == 2:
            return '2nd'
        if place == 3:
            return '3rd'
        return str(place) + 'th'

    def process_results(self):
        """ For each raw result, expand to full information """
        #
        # Steps to take for each record [source]:
        #    Add event number
        #    Add event category
        #    Add event
        #    Add swimmer name
        #    Add swimmer number
        #    Add club
        #    Add competitive designation
        #    Add time
        #    Add heat (maybe)
        #    Add results valid?
        #    Add place
        #    Add points earned
        # Example expanded record w/o heat:
        # AA,Girls 8 & Under,100m IM,Brooklin McNeely,Kemptville,N,02:26:32,OK,1,6
        #
        for index in range(len(self.results_data)):
            # ignore blank lines
            if self.results_data[index][RD_EVNO]:
                event_index = self.find_event_index(self.results_data[index][RD_EVNO])
                if event_index == -1:
                    exception_text = "records file, line # " + str(index + 1) + \
                                     ": cannot find event index " + \
                                     self.results_data[index][RD_EVNO]
                    raise LookupError(exception_text)
                s_index = self.find_swimmer_by_number(self.results_data[index][RD_SWIM])
                if s_index == -1:
                    exception_text = "records file, line # " + str(index + 1) + \
                                     ": cannot find swimmer #" + self.results_data[index][RD_SWIM]
                    raise LookupError(exception_text)
                # format final results record
                results_record = []
                results_record.append(self.events_data[event_index][ED_EVNO])
                results_record.append(self.events_data[event_index][ED_CATG])
                results_record.append(self.events_data[event_index][ED_EVNT])
                results_record.append(self.swimmers_data[s_index][SD_NAME])
                results_record.append(self.swimmers_data[s_index][SD_SWIM])
                results_record.append(self.swimmers_data[s_index][SD_CLUB])
                results_record.append(self.swimmers_data[s_index][SD_COMP])
                results_record.append(self.results_data[index][RD_TIME])
                results_record.append(self.results_data[index][RD_VALD])
                # save record in final results
                self.interim_results_data.append(results_record)
        # add place and points
        self.add_place_and_points()

# main
RESULTS = Results()
filemgr.read_file(CONFIG_FILE, filemgr.CONFIG_DATA, filemgr.MULTI_DIMENSION)
MEET_NAME = filemgr.get_value("meet")
print("Meet Statistics v0.4")
print("program name: " + sys.argv[0])
filemgr.read_file(RESULTS.config_file, filemgr.CONFIG_DATA, filemgr.MULTI_DIMENSION)
filemgr.read_file(filemgr.get_value("raw_results_file"), \
                  RESULTS.results_data, filemgr.MULTI_DIMENSION)
filemgr.read_file(filemgr.get_value("swimmers_file"), \
                  RESULTS.swimmers_data, filemgr.MULTI_DIMENSION)
filemgr.read_file(filemgr.get_value("events_file"), \
                  RESULTS.events_data, filemgr.MULTI_DIMENSION)
# add placeholder for number of events and points
for data_index in range(len(RESULTS.swimmers_data)):
    RESULTS.swimmers_data[data_index].append(0)
    RESULTS.swimmers_data[data_index].append(0)
filemgr.read_file(filemgr.get_value("medals_file"), RESULTS.medals_data, \
                  filemgr.MULTI_DIMENSION)
CREATE_SWIMMERS_PAGE = filemgr.get_value("create_swimmers_page")

# process raw results into full results
RESULTS.process_results()

# compile swimmer results
RESULTS.compile_swimmer_results()

# compile medal results
RESULTS.compile_medal_results()

# compile club results
RESULTS.compile_club_results()

# produce the file used to create the participation labels
RESULTS.create_labels_file(filemgr.get_value("labels_file"))

# produce the file used by the announcer to share event results
RESULTS.create_event_results_file(filemgr.get_value("event_results_file"), \
                                  filemgr.get_value("meet"))

# produce the file used by the announcer to share medal results
RESULTS.create_medal_results_file(filemgr.get_value("medal_results_file"), \
                                  filemgr.get_value("meet"))

# produce the file used by the announcer to share club results
RESULTS.create_club_results_file(filemgr.get_value("club_results_file"), \
                                 filemgr.get_value("meet"))

# save the final results
RESULTS.create_meet_results_file(filemgr.get_value("final_results_file"))

# save the swimmers results
RESULTS.create_swimmers_results_file(filemgr.get_value("swimmers_results_file"), \
                                     filemgr.get_value("meet"))

# produce the file used by the points table team to validate input
RESULTS.create_pt_monitor_file(filemgr.get_value("pt_monitor_file"))

# create web page of swimmers results
if CREATE_SWIMMERS_PAGE == "True":
    RESULTS.create_swimmers_page(filemgr.get_value("pt_swimmers_results_file"))
