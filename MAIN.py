import sys
#sys.path.append("/home/ftt/.local/lib/python3.7/site-packages/")
sys.path.append("/usr/local/lib/python3.6/dist-packages/")
sys.path.append("/usr/lib/python3/dist-packages/")
sys.path.append("/usr/lib/python3.6/")


from flask import Flask
from flask_restful import Resource, Api

import datetime
import Req_classes.Functions		as Func
import Req_classes.Handler_1_POST	as H1_PST
import Req_classes.Handler_2_PATCH	as H2_PTC
import Req_classes.Handler_3_GET	as H3_GET
import Req_classes.Handler_4_GET	as H4_GET
import Req_classes.Handler_5_GET	as H5_GET


#import os
#import flask
#print(os.path.abspath(flask.__file__))
Welcome_text="""
╔╗╔╗╔╗╔═══╗╔╗──╔══╗╔══╗╔╗──╔╗╔═══╗
║║║║║║║╔══╝║║──║╔═╝║╔╗║║║──║║║╔══╝
║║║║║║║╚══╗║║──║║──║║║║║╚╗╔╝║║╚══╗
║║║║║║║╔══╝║║──║║──║║║║║╔╗╔╗║║╔══╝
║╚╝╚╝║║╚══╗║╚═╗║╚═╗║╚╝║║║╚╝║║║╚══╗
╚═╝╚═╝╚═══╝╚══╝╚══╝╚══╝╚╝──╚╝╚═══╝
"""
print(Welcome_text)

app = Flask(__name__)
api = Api(app)

app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = False

api.add_resource(H1_PST.PostNewTable,		'/imports')
api.add_resource(H2_PTC.PatchCitizenData,	'/imports/<import_id>/citizens/<citizen_id>')
api.add_resource(H3_GET.GetCitizens,		'/imports/<import_id>/citizens')
api.add_resource(H4_GET.GetBirthdays,		'/imports/<import_id>/citizens/birthdays')
api.add_resource(H5_GET.GetAgeStats,		'/imports/<import_id>/towns/stat/percentile/age')

#if __name__ == '__main__':
Func.CreateInfoTable()
app.run(threaded=True,host='0.0.0.0',port='8080')
	
