import re

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from .models import Task
from .forms import TaskForm, CustomUserCreationForm
import pygwalker as pyg

from expertassist.expert.dash_apps.finished_apps.edit_files import *
from expertassist.expert.dash_apps.finished_apps.analisis_atributos import *
from expertassist.expert.dash_apps.finished_apps.analisis_atributos_and_edit_files_conciliacion import *
from expertassist.expert.dash_apps.finished_apps.dashboard_user import *
from expertassist.expert.aj_setup.historico_modelos_x_aspirantes import *

def check_admin(user):
   return user.is_superuser

def get_tasks_user(user):
    return Task.objects.filter(user_id=user.id)

@login_required
def home(request):
    return render(request, 'home.html')

@user_passes_test(check_admin)
def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {"form": CustomUserCreationForm()})
    else:
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                match = re.search(r'^[\w.-]+@[\w\.-]+\.\w+$', str(request.POST["email"]))

                if match:
                    user = form.save()
                    login(request, user)
                    app = create_dash_app_dashboard(user,user.id)
                    return redirect('home')
                else:
                    return render(request, 'signup.html', {"form": CustomUserCreationForm, "error": "Usuario invalido, recuerda utilizar la forma 'ejemplo@twl.com'."})

            except IntegrityError:
                return render(request, 'signup.html', {"form": form, "error": "Username already exists."})
        else:
            return render(request, 'signup.html', {"form": form})

@login_required
def signout(request):
    logout(request)
    return redirect('home')

def signin(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'GET':
        return render(request, 'signin.html', {"form": AuthenticationForm()})
    else:
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()

            login(request, user)
            app = create_dash_app_dashboard(user,user.id)
            return redirect('home')
        else:
            return render(request, 'signin.html', {"form": form, "error": "Invalid username or password."})

@login_required
def tasks(request):
    tasks = Task.objects.filter(user=request.user)
    return render(request, 'tasks.html', {"tasks": tasks})
    
@login_required
def create_task(request):
    if request.method == "GET":
        return render(request, 'create_task.html', {"form": TaskForm})
    else:
        try:

            form = TaskForm(request.POST, request.FILES)
            if form.is_valid():
                new_task = form.save(commit=False)
                new_task.user = request.user
                new_task.save()
                return redirect('tasks')

        except ValueError:
            return render(request, 'create_task.html', {"form": TaskForm, "error": "Error creating task."})

@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)

    if request.method == 'GET':
        form = TaskForm(instance=task)
    else:
        form = TaskForm(request.POST, request.FILES, instance=task)
        if form.is_valid():
            form.save()
            return redirect('tasks')
    return render(request, 'task_detail.html', {'task': task, 'form': form})

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')

@login_required
def analisis_atributos_dash_view(request):
    return render(request, 'analisis_atributos.html')

@login_required
def edit_file_dash_view(request):
    return render(request, 'edit_file.html')

@login_required
def analisis_atributos_and_edit_files_dash_view(request):
    return render(request, 'analisis_atributos_and_edit_files.html')

@login_required
def pygwalker_selection(request):

    global archivo_id_

    usuario = request.user
    tareas = get_tasks_user(usuario)

    file_names = []

    for tarea in tareas:
        if tarea.data_file:
            ruta_archivo = tarea.data_file.path
            file_names.append(str(ruta_archivo))

    file_names_short = [nombre_archivo.split('\\')[-1] for nombre_archivo in file_names]
    file_names_combined = list(zip(file_names_short, file_names))

    if request.method == 'POST':

        archivo_id = request.POST.get('archivo')
        archivo_optional_id = request.FILES.get('archivo_2')

        if archivo_id:

            archivo_id_ = archivo_id 
            return redirect('pygwalker')

        if archivo_optional_id:

            pygwalker_storage_location = os.path.join('media', 'uploads', 'pygwalker')
            pygwalker_savefile = FileSystemStorage(location=pygwalker_storage_location)
            pygwalker_name = pygwalker_savefile.save(archivo_optional_id.name, archivo_optional_id)
            pygwalker_directory = pygwalker_savefile.path(pygwalker_name)

            archivo_id_ = pygwalker_directory
            return redirect('pygwalker')

    return render(request, 'pygwalker_selection.html', {'tareas': file_names_combined})

@login_required
def pygwalker_view(request):

    data = pd.read_excel(archivo_id_)
    
    pyg_html = pyg.to_html(data)
    
    return render(request, 'pygwalker.html', {'pyg_html': pyg_html})

@login_required
def concat_dataset_selection(request):
    global archivo_id

    usuario = request.user
    tareas = get_tasks_user(usuario)

    file_names = []

    for tarea in tareas:
        if tarea.data_file:
            ruta_archivo = tarea.data_file.path
            file_names.append(str(ruta_archivo))

    file_names_short = [nombre_archivo.split('\\')[-1] for nombre_archivo in file_names]
    file_names_combined = list(zip(file_names_short, file_names))

    if request.method == 'POST':
        archivo_id = request.POST.get('archivo')
        return redirect('concat_dataset')

    return render(request, 'concat_dataset_selection.html', {'tareas': file_names_combined})

@login_required
def concat_dataset(request):
    context = {}

    if request.method == 'POST':

        uploaded_file = request.FILES['document']

        if uploaded_file.name.endswith('.csv'):

            savefile = FileSystemStorage(location=os.path.join('media', 'concat'))
            name = savefile.save(uploaded_file.name, uploaded_file)
            file_directory = savefile.path(name)

            if archivo_id.endswith('.csv'):
                original_data = pd.read_csv(archivo_id)

            elif archivo_id.endswith('.xlsx'):
                original_data = pd.read_excel(archivo_id)

            to_concat_data = pd.read_csv(file_directory)

            try :
                newdata = pd.concat([original_data, to_concat_data], axis=0)
                newdata.to_excel(archivo_id, index=False)
            except:
                messages.warning(request, 'Error concatenando datos')

        elif uploaded_file.name.endswith('.xlsx'):
            savefile = FileSystemStorage(location=os.path.join('media', 'concat'))
            name = savefile.save(uploaded_file.name, uploaded_file)
            file_directory = savefile.path(name)

            if archivo_id.endswith('.csv'):
                original_data = pd.read_csv(archivo_id)

            elif archivo_id.endswith('.xlsx'):
                original_data = pd.read_excel(archivo_id)

            to_concat_data = pd.read_excel(file_directory)

            try :
                newdata = pd.concat([original_data, to_concat_data], axis=0)
                newdata.to_excel(archivo_id, index=False)
                messages.warning(request, '¡Datos concatenados con exito!')
            except:
                messages.warning(request, '¡Error concatenando datos!')

        else:
            messages.warning(request, '¡El archivo no se ha cargado. Utilice una extensión de archivo .csv o .xlsx!')

    return  render(request, 'concat_dataset.html', context)

@login_required
def edit_file_selection(request):
    usuario = request.user
    tareas = get_tasks_user(usuario)

    file_names = []

    for tarea in tareas:
        if tarea.data_file:
            ruta_archivo = tarea.data_file.path
            file_names.append(str(ruta_archivo))

    file_names_short = [nombre_archivo.split('\\')[-1] for nombre_archivo in file_names]
    file_names_combined = list(zip(file_names_short, file_names))

    if request.method == 'POST':
        archivo_id = request.POST.get('archivo')
        archivo_optional_id = request.FILES.get('archivo_2')

        if archivo_id:
            create_dash_app_edit_file(archivo_id)
        if archivo_optional_id:

            edit_file_storage_location = os.path.join('media', 'uploads', 'edit_files')
            edit_file_savefile = FileSystemStorage(location=edit_file_storage_location)
            edit_file_name = edit_file_savefile.save(archivo_optional_id.name, archivo_optional_id)
            edit_file_directory = edit_file_savefile.path(edit_file_name)

            create_dash_app_edit_file(edit_file_directory)

        return redirect('edit_file_dash_view')

    return render(request, 'edit_file_selection.html', {'tareas': file_names_combined})

@login_required
def analisis_atributos_selection(request):
    usuario = request.user
    tareas = get_tasks_user(usuario)

    file_names = []

    for tarea in tareas:
        if tarea.data_file:
            ruta_archivo = tarea.data_file.path
            file_names.append(str(ruta_archivo))

    file_names_short = [nombre_archivo.split('\\')[-1] for nombre_archivo in file_names]
    file_names_combined = list(zip(file_names_short, file_names))

    if request.method == 'POST':
        archivo_id = request.POST.get('archivo')
        archivo_optional_id = request.FILES.get('archivo_2')

        if archivo_id:

            create_dash_app_analisis_atributos(archivo_id)

        if archivo_optional_id:

            analisis_atributos_storage_location = os.path.join('media', 'uploads', 'analisis_atributos')
            analisis_atributos_savefile = FileSystemStorage(location=analisis_atributos_storage_location)
            analisis_atributos_name = analisis_atributos_savefile.save(archivo_optional_id.name, archivo_optional_id)
            analisis_atributos_directory = analisis_atributos_savefile.path(analisis_atributos_name)

            create_dash_app_analisis_atributos(analisis_atributos_directory)

        return redirect('analisis_atributos_dash_view')

    return render(request, 'analisis_atributos_selection.html', {'tareas': file_names_combined})

@login_required
def aspirantes_x_historico_selection(request):

    global archivo_id

    usuario = request.user
    tareas = get_tasks_user(usuario)

    file_names = []

    for tarea in tareas:
        if tarea.data_file:
            ruta_archivo = tarea.data_file.path
            file_names.append(str(ruta_archivo))

    file_names_short = [nombre_archivo.split('\\')[-1] for nombre_archivo in file_names]
    file_names_combined = list(zip(file_names_short, file_names))

    if request.method == 'POST':
        
        archivo_id = request.POST.get('archivo')

        master_data = process_aspirante_x_historico(archivo_id)

        create_dash_app_combined_conciliacion(master_data)
        return redirect('analisis_atributos_and_edit_files_dash_view')

    return render(request, 'aspirantes_x_historico_selection.html', {'tareas': file_names_combined})
