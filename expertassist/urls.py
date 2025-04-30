from django.contrib import admin
from django.urls import path
from expertassist.expert import views

from django.urls import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('tasks/', views.tasks, name='tasks'),
    path('logout/', views.signout, name='logout'),
    path('signin/', views.signin, name='signin'),
    path('create_task/', views.create_task, name='create_task'),
    path('tasks/<int:task_id>', views.task_detail, name='task_detail'),
    path('tasks/<int:task_id>/delete', views.delete_task, name='delete_task'),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
    path('edit_file_dash_view/', views.edit_file_dash_view, name='edit_file_dash_view'),
    path('edit_file_selection/', views.edit_file_selection, name='edit_file_selection'),
    path('analisis_atributos_dash_view/', views.analisis_atributos_dash_view, name='analisis_atributos_dash_view'),
    path('analisis_atributos_selection/', views.analisis_atributos_selection, name='analisis_atributos_selection'),
    path('concat_dataset/', views.concat_dataset, name='concat_dataset'),
    path('concat_dataset_selection/', views.concat_dataset_selection, name='concat_dataset_selection'),
    path('edit_file_dash_view/', views.edit_file_dash_view, name='edit_file_dash_view'),
    path('analisis_atributos_and_edit_files_dash_view/', views.analisis_atributos_and_edit_files_dash_view, name='analisis_atributos_and_edit_files_dash_view'),
    path('pygwalker_selection/', views.pygwalker_selection, name='pygwalker_selection'),
    path('pygwalker/', views.pygwalker_view, name='pygwalker'),
    path('aspirantes_x_historico_selection/', views.aspirantes_x_historico_selection, name='aspirantes_x_historico_selection'),
]
