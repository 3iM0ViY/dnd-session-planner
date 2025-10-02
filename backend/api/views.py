from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(["GET"])
def getData(request):
	DM = {"name": "Yulian", "age": 20}
	return Response(DM)