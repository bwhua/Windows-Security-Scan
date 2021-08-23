import platform
#imports the scan file based on what OS the computer is on
if (platform.system() == 'Windows'):
    import scan_windows as scan
elif(platform.system() == 'Darwin'):
    import scan_mac as scan
elif(platform.system() == 'Linux'):
    import scan_linux as scan

from tkinter import *
import json
import time
import os.path

# This class manages all of the frames (the other classes) that are being showed
class ramscan(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        self.container = Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        #Check if program has computer_info.json. if not, make one
        if not os.path.isfile('computer_info.json'):
            scan.make_json()
        # create the frames & append to frames dict
        self.frames = {}

        # create the frames & append to frames dict
        # puts all of the classes in the list frames
        for F in (info_screen, loading_screen, credits):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("info_screen")

    #This shows the frame that was given as an arguement
    def show_frame(self, page_name):
        for frame in self.frames.values():
            frame.grid_remove()
        # we do this because it's the only non-static page, this is 'refreshing' the page
        if (page_name == 'info_screen'):
            frame = info_screen(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        frame = self.frames[page_name]
        frame.grid()

class info_screen(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        self.header = StringVar()
        self.header.set('Attribute')

        self.information = StringVar()
        self.information.set('Information about the attribute will be displayed here')
        self.importance = StringVar()
        self.importance.set('If you click the \'i\' next to the attribute, you will see why it is important')

        top_frame = Frame(self, bg='cyan', width=450, height=50, pady=3)
        center = Frame(self, bg='gray2', width=50, height=40, padx=3, pady=3)
        btm_frame = Frame(self, bg='white', width=450, height=45, pady=3)
        btm_frame2 = Frame(self, bg='lavender', width=450, height=60, pady=3)
        # layout all of the main containers
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        top_frame.grid(row=0, sticky="ew")
        center.grid(row=1, sticky="nsew")
        btm_frame.grid(row=3, sticky="ew")
        btm_frame2.grid(row=4, sticky="ew")

        #add our logo to the GUI
        logo_photo = PhotoImage(file="images/logo.png")
        logo_img = Label(top_frame, image=logo_photo)
        logo_img.image = logo_photo # keep a reference!
        logo_img.grid(row=0, rowspan=3, column=0, padx=150, pady=2, sticky='e')

        Label(top_frame, text='Ram Scan', font=('Times New Roman', 20)).grid(row=0, column= 1, padx=3, pady=3, sticky='nsew')
        basic = Label(top_frame, text=self.nested_data('Basic Info'), justify='left').grid(row=1, column=1, padx=3, pady=2)
        date = Label(top_frame, text=self.nested_data('Date')).grid(row=2, column=1, padx=3, pady=2)

        Button(top_frame, text="Re-scan your system", command = lambda: self.popup()).grid(row=2, column=3, padx=3, pady=2)

        # create the center, center_left, and center_right widgets
        center.grid_rowconfigure(0, weight=1)
        center.grid_columnconfigure(1, weight=1)
        ctr_left = Frame(center, bg='blue', width=100, height=190)
        ctr_mid = Frame(center, bg='yellow', width=1000, height=190, padx=3, pady=3)
        ctr_right = Frame(center, bg='green', width=100, height=190, padx=3, pady=3)
        scrollbar = Scrollbar(ctr_mid)
        scrollbar.pack(side='right', fill='y')
        # This creates the area in which text will appear for nested data
        self.text = Text(ctr_mid, wrap='word', yscrollcommand=scrollbar.set, width = 100)
        self.text.pack()
        scrollbar.config(command=self.text.yview)
        # tells it which alignment the text has
        ctr_left.grid(row=0, column=0, sticky="ns")
        ctr_mid.grid(row=0, column=1, sticky="nsew")
        ctr_right.grid(row=0, column=2, sticky="ns")

        #create buttons and labels for single information
        Label(ctr_left, text="Click on the i to see more information", font=('Times New Roman', 12)).grid(row=1, columnspan=2, padx=3, pady=3)
        Button(ctr_left, text=' i ',  command=lambda: self.description('Firewall')).grid(row=2, column=0, padx=3, pady=2)
        Button(ctr_left, text=' i ', command=lambda: self.description('Screen Lock')).grid(row=3, column=0, padx=3, pady=2)
        Button(ctr_left, text=' i ', command=lambda: self.description('Remote Login')).grid(row=4, column=0, padx=3, pady=2)
        Button(ctr_left, text=' i ', command=lambda: self.description('IP Address')).grid(row=5, column=0, padx=3, pady=2)
        Button(ctr_left, text=' i ', command=lambda: self.description('MAC Address')).grid(row=6, column=0, padx=3, pady=2)
        Button(ctr_left, text=' i ', command=lambda: self.description('Memory')).grid(row=7, column=0, padx=3, pady=2)
        Label(ctr_left, text=self.single_data('Screen Lock'), justify='left').grid(row=3, column=1, padx=3, pady=3, sticky='w')
        Label(ctr_left, text=self.single_data('Remote Login')).grid(row=4, column=1, padx=3, pady=3, sticky='w')
        Label(ctr_left, text=self.single_data('IP Address')).grid(row=5, padx=3, column=1, pady=3, sticky='w')
        Label(ctr_left, text=self.single_data('MAC Address')).grid(row=6, padx=3, column=1, pady=3, sticky='w')
        Label(ctr_left, text=self.nested_data('Memory')).grid(row=7, column=1, padx=3, pady=3, sticky='w')

        #create buttons for nested data information
        Label(ctr_right, text="Click on the category to get the specifics\nClick on the i to see more information", font=('Times New Roman', 12)).grid(row=1, columnspan=2, padx=3, pady=3, sticky='w')
        Button(ctr_right, text=' i ', command=lambda: self.description('Wi-Fi Info')).grid(row=2, column=0, padx=3, pady=2)
        Button(ctr_right, text=' i ', command=lambda: self.description('Wi-Fi History')).grid(row=3, column=0, padx=3, pady=2)
        Button(ctr_right, text=' i ', command=lambda: self.description('Software')).grid(row=4, column=0, padx=3, pady=2)
        Button(ctr_right, text=' i ', command=lambda: self.description('Startup Programs')).grid(row=5, column=0, padx=3, pady=2)
        Button(ctr_right, text=' i ', command=lambda: self.description('Updates')).grid(row=6, column=0, padx=3, pady=2)
        Button(ctr_right, text=' i ', command=lambda: self.description('Open Ports')).grid(row=7, column=0, padx=3, pady=2)
        Button(ctr_right, text=' i ', command=lambda: self.description('Disk Encryption')).grid(row=8, column=0, padx=3, pady=2)

        Button(ctr_right, text="WiFi Info", command=lambda: self.nested_data('Wi-Fi Info')).grid(row=2, column=1, padx=3, pady=3, sticky='w')
        Button(ctr_right, text="WiFi History", command=lambda: self.nested_data('Wi-Fi History')).grid(row=3, padx=3, column=1, pady=3, sticky='w')
        Button(ctr_right, text="Software", command=lambda: self.nested_data('Software')).grid(row=4, column=1, padx=3, pady=3, sticky='w')
        Button(ctr_right, text="Startup Programs", command=lambda: self.nested_data('Startup Programs')).grid(row=5, column=1, padx=3, pady=3, sticky='w')
        Button(ctr_right, text="Available Updates", command=lambda: self.nested_data('Updates')).grid(row=6, padx=3, column=1, pady=3, sticky='w')
        Button(ctr_right, text="Open Ports", command=lambda: self.nested_data('Open Ports')).grid(row=7, column=1, padx=3, pady=3, sticky='w')
        Button(ctr_right, text="Open disk encryption via control panel", command=self.open_disk_encryption).grid(row=8, column=1, padx=3, pady=3, sticky='w')

        #Create Labels for what information is being displayed and why it's important
        Label(btm_frame, textvariable=self.header, justify='left', wraplength=600, font=('Times New Roman', 20)).pack()
        Label(btm_frame, textvariable=self.information, justify='left', wraplength=600, font=('Times New Roman', 14)).pack()
        Label(btm_frame2, textvariable=self.importance, justify='left', wraplength=600, font=('Times New Roman', 14)).pack()
        firewall = Label(ctr_left, text=self.single_data('Firewall')).grid(row=2, column=1, padx=3, pady=3, sticky='w')
    # This popup appears when the re-scan system but
    def popup(self):
        self.win = Toplevel()
        self.win.wm_title("Please Confirm")
        label = Label(self.win, text="Please let the program run. \nIt may look like it's frozen or not responding \nIt takes around a minute\n")
        label.grid(row=0, column=0)
        cancel_button = Button(self.win, text="Cancel", command=self.win.destroy)
        cancel_button.grid(row=1, column=0)
        ok_button = Button(self.win, text="Okay", command=self.popup_ok)
        ok_button.grid(row=1, column=1)
    #This is the code that executes when the 'okay' button is pushed on the popup
    def popup_ok(self):
        self.rescan()
        self.win.destroy()
    #formats wifi info from json file and writes it the the center_mid frame
    def display_wifi_info(self, info):
        result = 'Here are visible Wi-Fi connections:'
        keys = list(info)
        for i in range(len(info)):
            ssid = keys[i]
            dict = info[ssid]
            auth = dict['Authentication']
            encryption = dict['Encryption']
            net_type = dict['Network Type']
            result += ('\n\tSSID: %s\n\t\tAuthentication: %s\n\t\tEncryption: %s\n\t\tNetwork Type: %s' % (ssid, auth, encryption, net_type))
        self.writeText(result)
    # This is a generic helpter for displaying lists of information
    def display_lists(self, attribute, info):
        result = ('%s:\n' % attribute)
        for i in range(len(info)):
            result += ('\t%s\n' % info[i])
        self.writeText(result)
    # Display's update numbers and where to go to download them
    def display_updates(self, info):
        result = ''
        update = info['Update']
        website = info['Website']
        if(len(info['Website']) == 0):
            result = "Your device is fully updated"
        else:
            for i in range(len(update)):
                result += ('\t%s can be found at %s\n\n' % (update[i], website[i]))
        self.writeText(result)
    # Displays open ports, whether they are TCP or UDP, and how mny processes are using them
    def display_open_ports(self, info):
        tcp_port = info['TCP Ports']
        udp_port = info['UDP Ports']
        result = 'TCP Port:\t\tNumber of processes used by:\t\t\tUDP Port:\t\t\tNumber of processes used by:\n\n'
        length = len(tcp_port) if len(tcp_port) > len(udp_port) else len(udp_port)
        # loop through larger value
        for i in range(length):
            #if i is less than tcp port and udp port print both
            if(i < len(tcp_port) and i < len(udp_port)):
                result += f'{tcp_port[i][0]}\t\t{tcp_port[i][1]}\t\t\t\t{udp_port[i][0]}\t\t{udp_port[i][1]}\n'
            elif(i < len(tcp_port) and i >= len(udp_port)):
                result += f'{tcp_port[i][0]}\t\t{tcp_port[i][1]}\n'
            else:
                result += f'\t\t\t\t\t{udp_port[i][0]}\t{udp_port[i][1]}\n'
        self.writeText(result)
    # Display's the amount memory the computer has total and memory
    def display_memory(self, info):
        return ('Total Memory:\t  %.2f GB\nAvailable Memory: %.2f GB' % (info['Total Memory'], info['Available Memory']))
    # Display's the computer's basic information
    def display_basic_info(self, info):
        sysinfo = info['System Info']
        name = info['Machine Name']
        version = info['Version']
        processor = info['Processor']
        return ('System Info: \t%s\nMachine Name: \t%s\nVersion: \t\t%s\nProcessor: \t%s\n' % (sysinfo, name, version, processor))
    # This shows the date and time the scan was last run
    def display_date(self, info):
        return ('Your computer was last scanned on %s/%s/%s at %s' % (info['Month'], info['Day'], info['Year'], info['Time']))
    # This opens the bit_locker
    def open_disk_encryption(self):
        scan.get_disk_encryption()
    #rescan's system and changes the screen to the loading_screen
    def rescan(self):
        self.controller.show_frame("loading_screen")
        scan.make_json()
    # writes text to the text field in the mid_center
    def writeText(self, info):
        self.text.config(state='normal')
        self.text.delete(1.0, 'end')
        self.text.insert('end', info)
        self.text.config(state='disabled')
    # sets the labels for the description of an attribute and it's importance
    def description(self, name):
        self.header.set(name)
        with open('information.json', 'r') as read:
            description = json.load(read)
            info = description[name]
        self.information.set(info['description'])
        self.importance.set(info['importance'])
    # This sets the labels for all the single data point attributes
    def single_data(self, attribute):
        with open('computer_info.json', 'r') as read:
            data = json.load(read)
            info = data[attribute]
        result = ('%s:\t%s' % (attribute, info))
        if(attribute == 'Screen Lock'):
            result += ' Minutes'
        return result
    # This routes to methods to write lists and nested data point attributes
    def nested_data(self, attribute):
        with open('computer_info.json', 'r') as read:
            data = json.load(read)
            info = data[attribute]
        if(attribute == 'Open Ports'):
            self.display_open_ports(info)
        elif(attribute == 'Updates'):
            self.display_updates(info)
        elif(attribute == 'Wi-Fi History' or attribute == 'Startup Programs' or attribute == 'Software'):
            self.display_lists(attribute, info)
        elif(attribute == 'Wi-Fi Info'):
            self.display_wifi_info(info)
        elif(attribute == 'Memory'):
            return self.display_memory(info)
        elif(attribute == 'Basic Info'):
            return self.display_basic_info(info)
        elif(attribute == 'Date'):
            return self.display_date(info)
# This is the class for the loading screen
class loading_screen(Frame):
    # This creates the widges for this page, a label and 'back' buttons
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        label = Label(self, text="The scan is now complete, please click 'Back' to see the re-scanned data.")
        label.pack(side="top", fill="x", pady=10)
        restart_button = Button(self, text="Back", command=self.go_back)
        restart_button.pack()
    # Functionality for the back button
    def go_back(self):
        self.controller.show_frame("info_screen")
# Class for the credits screen
class credits(Frame):
    # This creates the widges for this page, a label and 'back' buttons
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        label = Label(self, text="This page has yet to be implemented, please press the 'Back' putton to go back (duh)")
        label.pack(side="top", fill="x", pady=10)
        restart_button = Button(self, text="Back", command=self.go_back)
        restart_button.pack()
    # Functionality for the back button
    def go_back(self):
        self.controller.show_frame("start_page")
if __name__ == "__main__":
    app = ramscan()
    app.title('Ram Scan')
    # app.geometry("1300x700")
    app.mainloop()
