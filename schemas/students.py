

def address(item_address)->dict:
    return {
        "city": item_address["city"],
        "country": item_address["country"]
    }


def student(item)->dict:

    return {
        "id": str(item["_id"]),
        "name": item["name"],
        "age": item["age"],
        "address": address(item["address"])
    }

def students(items)-> list:
    return [student(item) for item in items]