from pyxtal.db import database

db0 = database('benchmark.db')
#db = database("../../../Organic_CSP/test.db")
#row = db.get_row('XATJOT')
#cinfo = row.data['charmm_info']
#row1 = db0.get_row('XATJOT')
#data = row1.data
#data['charmm_info'] = cinfo
#db0.db.update(row1.id, data=data)

row1 = db0.get_row('XATJOT')
print(row1.data['charmm_info']['label'])
