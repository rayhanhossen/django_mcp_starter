import json

f = open('C:/Users/saikat.mitra/OneDrive - BRAC IT Services Limited/Desktop/bangladesh_districts.geojson')
data = json.load(f)
f.close()

new_dict = {
    "type": "FeatureCollection",
    "features": []
}

for index in range(0, len(data['features'])):
    new_dict['features'].append(
        {
            "type": "Feature",
            "geometry": {
                "type": data['features'][index]['geometry']['type'],
                "coordinates": data['features'][index]['geometry']['coordinates']
            },
            "properties": {
                "name": data['features'][index]['properties']['district'],
                "id": data['features'][index]['properties']['district'],
                "CNTRY": "Bangladesh",
                "TYPE": "District"
            },
            "id": data['features'][index]['properties']['district']
        }
    )

with open("bangladesh_districts_amcharts.json", "w") as outfile:
    json.dump(new_dict, outfile)

