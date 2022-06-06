def get_products_from_api_response(data):
    

    stores = []

    for item in data:

        store = {
            'id': item ['id'],
            'title': item['title'],
            'image': item['image'],
        }
        stores.append(store)
    return stores