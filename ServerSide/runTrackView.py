#************************************************#
# App: RunTrackView                              #
# Version: 1.0.1                                 #
# Autor: Gilberto Valenzuela                     #
# Description: Visualizador de los datos de      #
# localización de los equipos                    #
#************************************************#

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg
import json
import sys
import matplotlib
matplotlib.use('TkAgg')


def load_data():
    try:
        with open("ClientPosition.json", "r") as pos:
            currentData = json.load(pos)
    except FileNotFoundError:
        print("No Client Positions File found")
        sys.exit(1)
    for client in currentData:
        if currentData[client]["Taller"] in plant["Talleres_CiscoPrime"]:
            plant["Talleres_CiscoPrime"][currentData[client]["Taller"]
                                         ]["x"].append(currentData[client]["Coordenadas"][0])
            plant["Talleres_CiscoPrime"][currentData[client]["Taller"]
                                         ]["y"].append(currentData[client]["Coordenadas"][1])
        else:
            print(currentData[client]["Taller"] +
                  " not found in plantConfig.json")
    return currentData


def search(searchInfo, searchMode):
    plt.clf()  # limpia el gráfico para evitar el solape de información
    currentData = load_data()
    if searchMode == "ClientSearch":
        clientToFind = searchInfo
        if clientToFind in currentData:
            targetHall = currentData[clientToFind]["Taller"]
            print(targetHall)
            plt.scatter(currentData[clientToFind]["Coordenadas"][0],
                        currentData[clientToFind]["Coordenadas"][1], marker='o')  # Show only the desired client
        else:
            print("Client {} not found".format(searchInfo))
            return "", "Failed"
    elif searchMode == "HallSearch":
        targetHall = searchInfo
        plt.scatter(plant["Talleres_CiscoPrime"][targetHall]["x"], plant["Talleres_CiscoPrime"]
                    [targetHall]["y"], marker='o')  # Show all clients in a hall
    else:
        print("No Search mode detected")

# plantConfig.json debe tener la ruta al layout de todos los talleres. Formato de imagen (jpg, png)
    layout = plant["Talleres_CiscoPrime"][targetHall]["RutaLayout"]
    img = mpimg.imread(layout)
    mpimg.AxesImage('x')
# imshow() carga la imagen especificada al fondo del gráfico. La propiedad extent es necesaria definirla para que la imagen solo llene el área que deseamos. Si se omite, se carga la imagen en tamaño real haciendo los ejes tan extensos como sea necesario para abarcar la imagen.
# plt.imshow(img, extent=(-0.5, 420, 221, -0.5))  # T11
    plt.imshow(img, extent=(plant["Talleres_CiscoPrime"][targetHall]["AjusteEjes"][0], plant["Talleres_CiscoPrime"][targetHall]["AjusteEjes"]
                            [1], plant["Talleres_CiscoPrime"][targetHall]["AjusteEjes"][2], plant["Talleres_CiscoPrime"][targetHall]["AjusteEjes"][3]))
# plt.show() #Se usa cuando mostramos el gráfico directamente en matplotlib.
    # regresamos el taller objetivo que debe mostrar en el titulo del gráfico
    return targetHall, "Success"

# ------------------------------- Beginning of Matplotlib helper code -----------------------


def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    print("Draw function end")
    return figure_canvas_agg

# ------------------------------- Carga de configuraciones y datos externos. Creación del gráfico inicial -----------------------


try:
    with open("plantConfig.json", "r") as conf:
        plant = json.load(conf)
except FileNotFoundError:
    print("No Plant Configuration found")
    sys.exit(1)

# Inicializa un diccionario de listas donde se guardan las coordenadas x,y en el taller que corresponde
listaTaller = []
for taller in plant["Talleres_CiscoPrime"]:
    listaTaller.append(taller)
    plant["Talleres_CiscoPrime"][taller]["x"] = []
    plant["Talleres_CiscoPrime"][taller]["y"] = []

# Llama a la función para cargar los datos de todos los clientes en un diccionario
currentData = load_data()

""" plt.grid(True)
plt.xticks(ticks=[0, 50, 100, 150, 200, 250, 300, 350, 400])
plt.yticks(ticks=[0, 50, 100, 150, 200]) """
# plt.show()
fig = plt.gcf()  # se pasa el grafico como figura.
print(fig)
targetHall = "default"
#clientToFind = "l1pec023".upper()
#targetHall, fig = find_client(clientToFind)


# ------------------------------- Beginning of GUI CODE -------------------------------


# define the window layout
layout = [[sg.Text(targetHall, key="-TITLE-")],
          [sg.Canvas(expand_x=True, expand_y=True, key='-CANVAS-')],
          [sg.Combo(listaTaller, key="-TALLER-", disabled=True), sg.Checkbox("Buscar por taller ",
                                                                             key="-HALLSEARCH-", enable_events=True)],
          [sg.In(size=(25, 1), key="-SEARCH-")],
          [sg.Button('Buscar')]]

# create the form and show it without the plot
window = sg.Window('RunTrack View',
                   layout, finalize=True, element_justification='center', font='Helvetica 18', resizable=True)
window.maximize()
# add the plot to the window
fig_canvas_agg = draw_figure(window['-CANVAS-'].TKCanvas, fig)
print("after draw function call")
while True:
    event, values = window.read()
    print(event)
    print(values)
    if event == None or event == sg.WIN_CLOSED:
        break
    elif event == "-HALLSEARCH-":
        if values["-HALLSEARCH-"]:
            window["-SEARCH-"].update(disabled=True)
            window["-TALLER-"].update(disabled=False)
        if not values["-HALLSEARCH-"]:
            window["-SEARCH-"].update(disabled=False)
            window["-TALLER-"].update(disabled=True)
    elif event == "Buscar":
        if values["-HALLSEARCH-"]:
            print("buscando taller {}".format(values["-TALLER-"]))
            searchInfo = values["-TALLER-"]
            targetHall, returnCode = search(searchInfo, "HallSearch")
        elif not values["-HALLSEARCH-"]:
            searchInfo = values["-SEARCH-"].upper()
            targetHall, returnCode = search(searchInfo, "ClientSearch")
        else:
            print("Problema con el estado del CheckBox Buscar por Taller")
        if returnCode == "Success":
            window["-TITLE-"].update(targetHall)
            fig_canvas_agg.draw()
        else:
            pass
window.close()
