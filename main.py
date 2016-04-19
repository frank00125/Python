#coding=UTF-8
from Tkinter import *
import ttk
import tkMessageBox
import tkFileDialog as fd
from Tkinter import StringVar
import MySQLdb
import ctypes
import webbrowser
from googlemaps import *
import googlemaps
from datetime import datetime
from HTMLParser import HTMLParser

class MyHTMLParser(HTMLParser):
    def handle_data(self, data):
        self.__dataStr.append(data)

    def AllData(self):
        strs = list()
        for item in self.__dataStr:
            strs.append(item)
        while len(self.__dataStr) > 0:
            self.__dataStr.pop()
        return strs

    __dataStr = list()


class MyApp:
    def __init__(self, master):
        self.__master = master
        master.wm_title("台北夜生活大搜索")
        width = self.__master.winfo_screenwidth() / 2 - 400
        height = self.__master.winfo_screenheight() / 2 - 300
        sizes = "800x600+%d+%d" % (width, height)
        self.__master.geometry(sizes)
        frame = Frame(master,{
            'bg': 'black',
        })
        self.__frame = frame
        self.__frame.pack_propagate(0)
        self.__frame.place(x=0,y=0,height=600, width=800)
        self.__button = {}
        self.init()
    
    def createButton(self, name):
        button = Button(self.__frame, {
            'text': name,
            'bg': 'brown',
            'fg': 'yellow',
            'command': lambda: self.getStore(name)
        })

        self.__button[name] = button

    def createQuitButton(self):
        button = Button(self.__frame, {
            'text': 'EXIT',
            'font': 'Helvetica 10 bold',
            'bg': 'red',
            'fg': 'white',
            'command': self.__frame.quit
        })

        self.__quitButton = button

    def createSubmitButton(self):
        button = Button(self.__frame, {
            'text': '查詢',
            'font': 'Helvetica 10 bold',
            'bg': 'black',
            'fg': 'white',
            'command': self.query
        })

        self.__submitButton = button

        

    def getStore(self, name):
        var = StringVar()

        sql = "SELECT * FROM information WHERE name = '%s';" % (name)

        db = MySQLdb.connect(host='localhost', user='frank', passwd='css911066', db='test')

        cursor = db.cursor()
        cursor.execute('set names utf8;')

        detailStr = ""
        url = ""

        try:
            cursor.execute(sql)
            result = cursor.fetchall()
            for r in result:
                detailStr = "店名: %s\n類型: %s\n地址: %s\n臨近捷運站: %s\n網址: %s\n聯絡電話: %s\n" % (r[1],r[2],r[3],r[4],r[5],r[6])
                url = r[5]
                var.set(detailStr)
        except Exception,e:
            print 'ERROR:' + str(e)
            db.rollback()

        db.close()

        if self.__detailFrame is None:
            self.__detailFrame = Toplevel(self.__master,{
                'bg': 'blue',
            })
            self.__detailFrame.title(name)
            self.__detailFrame.geometry('500x500+50+50')
            
            self.__detailLabel = Label(self.__detailFrame,{
                'textvariable': var,
                'font': 'Helvetica 16',
                'bg': 'pink',
                'fg': 'black'
            })
            self.__detailLabel.place(x=0,y=100,height=300, width=500)
            
            self.__detailExitButton = Button(self.__detailFrame,{
                'text': 'EXIT',
                'font': 'Helvetica 12',
                'bg': 'red',
                'fg': 'white',
                'command': self.closeWindow
            })
            self.__detailExitButton.place(x=425,y=425,height=50,width=50)
            
            self.__showOpenningTime = Button(self.__detailFrame, {
                'text': '相關訊息',
                'font': 'Helvetica 12',
                'bg': 'brown',
                'fg': 'white',
                'command': lambda: self.showInformation(name)
            })
            self.__showOpenningTime.place(x=350,y=425,height=50,width=75)
            
            self.__OpenWebsiteButton = Button(self.__detailFrame,{
                'text': '開啟官方網站',
                'font': 'Helvetica 12',
                'bg': 'purple',
                'fg': 'white',
                'command': lambda: self.openUrl(r[5])
            })

            self.__OpenWebsiteButton.place(x=250, y=425,height=50,width=100)
            self.__OpenHowToGo = Button(self.__detailFrame,{
                'text': '如何去？',
                'font': 'Helvetica 12',
                'bg': 'black',
                'fg': 'white',
                'command': lambda: self.howToGo(r[4], r[3])
            })
            self.__OpenHowToGo.place(x=175,y=425,height=50,width=75)
        else:
            self.__detailFrame.title(name)
            self.__detailLabel.config(textvariable=var)
            self.__showOpenningTime.config({
                'command': lambda: self.showInformation(name)
            })
            self.__OpenWebsiteButton.config({
                'command': lambda: self.openUrl(r[5])
            })
            self.__OpenHowToGo.config({
                'command': lambda: self.howToGo(r[4], r[3])
            })

        self.__detailFrame.lift(aboveThis=self.__master)
    
    def closeWindow(self):
        self.__detailLabel.destroy()
        self.__detailLabel = None
        self.__detailExitButton.destroy()
        self.__detailExitButton = None
        self.__OpenWebsiteButton.destroy()
        self.__OpenWebsiteButton = None
        self.__detailFrame.destroy()
        self.__detailFrame = None

    def openUrl(self, url):
        webbrowser.open_new(url)

    def howToGo(self, station, address):
        steps = self.howToGoFromStation(station, address)
        way = u'從%s出發\n' % (station.decode('UTF-8'))
        count = 0
        for step in steps:
            count += 1
            way += '%d: %s\n' % (count, step)
        tkMessageBox.showinfo('如何去？', way)

    def howToGoFromStation(self, station, address):
	steps = list()
    	ways = list()
    	gmaps = googlemaps.Client(key='AIzaSyC8UZAQ6R3Le4NdeNUAxCgOYVMoJA-Nb94')
    	now = datetime.now()
    	dirs = gmaps.directions(station, address, mode='walking',departure_time=now,language='zh-TW')
    	for route in dirs:
    	    for way in route['legs']:
    	        for step in way['steps']:
    	            steps.append(step['html_instructions'])

        for step in steps:
            parser = MyHTMLParser()
            parser.feed(step)
            road = u''
            roads = parser.AllData()
            for i in range(len(roads)):
                road += roads[i]
            ways.append(road)
            road = u''
    
        return ways
    
    def showInformation(self, name):
        db = MySQLdb.connect(host='localhost', user='frank', passwd='css911066', db='test')

        cursor = db.cursor()
        cursor.execute('set names utf8;')

        sql = "SELECT * FROM price p JOIN time t ON p.name=t.name WHERE p.name LIKE '%%%s%%';" % (name)
        print sql

        try:
            cursor.execute(sql)
            result = cursor.fetchall()
            prices = ""
            for r in result:
                isOpen = [False, False, False, False, False, False, False]
		count = 1
                prices += '營業時間:\n\n'
                for i in range(22, 36, 2):
                    if r[i] > 12:
                        start = "%dp.m." % (r[i] - 12)
                    else:
                        start = '%da.m.' % (r[i])
                    
                    if r[i+1] > 12:
                        end = '%dp.m.' % (r[i+1] - 12)
                    else:
                        end = '%da.m.' % (r[i+1])
                    
                    if r[i] == -1 and r[i+1]== -1:
                        if count == 7:
                            prices += "    星期日: 無營業\n"
                        else:
                            prices += "    星期%d : 無營業\n" % (count)
                    elif count != 7:
                        isOpen[count - 1] = True
                        prices += "    星期%d : %s ~ %s\n" % (count, start, end)
                    elif count == 7:
                        isOpen[6] = True
                        prices += "    星期日: %s ~ %s\n" % (start, end)
                    count += 1

                prices += '\n簡略低消價位表: \n\n'
		
		count = 1
                for i in range(2, 16, 2):
                    man = ""
                    woman = ""
                    if isOpen[count - 1]:
                        if r[i] == -1:
                            man = "無低消"
                        else:
                            man = str(r[i])

                        if r[i+1] == -1:
                            woman = "無低消"
                        else:
                            woman = str(r[i+1])

                        if count != 7:
                            prices += "    星期%d : (男)%s (女)%s\n" % (count, man, woman)
                        else:
                            prices += "    星期日: (男)%s (女)%s\n" % (man, woman)
                    count += 1

                avg = ''
                if r[16] == -1:
                    avg = '無低消'
                else:
                    avg = str(r[16])
                prices += "    平均價位: %s\n" % (avg)
                
                man_high = ''
                woman_high = ''
                if r[17] == -1:
                    man_high = '無低消'
                else:
                    man_high = str(r[17])
                if r[18] == -1:
                    woman_high = '無低消'
                else:
                    woman_high = str(r[18])
                prices += "    男生最高價位: %s, 女生最高價位: %s\n" % (man_high, woman_high)

                
                tkMessageBox.showinfo('%s的相關資訊' % (name), prices)
        except Exception,e:
            print "ERROR:" + str(e)
            db.rollback()

    def transferDatetoInt(self):
        tstr = self.__combox['time'].get()

        if tstr == u'星期日':
            return 7
        elif tstr == u'星期一':
            return 1
        elif tstr == u'星期二':
            return 2
        elif tstr == u'星期三':
            return 3
        elif tstr == u'星期四':
            return 4
        elif tstr == u'星期五':
            return 5
        elif tstr == u'星期六':
            return 6
        else:
            return 0
    
    def query(self):
        butt = self.__button.keys()
        if len(butt) != 0:
            for key in butt:
                if self.__button[key] is None:
                    print 'None in button[%s]' % (key)
                else:
                    self.__button[key].place_forget()
                    self.__button[key].destroy()
                    self.__button[key] = None

        db = MySQLdb.connect(host='localhost', user='frank', passwd='css911066',db='test')

        cursor = db.cursor()
        cursor.execute('set names utf8;')
        
        """
        try:
            cursor.execute('SELECT * FROM test.information;')
            result = cursor.fetchall()
            for record in result:
                for item in record:
                    print item
                print '\n'
            cursor.close()
        except:
            print 'error'
        db.close()
        """
        typ = self.__combox['type'].get()
        name = self.__nameText.get()
        highestPrice = self.__combox['highestPrice'].get()
        time = self.transferDatetoInt()
        station = self.__combox['station'].get()
        sql1 = "SELECT p.name FROM information i JOIN price p ON i.name=p.name JOIN time t ON p.name=t.name WHERE "

        situation = False

        print type(typ)

        if name != "":
            situation = True
            sql1 += "i.name LIKE '%%%s%%'" % (name)
        
        if typ != u"不限":
            situation = True
            if name != "":
                sql1 += " && "
            sql1 += "i.typ LIKE '%%%s%%'" % (typ)

        if highestPrice != u"None":
            situation = True
            if name != "" or typ != u"不限":
                sql1 += " && "

            for week in ['mon','tue','wed','thu','fri','sat','sun']:
                for sex in ['man','woman']:
                    tmpstr = 'p.%s_%s' % (week, sex)
                    sql1 += '%s <= %s || %s == -1' % (tmpstr, highestPrice)
                    if tmpstr != 'p.sun_woman':
                        sql1 += ' && '

        if time != 0:
            situation = True
            if name != "" or typ != u"不限" or highestPrice != u"None":
                sql1 += " && "

            if time == 1:
                sql1 += "t.mon_start != -1"
            elif time == 2:
                sql1 += "t.tue_start != -1"
            elif time == 3:
                sql1 += "t.wed_start != -1"
            elif time == 4:
                sql1 += "t.thu_start != -1"
            elif time == 5:
                sql1 += "t.fri_start != -1"
            elif time == 6:
                sql1 += "t.sat_start != -1"
            elif time == 7:
                sql1 += "t.sun_start != -1"

        if station != u'不限':
            situation = True
            if name != "" or typ != u"不限" or highestPrice != u"None" or time != 0:
                sql1 += " && "
            
            sql1 += "i.near_station LIKE '%%%s%%'" % (station)

        sql1 += ';'
        sql1 = sql1.encode("UTF-8")

        if situation:
            print sql1
            try:
                cursor.execute(sql1)
                result = cursor.fetchall()
                Y = 200
                X = 50
                for record in result:
                    for item in record:
                        print item
                        if X + 70 >= 800:
                            X = 50
                            Y += 50

                        self.createButton(item)
                        self.__button[item].place(x=X, y=Y, height=40, width=150)
                        
                        X += 170
                cursor.close()
            except Exception,e:
                print "ERROR:" + str(e)
                db.rollback()

        else:
            tkMessageBox.showinfo("注意!!!", "請至少輸入一個欄位") 

        db.close()
        
    def init(self):
        """
        self.createTextArea()
        self.createLabel('店名: ')
        self.createComboBox('closeTime', ['10pm','11pm','12pm','1am','2am','3am','None'])
        self.createLabel('閉店時間: ')
        self.createComboBox('openingTime', ['6pm','7pm','8pm','9pm','10pm','11pm','None'])
        self.createLabel('開店時間: ')
        self.createComboBox('highestPrice', ['None', '100','200','300','400','500','600','700','800'])
        self.createLabel('最高價格: ')
        self.createComboBox('lowestPrice', ['None','100','200','300','400','500','600','700','800'])
        self.createLabel('最低價格" ')
        self.createComboBox('type', ['沙發酒吧','調酒餐廳','娛樂夜店','同志夜店'])
	self.createLabel('類型: ')
	"""        
	self.createLabel('type', '類型')
        self.createComboBox('type', ['不限','沙發酒吧','調酒餐廳','娛樂夜店','同志夜店'])
        self.createLabel('highestPrice', '最高價格: ')
        self.createComboBox('highestPrice', ['None', '100','200','300','400','500','600','700','800'])
        self.createLabel('time', '時間')
        self.createComboBox('time', ['不限','星期日','星期一','星期二','星期三','星期四','星期五','星期六'])
        self.createLabel('name', '店名')
        self.createLabel('title', '台北夜生活大搜索')
        self.createComboBox('station', ['不限','忠孝敦化站','市政府站','中正紀念堂站','南京東路站','中山站','忠孝復興站','中山國小','國父紀念館','古亭站','台電大樓站','科技大樓站','永春站', '善導寺站','大安站','行天宮站'])
        self.createLabel('station','臨近捷運站')
        self.createTextArea()
        self.createSubmitButton()
        self.createQuitButton()
        
        self.__combox['type'].current(newindex=0)
        self.__combox['highestPrice'].current(newindex=0)
        self.__combox['time'].current(newindex=0)
        self.__combox['station'].current(newindex=0)
        self.__label['title'].config({
            'font': 'Helvetica 24 bold',
            'bg': 'white',
            'fg': 'red'
        })

        X = 105
        Y = 5
        self.__label['title'].place(x=250,y=10,height=80, width=300)
        self.__label['name'].place(x=300,y=100,height=25,width=50)
        self.__nameText.place(x=350, y=100, height=25,width=115)
        lst = ['type', 'highestPrice', 'time', 'station']
        self.__label[lst[0]].place(x=30, y=145, height=30, width=50)
        self.__combox[lst[0]].place(x=80, y=145, height=30, width=90)
	self.__label[lst[1]].place(x=190, y=145, height=30, width=70)
        self.__combox[lst[1]].place(x=260, y=145, height=30, width=90)
        self.__label[lst[2]].place(x=370, y=145, height=30, width=50)
        self.__combox[lst[2]].place(x=420, y=145, height=30, width=90)
        self.__label[lst[3]].place(x=530, y=145, height=30, width=75)
        self.__combox[lst[3]].place(x=605, y=145, height=30, width=100)

        self.__submitButton.place(x=530,y=100, height=25, width=55)
        self.__quitButton.place(x=585, y=100, height=25, width=55)

    def createListBox(self, listName):
        listbox = Listbox(self.master)

        listbox.insert(END, "a list entry")

        for item in listName:
            listbox.insert(END, item)
        
        self.listbox = listbox
        self.listbox.pack({ "side": "bottom" })

    def createComboBox(self, name, listName):
        v = StringVar()
        combox = ttk.Combobox(self.__frame, textvariable=v, state='readonly')
        combox['values'] = tuple(listName)
        combox.current(0)
        self.__combox[name] = combox

    def createTextArea(self):
        name = Entry(self.__frame)
        self.__nameText = name

    def createLabel(self, name, context):
        var = StringVar()
        label = Label(self.__frame, textvariable=var, relief=RAISED)
        label.config({
            'font': 'Helvetica 10 bold',
            'bg': 'white',
            'fg': 'black'
        })
        var.set(context)
        self.__label[name] = label
        

    __button = dict()
    __frame = None
    __master = None
    __detailFrame = None
    __nameText = None
    __combox = dict()
    __label = dict()

root = Tk()
app = MyApp(root)
root.mainloop()
