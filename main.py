

#python modules used
from time import strftime
import sqlite3 as sq
from collections import OrderedDict
import json
#modules to convert isotime to local time
from dateutil import tz
import dateutil.parser

## kivy modules ##
import kivy
#kiv.require()
from kivy.app import App
#from kivy.logger import Logger
#import logging
#Logger.setLevel(logging.TRACE)
from kivy.base import EventLoop
from kivy.animation  import Animation
#from kivy.network.urlrequest import UrlRequest
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.settings import SettingsWithTabbedPanel

##md methods used 
from kivymd.theming import ThemeManager
from kivymd.dialog import MDDialog

## juicyfy the app with 3rd party modules ##

#access environment variables easily
from decouple import config
#text to speech module
from plyer import tts
#Internet access
import requests
#access geo coordinates
import geocoder
#access weather data api
import pyowm


## custom modules ##
from Defaults_json import my_settings

LOCAL_TIME= tz.gettz() #local time setter

con=sq.connect("weather_data.db3") #database connection


""" uncomment line below and paste your api key """

#api_key='paste open weather api key'

"""or make .env file with for your api key"""
api_key = config('API')
owm = pyowm.OWM(api_key)







""" all application logic and functions """

class WeatherApp(App):
    settings_cls=SettingsWithTabbedPanel
    use_kivy_settings= False
    theme_cls = ThemeManager()
    theme_cls.primary_palette = 'Brown'
    theme_cls.accent_palette = 'Brown'
    theme_cls.theme_style = 'Dark'
    title="Weather 24/7"
    icon:"icon.png"
        

        
               
                      
    #function1 update time
    def updates(self,*args):
        self.root.ids._today.text = strftime('%A,%B %Y.\n%H:%M:%S')

        
        
        
#if data connection is available
    # using requests function 2
    def is_connected(self):
        try:
            # connect to the host -- tells us if the host is actually
            # reachable
            response=requests.get("https://google.com",timeout=2)
            self.notify_on()
            #s=socket.create_connection(("www.google.com", 1))
            #s.close()
            return True
        except requests.ConnectionError :
            pass
        return False
                
    def show_dialog(self,*args):
        info=MDDialog(title="app info")
                
     #display map if connected 
     #function 3
    def online_view(self,*args):
        self.saved_data()
        if self.is_connected():
            Clock.schedule_once(self.main_location_weather, 20)
        else:
            self.notify_off()
            self.offline_view()
            
            
            
      #popups 
    def notify_on(self,*args):
        self.message=Label(text="connected smoothly\nmap and weather updating...")
        self.pops=Popup(title="online",size_hint=(0.8,0.2),content=self.message)
        self.pops.open()
        
        
        
    def notify_off(self,*args):
        self.message1=Label(text="no connection\ncheck  internet connection.")
        self.pops1=Popup(title="offline",size_hint=(0.8,0.2),content=self.message1)
        self.pops1.open()
        
        
        
        
      #get curremt weather from opwm if connected and write txt file
      #function 4
    def main_location_weather(self,*args):
        if self.is_connected():
            self.my_main_location=self.config.get("setup","main location")
            g=geocoder.arcgis(str(self.my_main_location))#str(locale)
            coords=g.latlng
            lati=coords[0]
            long=coords[1]
            observation= owm.weather_at_coords(lati,long)# get obs_objct
            loco=observation.get_location()# get location details
            loco_id=loco.get_ID()
            loco_name=loco.get_name()
            lon=loco.get_lon()
            lat=loco.get_lat()
            recep=observation.get_reception_time(timeformat='iso')#when data was received
            
            weather_object=observation.get_weather()# extract weather data
           #weather items 
            ref_times=weather_object.get_reference_time(timeformat='iso')
            ref_time=dateutil.parser.parse(ref_times).astimezone(LOCAL_TIME).strftime('%d %b,%Y. %I:%M %p') 
            sunrises=weather_object.get_sunrise_time('iso')
            sunrise=dateutil.parser.parse(sunrises).astimezone(LOCAL_TIME).strftime('%d %b,%Y. %I:%M %p')
            sunsets=weather_object.get_sunset_time('iso')
            sunset=dateutil.parser.parse(sunsets).astimezone(LOCAL_TIME).strftime('%d %b,%Y. %I:%M %p')
            de_wea=weather_object.get_detailed_status()
            temp=weather_object.get_temperature(unit='celsius')
            mean_temp=temp["temp"]
            max_temp=temp["temp_max"]
            min_temp=temp["temp_min"]
            viz=weather_object.get_visibility_distance()
            wind=weather_object.get_wind()
            print(wind,"wind object")
            w_spd=wind["speed"]
            w_deg=wind["deg"]
            cld_cvr=weather_object.get_clouds()
            humd=weather_object.get_humidity()
            atm_p=weather_object.get_pressure() 
            prs=atm_p["press"]
            sealvl=atm_p["sea_level"]
            rain=weather_object.get_rain()
            #icon_name=weather.get_weather_icon_name()
            icon_url=weather_object.get_weather_icon_url()
            info="{}\n mean temperature {} °c\n{}".format(de_wea,mean_temp,loco_name)
            current_label=self.root.ids.current_weather_location_time
            current_label.text=info #mapmarker 
            self.root.ids.weather_icons.source=icon_url 
            self.talk_back(info) #text to speech 
            #save the data in txt file 
            record={'latitude':lat,'longtitude':long,'location':loco_name,'time':ref_time,'sunrise':sunrise,'sunset':sunset,'weather':de_wea,'mean_temp':mean_temp,'max_temp':max_temp,'min_temp':min_temp,'humidity':humd,'wind_speed':w_spd,'wind_degree':w_deg,'cloud_cover':cld_cvr,'atmospheric_pressure':prs,'visibility':viz,'rain_volume':rain,'icon_url':icon_url}
            with open("recent_weather.txt","w") as f:
                json.dump(record,f)
                f.close()
                self.saved_data()
            Clock.schedule_once(self.update_map, 20)
        else:
            self.notify_off()
             
                
        
        
        
        
        
        
        
        #searching screen
        #user searching location
    def search_location(self,*args):
        self.city_name=self.root.ids.city_name
        if self.is_connected() and len(self.city_name.text) > 0:
            g=geocoder.arcgis(str(self.city_name.text))
            coords=g.latlng
            lati=coords[0]
            long=coords[1]
            observation= owm.weather_at_coords(lati,long)# get obs_objct
            loco=observation.get_location()# get location object details
            loco_id=loco.get_ID()
            loco_name=loco.get_name()
            recep=observation.get_reception_time(timeformat='iso')#when data was received
            weather_object=observation.get_weather()
            ref_times=weather_object.get_reference_time(timeformat='iso')
            ref_time=dateutil.parser.parse(ref_times).astimezone(LOCAL_TIME).strftime('%d %b,%Y. %I:%M %p') 
            de_wea=weather_object.get_detailed_status()
            temp=weather_object.get_temperature(unit='celsius')
            mean_temp=temp["temp"]
            viz=weather_object.get_visibility_distance()
            #icon_name=weather.get_weather_icon_name()
            icon_url=weather_object.get_weather_icon_url()
            output="{} in {}, {}\n average temperature  {} °c.\nvisible distance {} metres".format(ref_time,loco_name,de_wea,mean_temp,viz)
            self.root.ids.results_label.text=output
            self.talk_back(output)
            self.city_name.text=""
        else:
            self.notify_off()
            self.root.ids.results_label.text='None'
            self.city_name.text=""

        
                
                        
    def raise_output(self,widget,*args):
        Animation.cancel_all(widget)
        anim=Animation(bring_up= 0.5,d= 10)
        self.search_location()
        anim.start(widget)
        
    def drop_output(self,widget,*args):
        Animation.cancel_all(widget)
        self.root.ids.results_label.text=''
        anim=Animation(bring_up= 0,d=5,t="in_out_elastic")
        anim.start(widget)
        self.city_name.unfocus=True
                                        
                                                
                                                        
                                                                
                                                                        
                                                                                
                                                                                        
                                                                                                
                                                                                                                
        
        
        #remove map from home_screen if user has no connection
    def offline_view(self,*args):
        self.mappin=self.root.ids.first_view
        map_out=self.root.ids.map_drawn
        self.mappin.remove_widget(map_out)
        self.saved_data()
        #Clock.unschedule(self.update_map)
                
        
        
        
        
        
        
        
        
        
        
        
        
        

    #open last saved weather object if  user is offline
    def saved_data(self,*args):
        with open("recent_weather.txt","r") as f:
            weather=json.load(f)
            #self.root.ids.current_weather_now.text
            self.latitude=weather['latitude']
            self.longtitude=weather['longtitude']
            self.root.ids.time_location.text=str(weather['location'])+" \n"+str(weather['time'])
            self.root.ids.sun_rise.text="sunrise time\n"+str(weather['sunrise'])
            self.root.ids.sun_set.text="sunset time\n"+str(weather['sunset'])
            self.root.ids.current_weather.text="weather status \n"+str(weather['weather'])
            #self.root.ids.rainfall.text=weather['mean_temp']
            self.root.ids.max_temp.text="max temperature\n"+str(weather[ 'max_temp'])+" °c"
            self.root.ids.min_temp.text="min tempersture\n"+str(weather['min_temp'])+" °c"
            self.root.ids.humidity.text="humidity\n"+str(weather['humidity'])+"  %"
            self.root.ids.wind_speed.text="wind speed\n"+str(weather['wind_speed'])+" metres/sec"
            self.root.ids.wind_degree.text="wind degree\n"+str(weather['wind_degree'])
            self.root.ids.clouds.text="cloud cover\n"+str(weather['cloud_cover'])+" %"
            self.root.ids.pressure.text="atmospheric pressure \n"+str(weather['atmospheric_pressure'])+" hPa"
            self.root.ids.viz.text="visible distance\n"+str(weather['visibility'])+"  metres"
            self.root.ids.rainfall.text="rainfall volume \n"+str(weather['rain_volume'])+" hours : mm"
            #self.root.ids.weather_icon.source=str(weather['icon_url'])
            
            
            
          #update map coordinates  
    def update_map(self,*args):
        self.root.ids.map_drawn.center_on(self.latitude,self.longtitude)
        #self.root.ids.markers.my_lat1 =self.latitude
        #self.root.ids.markers.my_lon1=self.longtitude
  
        
        
        
        
        
        
        
        
        
        
        #display weather data from database 
        #data is weather forecasts of all default locations
    def display_records(self,*args):
        weathers=self.get_weather_forecasts()
        table_header=[h for h in weathers.keys()]
        rows_len=len(weathers[table_header[0]])
        
        data=[]
        for headers in table_header:
            data.append({"text":str(headers),"size_hint_y":None,"height": 50})#"font_size":16
        for d in range(rows_len):
            for h in table_header:
                data.append({"text":str(weathers[h][d]),"size_hint_y":None,"height": 35})
               
        self.root.ids.table_layout.cols=len(table_header)
        self.root.ids.data_records.data=data        
        #data added to recycle gridlayout
        self.todays_date=strftime('%d %b,%Y. %I:%M %p')
        if self.final_date < self.todays_date:
            self.new_forecast()
        else:
            return
      #extract data from database  
    def get_weather_forecasts(self):
        con=sq.connect("weather_data.db3")
        cur=con.cursor()
        #headers for the table
    
        data=OrderedDict()
        data["location"]={}
        data["time of the day"]={}
        data["weather status"]={}
        data["temperature °c"]={}
        #data["humidity%"]={}
        #data["cloud cover %"]={}
        #data["wind speed"]={}
        #data["wind degree"]={}
        #data["atm_pres"]={}
        #data["rainfall mm/hr"]={}
        #data["from date"]={}
        #data["ending date"]={}
        loco=[]
        self.ref_time=[] 
        wea=[]
        av_temp=[]
        hmd=[]
        cld=[]
        wnd_spd=[]
        wnd_deg=[]
        atm_p=[]
        rain=[]
        starting_d=[]
        ending_d=[]
        sql1="SELECT * FROM data"
        cur.execute(sql1)
        items=cur.fetchall()
        for item in items:
            loco.append(item[1])#"location_name"]) NOsql format
            self.ref_time.append(item[2])
            wea.append(item[3])
            av_temp.append(item[4])
            hmd.append(item[5])
            cld.append(item[6])
            wnd_spd.append(item[7])
            wnd_deg.append(item[8])
            atm_p.append(item[9])
            rain.append(item[10])
            starting_d.append(item[11])
            ending_d.append(item[12])
            
        data_count = len(loco)
        idx=0
        #values from the database 
        while idx < data_count:
            data["location"][idx]=loco[idx]
            data["time of the day"][idx]=self.ref_time[idx]
            data["weather status"][idx]=wea[idx]
            data["temperature °c"][idx]=av_temp[idx]
            #removed cause phone screens are tiny
            #data["humidity%"][idx]=hmd[idx]
            #data["cloud cover %"][idx]=cld[idx]
            #data["wind speed"][idx]=wnd_spd[idx]
            #data["wind degree"][idx]=wnd_deg[idx]
            #data["atm_pres"][idx]=atm_p[idx]
            #data["rainfall mm/hr"][idx]=rain[idx]
            #data["from date"][idx]=starting_d[idx]
            #data["ending date"][idx]=ending_d[idx]
            
            idx+=1 #sql ids
        self.final_date=ending_d[-1]
        self.starting_date=starting_d[-1]
        self.locality=self.config.get("setup","main location")
        timeline="Current location {}\n daily weather forecast after every 3 hours\n from {} upto {}".format(self.locality,self.starting_date,self.final_date)
        self.root.ids.timelinelabel.text=timeline
        
        return data
        
        
    #trigger to get new weather forecast after 5 days
    def new_forecast(self,*args):
        if self.is_connected():
            con=sq.connect("weather_data.db3")
            cur=con.cursor()
            self.my_main_location=self.config.get("setup","main location")
            #locale=self.my_main_location
            g=geocoder.arcgis(self.my_main_location)
            coords=g.latlng
            lati=coords[0]
            long=coords[1]
            observation= owm.weather_at_coords(lati,long)# get obs_objct
            loco=observation.get_location()#get location object
            locations=loco.get_name() #location name
            fc=owm.three_hours_forecast(locations)# 5 days
            #fc.actualize()
            f = fc.get_forecast()
            location_obj=f.get_location()
            start=fc.when_starts('iso')
            starting_d=dateutil.parser.parse(start).astimezone(LOCAL_TIME).strftime('%d %b,%Y. %I:%M %p') 
            finish=fc.when_ends('iso')
            ending_d=dateutil.parser.parse(finish).astimezone(LOCAL_TIME).strftime('%d %b,%Y. %I:%M %p') 
            for weather_object in f:
                location=location_obj.get_name()
                ref_times=weather_object.get_reference_time(timeformat='iso')
                ref_time=dateutil.parser.parse(ref_times).astimezone(LOCAL_TIME).strftime('%d %b,%Y. %I:%M %p') 
                sunrises=weather_object.get_sunrise_time('iso')
                sunrise=dateutil.parser.parse(sunrises).astimezone(LOCAL_TIME).strftime('%d %b,%Y. %I:%M %p')
                sunsets=weather_object.get_sunset_time('iso')
                sunset=dateutil.parser.parse(sunsets).astimezone(LOCAL_TIME).strftime('%d %b,%Y. %I:%M %p')
                de_wea=weather_object.get_detailed_status()
                temp=weather_object.get_temperature(unit='celsius')
                mean_temp=temp["temp"]
                max_temp=temp["temp_max"]
                min_temp=temp["temp_min"]
                viz=weather_object.get_visibility_distance()
                wind=weather_object.get_wind()
                w_spd=wind["speed"]
                w_deg=wind["deg"]
                cld_cvr=weather_object.get_clouds()
                humd=weather_object.get_humidity()
                atm_p=weather_object.get_pressure() 
                prs=atm_p["press"]
                sealvl=atm_p["sea_level"]
                rain=str(weather_object.get_rain())
                sql_query= 'INSERT INTO data (location,time,weather,mean_temp,humidity,wind_speed,wind_degree,cloud_cover,atmospheric_pressure,rain_volume,starting_date,ending_date) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)'
                rows=[location,ref_time,de_wea,mean_temp,humd,w_spd,w_deg,cld_cvr,prs,rain,starting_d,ending_d]
                cur.execute(sql_query,(rows))
                con.commit()
                #con.close()
        else:
            self.notify_off()
        
        
        #text to speech implimentation
    def talk_back(self,words,*args):
        tts.speak(str(words))
        
        
    def about(self,*args):
       idea='App name: Weather 24/7 version 1.0\nDeveloped:on 2019,june\nBy:stephen m.k\nContact:stephenkinyanjui2018@gmail.com\nFramework: kivy and kivymd using python.'
       idea1='Agenda:weather info from openweather.com.\nsoil analysis,air pollution levels\nOzone & uv exposure rate\n various satellite imagery and data.\nAll features will be available in version 2.0 of the app'
       contents=Label(text=idea,halign="center",size_hint=(0.4,0.2),font_size=18)
       contents1=Label(text=idea1,halign="center",size_hint=(0.4,0.2),font_size=18)
       layout=GridLayout(cols=1,padding=(10,10),spacing=10)
       layout.add_widget(contents)
       layout.add_widget(contents1)
       self.popp=Popup(title="About",content=layout,size_hint=(0.7,0.5))
       self.popp.open()
       
       
    #def log_out popup when exiting app
        
        
        
        
        
       
    def on_start(self,*args):
        EventLoop.ensure_window()
        Clock.schedule_interval(self.updates,1.0/60)
        if self.is_connected:
            self.online_view()
        else:
            self.offline_view()
        self.display_records()
       
       
        
#main default configurations         
    def build_config(self,config):
        config.setdefaults("setup",{"main location":"Nairobi","talk back":True})
        #function 1 default settings 
    def build_settings(self,settings):
        settings.add_json_panel("Settings Panel",self.config,data=my_settings)
        
    def on_config_change(self,config,section,key,value):
        #getting value from config
        if key == "main location":
            self.main_location_weather()
            Clock.schedule_once(self.new_forecast,40)
        
if __name__ == '__main__':
    WeatherApp().run()