import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import json
import sys

try:
    with open("ClientPosition.json", "r") as pos:
        currentData = json.load(pos)
except FileNotFoundError:
    print("No Client Positions File found")
    sys.exit(1)

try:
    with open("plantConfig.json", "r") as conf:
        plant = json.load(conf)
except FileNotFoundError:
    print("No Plant Configuration found")
    sys.exit(1)

clientToFind = sys.argv[1].upper()

if clientToFind in currentData:
    targetHall = currentData[clientToFind]["Taller"]
    print(targetHall)
else:
    print("Client not found")
    sys.exit(0)
# Inicializa un diccionario de listas donde se guardan las coordenadas x,y en el taller que corresponde

for taller in plant["Talleres_CiscoPrime"]:
    plant["Talleres_CiscoPrime"][taller]["x"] = []
    plant["Talleres_CiscoPrime"][taller]["y"] = []

# x = {"T08C0": [], "T08C5": [], "T09C0": [], "T09C5": [],
#     "T10C0": [], "T10C5": [], "T11C0": [], "T11C5": []}
# y = {"T08C0": [], "T08C5": [], "T09C0": [], "T09C5": [],
#     "T10C0": [], "T10C5": [], "T11C0": [], "T11C5": []}

for client in currentData:
    if currentData[client]["Taller"] in plant["Talleres_CiscoPrime"]:
        plant["Talleres_CiscoPrime"][currentData[client]["Taller"]
                                     ]["x"].append(currentData[client]["Coordenadas"][0])
        plant["Talleres_CiscoPrime"][currentData[client]["Taller"]
                                     ]["y"].append(currentData[client]["Coordenadas"][1])
    else:
        print(currentData[client]["Taller"] + " not found in plantConfig.json")

#layout = './VCG/TALLER 11 MONTAJE-EG-L9-GVC.png'
#layout = './VCG/TALLER 8 MONTAJE-EG-L9-GVC.png'
#layout = './VCG/TALLER 8 MONTAJE-E1-L9-GVC.png'
#layout = './VCG/TALLER 9 MONTAJE-EG-L9-GVC.png'
#layout = './VCG/TALLER 9 MONTAJE-E1-L9-GVC.png'
#layout = './VCG/TALLER 10 MONTAJE-EG-L9-GVC.png'
#layout = './VCG/TALLER 10 MONTAJE-E1-L9-GVC.png'
layout = plant["Talleres_CiscoPrime"][targetHall]["RutaLayout"]

img = mpimg.imread(layout)
mpimg.AxesImage('x')
# imshow() carga la imagen especificada al fondo del gráfico. La propiedad extent es necesaria definirla para que la imagen solo llene el área que deseamos. Si se omite, se carga la imagen en tamaño real haciendo los ejes tan extensos como sea necesario para abarcar la imagen.
# plt.imshow(img, extent=(-0.5, 420, 221, -0.5))  # T11
plt.imshow(img, extent=(plant["Talleres_CiscoPrime"][targetHall]["AjusteEjes"][0], plant["Talleres_CiscoPrime"][targetHall]["AjusteEjes"]
           [1], plant["Talleres_CiscoPrime"][targetHall]["AjusteEjes"][2], plant["Talleres_CiscoPrime"][targetHall]["AjusteEjes"][3]))  # T08 C0
# plt.imshow(img, extent=(-0.5, 425, 233, -0.5))  # T08 C5
# plt.imshow(img, extent=(-0.5, 430, 260, -0.5))  # T09 C0
# plt.imshow(img, extent=(-0.5, 430, 260, -0.5))  # T09 C5
# plt.imshow(img, extent=(-0.5, 450, 200, -0.5))  # T10 C0
# plt.imshow(img, extent=(-0.5, 450, 200, -0.5))  # T10 C5

#plt.scatter(x["T11C0"], y["T11C0"], marker='o')
# plt.scatter(plant["Talleres_CiscoPrime"][targetHall]["x"], plant["Talleres_CiscoPrime"][targetHall]["y"], marker='o') # Show all clients in a hall
plt.scatter(currentData[clientToFind]["Coordenadas"][0],
            currentData[clientToFind]["Coordenadas"][1], marker='o')  # Show only the desired client
plt.grid(True)
plt.xticks(ticks=[0, 50, 100, 150, 200, 250, 300, 350, 400])
plt.yticks(ticks=[0, 50, 100, 150, 200])
plt.show()
