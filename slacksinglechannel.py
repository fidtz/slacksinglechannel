import time
import configparser
from threading import Thread
import queue
from slackclient import SlackClient
from tkinter import *
from tkinter import ttk


class ChannelWindow:
    def __init__(self, parent, messagesininit, messagesoutinit, channeldictinit, defaultchannelinit):
        """Some initialization and all the gui stuff."""
        self.parentwindow = parent

        self.channeldict = channeldictinit

        self.messagesin = messagesininit
        self.messagesout = messagesoutinit

        self.frame = ttk.Frame(root, width=40, height=1)
        self.frame.grid(row=0, column=0)

        self.messages = ttk.Label(self.frame, width=40)
        self.messages.grid(row=2, column=0)

        self.entry = ttk.Entry(self.frame, width=40)
        self.entry.grid(row=1, column=0)
        self.entry.bind("<Return>", self.update)

        self.currentchannel = StringVar()
        self.choosechannel = ttk.Combobox(self.frame,
                                          values=sorted(self.channeldict.keys()),
                                          width=30,
                                          textvariable=self.currentchannel)
        self.choosechannel.grid(row=0, column=0)
        self.choosechannel.current(sorted(self.channeldict.keys()).index(defaultchannelinit))  # start in the channel from ini file

        self.parentwindow.title(self.currentchannel.get())

        self.entry.icursor(0)
        self.entry.focus_set()

        self.update_list()

    def update(self, _):  # when enter is pressed
        if len(self.entry.get()) > 0:
            self.messagesout.put((self.channeldict[self.currentchannel.get()], self.entry.get()))  # add message to queue
            self.entry.delete(0, END)
            self.entry.icursor(0)
            self.entry.focus_set()

    def update_list(self):
        labeltext = self.messages.cget("text")
        while True:
            try:
                m = self.messagesin.get(block=False)  # cycle through messages in queue
                if m[0] == self.channeldict[self.currentchannel.get()]:  # using currently selected channel in combo box.
                    labeltext = labeltext + '\n' + m[1]
                    self.parentwindow.deiconify()
                    self.parentwindow.focus_force()
                    self.parentwindow.title(self.currentchannel.get())
                    self.entry.icursor(0)
                    self.entry.focus_set()

            except queue.Empty:
                if len(labeltext.splitlines(True)) > 30:
                    labeltext = ''.join(labeltext.splitlines(True)[1:])
                break
            if m is None:
                break
        self.messages.configure(text=labeltext)

        self.frame.after(1100, self.update_list)


def updateusers(scupuser):
    userlistraw = scupuser.api_call('users.list')
    userdictupuser = {}
    for u in userlistraw['members']:
        userdictupuser[u['id']] = (u['name'], u['real_name'])
    return userdictupuser


def updatechannels(scupdate):
    channellistraw = scupdate.api_call('channels.list')
    # print(channellistraw)
    channeldictupdate = {}
    for u in channellistraw['channels']:
        channeldictupdate[u['name']] = u['id']
    return channeldictupdate


def populatemessages(scpop, userdictpop, messagesinpop, logynpop):

    while True:
        event = scpop.rtm_read()
        if 'eventlog' not in locals() and logynpop == 'y':
            eventlog = open('eventlog.log', 'w')
        if logynpop == 'y':
            eventlog.write(str(event)+'\n')
            eventlog.flush()
        for i in event:
            if 'type' in i:
                if i['type'] == 'message' and 'user' in i and 'reply_to' not in i:
                            try:
                                currentuser = userdictpop[i['user']][0]
                            except KeyError:
                                if logynpop == 'y':
                                    eventlog.write(str(userdictpop) + '\n')
                                    eventlog.flush()
                                userdictpop = updateusers(sc)
                                currentuser = userdict[i['user']][0]
                            messagesinpop.put((i['channel'], currentuser + ' - ' + i['text']))
        time.sleep(2)


def postmessages(scpost, messagesoutpost):
    while True:
        try:
            nm = messagesoutpost.get(block=True)
            scpost.api_call('chat.postMessage', channel=nm[0], as_user='true', text=nm[1])
        except queue.Empty:
            break
        if nm is None:
            break


if __name__ == '__main__':

    config = configparser.ConfigParser()
    config.read(sys.argv[1])
    logyn = 'n'

    if 'logging' in config['default']:
        logyn = config['default']['logging']

    if len(config['default']['token']) < 10:
        print('no token found')
        sys.exit(0)

    defaultchannel = config['default']['channel']
    if len(defaultchannel) < 1:
        defaultchannel = 'general'

    sc = SlackClient(config['default']['token'])
    sc.rtm_connect()

    userdict = updateusers(sc)

    channeldict = updatechannels(sc)

    messagesin = queue.Queue()
    messagesout = queue.Queue()

    o = Thread(target=postmessages, args=(sc, messagesout))
    o.daemon = True
    o.start()

    t = Thread(target=populatemessages, args=(sc, userdict, messagesin, logyn))
    t.daemon = True
    t.start()

    root = Tk()
    newchannel = ChannelWindow(root, messagesin, messagesout, channeldict, defaultchannel)
    root.mainloop()
