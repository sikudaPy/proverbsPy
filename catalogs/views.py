import json
from django.http import HttpResponse, FileResponse
from django.template import loader
from .models import Catalog
from django.core.paginator import Paginator
from django.shortcuts import redirect
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CatalogSerializer
from openpyxl import Workbook
import os
from django.conf import settings
from django.contrib.auth.decorators import permission_required

def main(request):
  template = loader.get_template('main.html')
  return HttpResponse(template.render()) 

def catalogs(request):

  strFilter = str(request.GET.get("filter") or "")
  mycatalog = getCatalogByFilter(strFilter)

  per_page = request.GET.get("per_page") or 9
  paginator = Paginator(mycatalog, per_page)  
  page_number = request.GET.get("page") or 1
  page_mycatalogs = paginator.get_page(page_number)
  
  template = loader.get_template('all_catalog.html')
  context = {
    'page_mycatalogs': page_mycatalogs,
    'filter': strFilter,
    'user': request.user
  }
  return HttpResponse(template.render(context, request))

def details(request, id):
  myitem = Catalog.objects.get(id=id)
  template = loader.get_template('item_catalog.html')
  context = {
    'myitem': myitem,
  }
  return HttpResponse(template.render(context, request))

def UploadJson(request):
    if request.method == "POST":
        handle_uploaded_file(request.FILES['file_upload'])
        return redirect("/catalogs/")
    else:
        if request.user.is_superuser:
            template = loader.get_template('admin_catalog.html')
            context = {}
            return HttpResponse(template.render(context, request))
        else: 
            return redirect("/catalogs/")

#Загрузка json file [{'name':'', 'title':''}]
def handle_uploaded_file(f):
    file = open(f"{settings.MEDIA_ROOT}/{f.name}", "wb+")
    with file as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    file.close()

    file = open(f"{settings.MEDIA_ROOT}/{f.name}", encoding='utf-8')
    catalogs = json.load(file)
    Catalog.objects.all().delete()
    for elem in catalogs:
        new_object = Catalog(name = elem['name'], title = elem['title'])
        new_object.save()
    file.close()    
    os.remove(f"{settings.MEDIA_ROOT}/{f.name}")        

def SaveExcell(request):
    wb = Workbook()
    sheet = wb.active
    sheet.title = "Пословицы"
    strFilter = str(request.GET.get("filter") or "")
    mycatalog = getCatalogByFilter(strFilter)
    i = 1
    for elem in mycatalog.all():
        sheet['A'+str(i)] = elem.name
        sheet['B'+str(i)] = elem.title
        i = i + 1
    
    strFile = f"{settings.MEDIA_ROOT}/Catalogs.xlsx"
    wb.save(strFile)
    return FileResponse(open(strFile, "rb"))

class CatalogAPI(APIView):
    def get(self, request, format=None):
        #Catalog.objects.all()
        strFilter = str(request.GET.get("filter") or "")
        if request.GET.get("page") is None:  
            page_mycatalogs = getCatalogByFilter(strFilter)
        else:
            mycatalog = getCatalogByFilter(strFilter)
            per_page = request.GET.get("per_page") or 9
            paginator = Paginator(mycatalog, per_page)  
            page_number = request.GET.get("page") or 1
            page_mycatalogs = paginator.get_page(page_number)

        serializer = CatalogSerializer(page_mycatalogs, many=True)
        return Response(serializer.data)

    @permission_required('catalogs.can_edit')
    def post(self, request, format=None):
        serializer = CatalogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    permission_required('catalogs.can_edit')
    def put(self, request, pk, *args, **kwargs):

        try:
            proverb = Catalog.objects.get(pk=pk)
        except Catalog.DoesNotExist:
            return Response({'error': 'Article not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CatalogSerializer(proverb, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    permission_required('catalogs.can_edit')
    def delete(self, request, pk, *args, **kwargs):
        try:
            proverb = Catalog.objects.get(pk=pk)
        except Catalog.DoesNotExist:
            return Response({'error': 'Article not found'}, status=status.HTTP_404_NOT_FOUND)

        proverb.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

#Special functions -----------------------------------------------------------------------------------------    
def getCatalogByFilter(strFilter: str = ""):
    return Catalog.objects.filter(Q(name__icontains=strFilter) | Q(title__icontains=strFilter)).order_by('name') 



    
