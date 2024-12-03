from fastapi import APIRouter, Query
from schemas.students import student, students
from fastapi.requests import Request
from models.Student import Student
from fastapi.responses import JSONResponse
from fastapi import status
from bson import ObjectId

students_router = APIRouter()


@students_router.get("/")
def get_students(request: Request, country: str = Query(None), age: int = Query(None)):
    try:
        query = {}
        if country:
            query["address.country"] = country
        if age is not None:
            query["age"] = {"$gte": age}

        print(query)

        # Fetch matching students from the database
        cursor = request.app.mongodb_collection.find(query)
        students_list = [
            {"name": doc["name"], "age": doc["age"]}
            for doc in cursor
        ]

        # Return the filtered data
        return JSONResponse({"data": students_list}, status_code=status.HTTP_200_OK)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


@students_router.post("/")
def create_student(request: Request, student_data: Student):

    student_dict = student_data.dict()

    try:
        result = request.app.mongodb_collection.insert_one(student_dict)
        print(result)

        return_data = {
            "id": str(result.inserted_id)
        }

        return JSONResponse(return_data, status_code=status.HTTP_201_CREATED)

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

@students_router.get("/{id}")
def get_student_byid(request: Request, id: str):
    try:
        print(request.app.mongodb_collection, "request")
        object_id = ObjectId(id)
        cursor = request.app.mongodb_collection.find_one({"_id": object_id})
        data = student(dict(cursor))
        print(data)
        return JSONResponse(data, status_code=status.HTTP_200_OK)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


@students_router.delete("/{id}")
def delete_student_byid(request: Request, id: str):
    try:
        object_id = ObjectId(id)
        result = request.app.mongodb_collection.delete_one({"_id": object_id})

        if result.deleted_count == 0:
            return JSONResponse({"error": "Student Not found"},status_code= status.HTTP_404_NOT_FOUND)
        return JSONResponse({}, status_code=status.HTTP_200_OK)
    except Exception as e:
        return JSONResponse({"error": str(e)},status_code= status.HTTP_500_INTERNAL_SERVER_ERROR)

@students_router.patch("/{id}")
def edit_student_byid(request: Request, id: str, student_data: dict):
    try:
        object_id = ObjectId(id)
        update_data = {}

        # Validate fields
        if "name" in student_data and student_data["name"]:
            update_data["name"] = student_data["name"]
        if "age" in student_data and student_data["age"]:
            update_data["age"] = student_data["age"]
        if "address" in student_data:
            address_update = {}
            if "city" in student_data["address"]:
                address_update["city"] = student_data["address"]["city"]
            if "country" in student_data["address"]:
                address_update["country"] = student_data["address"]["country"]
            update_data["address"] = address_update

        if not update_data:
            return JSONResponse({"error": "No fields provided to update"}, status_code=status.HTTP_400_BAD_REQUEST)

        updated_record = request.app.mongodb_collection.update_one({"_id": object_id}, {"$set": update_data})

        if updated_record.matched_count == 0:
            return JSONResponse({"error": "Student not found"}, status_code=status.HTTP_404_NOT_FOUND)

        return JSONResponse({}, status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

