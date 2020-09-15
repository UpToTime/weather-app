#weather app main settings
import json

my_settings=json.dumps([{"type":"title","title":"App settings"},{"type":"string","title":"Home","desc":"Enter default location to receive weather information about daily ","section":"setup","key":"main location"},{"type":"bool","disabled":True,"title":"Talk back","desc":"allow app to talk back,text to speech","section":"setup","key":"talk back"}])





#{"type":"numeric","disabled":False,"title":"latitude","desc":"location latitude value, updated automatically !!dont edit!!","section":"setup","key":"lat"},{"type":"numeric","disabled":False,"title":"longtitude","desc":"location longtitude value, updated automatically !!dont edit!!","section":"setup","key":"lon"},
