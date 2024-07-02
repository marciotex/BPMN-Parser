# views.py

from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
import os
from . import forms
from .utils.bpmn_utils import parse_xml
from .utils.data_utils import process_bpmn_data
#from .utils.graph_utils import adefinir
#from .utils.simpy_utils import adefinir

# Caminho onde o arquivo BPMN será salvo
xmlpath = "static/upload/bpmn.xml"

def remove_xml_file():
    if os.path.isfile(xmlpath):
        os.remove(xmlpath)

def result(request):
    try:
        myroot = parse_xml(xmlpath)
    except FileNotFoundError:
        return upload(request, error="File not found")

    lanes_data, task_data, event_data, processes_data, total_time, cycle_time, gateways_name, sum_events, sum_tasks, sum_lanes, sum_processes, flows = process_bpmn_data(myroot)

    remove_xml_file()

    return render(request, "index.html", {
        'lanes': lanes_data,
        'tasks': task_data,
        'events': event_data,
        'processes': processes_data,
        'gateways': gateways_name,
        'flows': flows,
        'total_time': total_time,
        'sum_events': sum_events,
        'sum_tasks': sum_tasks,
        'sum_lanes': sum_lanes,
        'sum_processes': sum_processes,
        'cycle_time': cycle_time
    })

def upload(request, error=None):
    template_name = "upload.html"
    if request.method == "POST":
        form = forms.UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            fs = FileSystemStorage()
            remove_xml_file()  # Remove o arquivo anterior se existir
            filename = fs.save(xmlpath, request.FILES['file'])  # Salva o arquivo no diretório estático definido
            return redirect('result')
    else:
        form = forms.UploadFileForm()
    
    return render(request, template_name, {'form': form, 'error': error})
