from fastapi import FastAPI, HTTPException
import json
from pydantic import BaseModel


class Item(BaseModel):
	id: int
	latitude: float
	longitude: float

json_filename="location.json"

with open(json_filename,"r") as read_file:
	data = json.load(read_file)

app = FastAPI()

@app.get('/loc')
async def read_all_loc():
	return data['location']


@app.get('/loc/{item_id}')
async def read_loc(item_id: int):
	for loc_id in data['location']:
		print(loc_id)
		if loc_id['id'] == item_id:
			return loc_id
	raise HTTPException(
		status_code=404, detail=f'location not found'
	)

@app.post('/loc')
async def add_loc(item: Item):
	item_dict = item.dict()
	item_found = False
	for loc_item in data['location']:
		if loc_item['id'] == item_dict['id']:
			item_found = True
			return "Location ID "+str(item_dict['id'])+" exists."
	
	if not item_found:
		data['location'].append(item_dict)
		with open(json_filename,"w") as write_file:
			json.dump(data, write_file)

		return item_dict
	raise HTTPException(
		status_code=404, detail=f'item not found'
	)

@app.put('/loc')
async def update_loc(item: Item):
	item_dict = item.dict()
	item_found = False
	for loc_idx, loc_item in enumerate(data['location']):
		if loc_item['id'] == item_dict['id']:
			item_found = True
			data['location'][loc_idx]=item_dict
			
			with open(json_filename,"w") as write_file:
				json.dump(data, write_file)
			return "updated"
	
	if not item_found:
		return "location ID not found."
	raise HTTPException(
		status_code=404, detail=f'item not found'
	)

@app.delete('/loc/{item_id}')
async def delete_loc(item_id: int):

	item_found = False
	for loc_idx, loc_item in enumerate(data['location']):
		if loc_item['id'] == item_id:
			item_found = True
			data['location'].pop(loc_idx)
			
			with open(json_filename,"w") as write_file:
				json.dump(data, write_file)
			return "updated"
	
	if not item_found:
		return "location ID not found."
	raise HTTPException(
		status_code=404, detail=f'item not found'
	)
