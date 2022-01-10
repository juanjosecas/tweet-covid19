"""

Los datos se descargan de
https://covid.ourworldindata.org/data/owid-covid-data.csv

Tienen actualización diaria en la mayoría de los casos

"""

import pandas as pd  # Pandas
import numpy as np  # numpy para cuentas
import matplotlib.pyplot as plt  # para graficar
from scipy.signal import argrelextrema  # para encontrar los máximos y mínimos
from sklearn.linear_model import LinearRegression  # para hacer regresion lineal
import requests  # para descargar la base de datos
import sys  # me permite tener a mano una forma de cortar el script cuando lo estoy probando, como si fueran secciones con 'sys.exit()'
import pycountry  # Convierte los códigos de paises en nombres y otras cosas
from tqdm import tqdm  # permite monitorear la descarga del archivo


def get_data(
    url="https://covid.ourworldindata.org/data/owid-covid-data.csv",
    outfile="owid-covid.csv",
):

    # Streaming, so we can iterate over the response.
    response = requests.get(url, stream=True)
    total_size_in_bytes = int(response.headers.get("content-length", 0))
    block_size = 1024  # 1 Kibibyte
    progress_bar = tqdm(total=total_size_in_bytes, unit="iB", unit_scale=True)
    with open(outfile, "wb") as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    progress_bar.close()
    if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
        print("ERROR, something went wrong")
        sys.exit()


# dESCARGA EL ARCHIVO DE owid

get_data()

# Lo guarda en un csv
csv_file = "owid-covid.csv"

# carga el csv
df = pd.read_csv(csv_file)
df["date"] = pd.to_datetime(df["date"]) # cambia la columna a un formato de fecha de Pandas

# Sección del país que me interesa
# se utilizan los códigos ISO de tres letras, ARG es Argentina

"""
ARG  Argentina
AUS  Australia
BRA  Brasil
CAN  Canadá
CHE  Suiza
CHL  Chile
CHN  China
DEU  Alemania
DNK  Dinamarca
ESP  España
GBR  Reino Unido de Gran Bretaña e Irlanda del Norte
ISL  Islandia
ISR  Israel
ITA  Italia
MEX  México
NZL  Nueva Zelandia
SWE  Suecia
URY  Uruguay
USA  Estados Unidos de America (los)
"""

country_iso = "ARG"
country_data = df[df["iso_code"] == country_iso]
country_name = pycountry.countries.get(alpha_3=country_iso).name

date = country_data["date"]
cases = country_data["new_cases"]
deaths = country_data["new_deaths"]
cases_sm = country_data["new_cases_smoothed"]
death_sm = country_data["new_deaths_smoothed"]
vax = country_data["new_vaccinations"]
vax_sm = country_data["new_vaccinations_smoothed"]
tests = country_data["new_tests"]
tests_sm = country_data["new_tests_smoothed"]
excess = country_data["excess_mortality"]
total_tests = country_data["total_tests"]
total_cases = country_data["total_cases"]
total_deaths = country_data["total_deaths"]
total_vaccinations = country_data["total_vaccinations"]
full_vax_100 = country_data["people_fully_vaccinated_per_hundred"]
population = country_data.iloc[-1]["population"]


# Configuraciones generales para todos los gráficos

"""
Estilos disponibles (muchos!)
bmh
classic
fivethirtyeight
ggplot
grayscale
seaborn-bright
seaborn-colorblind
seaborn-darkgrid
seaborn-deep
seaborn-paper


Lista de colores: https://matplotlib.org/stable/gallery/color/named_colors.html

b: blue
g: green
r: red
c: cyan
m: magenta
y: yellow
k: black
w: white

grey
brown
indianred
red
salmon
darkorange
orange
gold
khaki
olive
yellow
lawngreen
sage
palegreen
lightgreen
green
aquamarine
turquoise
teal
cyan
dodgerblue
slategrey
royalblue
navy
blue
indigo
violet
magenta
orchid
crimson
pink
"""
style_plot = "fivethirtyeight"  # confgura el tema visual del plot

"""
Mapas de color disponibles
El predeterminado es 'jet' y es bastante malo porque tiene una escala de múltiples colores en vez de una escala continua de un color a otro

('Perceptually Uniform Sequential', [
            'viridis', 'plasma', 'inferno', 'magma', 'cividis']),

('Sequential', [
            'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
            'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
            'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']),

'Sequential (2)', [
            'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
            'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
            'hot', 'afmhot', 'gist_heat', 'copper']),

'Diverging', [
            'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
            'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic']),

"""

cmap = "viridis"  # configura el mapa de color

"""
Este es el gráfico más importante, me parece. No lo voy a condicionar para que siempre se genere.


Una figura con 4 gráficos

Casos Diarios + Suavizado           |       Muertes diarias + Suavizado

Vacunaciones Diarias + Suavizado    |       Tests Diarios + Suavizado

"""

graficos_principales = True

if graficos_principales:

    with plt.style.context(style_plot):
        # Creación de la figura
        plt.rcParams["font.size"] = "20"
        fig1, ((casos, muertes), (vacunaciones, testeos)) = plt.subplots(
            2, 2, figsize=(32, 18)
        )
        fig1.suptitle(country_name, fontsize=40)

        # casos diarios nuevos, casos diarios nuevos suavizados
        casos.plot(
            date,
            cases,
            linestyle="-",
            linewidth=0.5,
            color="blue",
            label="Casos Diarios",
            alpha=0.5,
        )
        casos.plot(
            date,
            cases_sm,
            linestyle="-",
            linewidth=3,
            color="black",
            label="Promedio 7 días",
        )
        casos.set(ylabel="Casos", title="Casos diarios")

        # muertes diarios nuevos, muertes diarios nuevos suavizados
        muertes.plot(
            date,
            deaths,
            linestyle="-",
            linewidth=0.5,
            color="red",
            label="Muertes Diarias",
            alpha=0.5,
        )
        muertes.plot(
            date,
            death_sm,
            linestyle="-",
            linewidth=3,
            color="black",
            label="Promedio 7 días",
        )
        muertes.set(ylabel="Muertes", title="Muertes diarias")

        # vacunaciones diarios nuevos, vacunaciones diarios nuevos suavizados
        vacunaciones.plot(
            date,
            vax,
            linestyle="-",
            linewidth=0.5,
            color="green",
            label="Vacunación",
            alpha=0.5,
        )
        vacunaciones.plot(
            date,
            vax_sm,
            linestyle="-",
            linewidth=3,
            color="black",
            label="Promedio 7 días",
        )
        vacunaciones.set(
            xlabel="Fecha", ylabel="Vacunaciones", title="Vacunaciones diarias"
        )

        # testeos diarios nuevos, testeos diarios nuevos suavizados
        testeos.plot(
            date,
            tests,
            linestyle="-",
            linewidth=0.5,
            color="orange",
            label="Tests",
            alpha=0.5,
        )
        testeos.plot(
            date,
            tests_sm,
            linestyle="-",
            linewidth=3,
            color="black",
            label="Promedio 7 días",
        )
        testeos.set(xlabel="Fecha", ylabel="Tests diarios", title="Tests diarios")

        fig1.tight_layout()

        plt.savefig("graficos-principales.png", dpi=150)
        plt.show()


"""
Gráfico superpuesto de casos y muertes
"""

casos_superpuestos = True

if casos_superpuestos:
    with plt.style.context(style_plot):  # Casos nuevos y muertes nuevas suavizadas
        # crear la figura
        fig, ax = plt.subplots(figsize=(25, 12.5))
        fig.suptitle(country_name)
        ax.plot(date, cases_sm, color="green", linewidth=3)
        ax.set(xlabel="Fecha", ylabel="Casos Diarios (promedio 7 días)")
        ax.fill_between(date, 0, cases_sm, alpha=0.1, color="green")
        # usamos el mismo eje x
        ax2 = ax.twinx()
        ax2.plot(date, death_sm, color="red", linewidth=3)
        ax2.set(ylabel="Muertes Diarias (promedio 7 días)")

        # Picos, sirve para detectar los picos con una ventana de 14 días
        ilocs_max = argrelextrema(
            country_data["new_cases_smoothed"].values, np.greater_equal, order=14
        )[0]
        date_peak = country_data.iloc[ilocs_max]["date"]
        cases_peak = country_data.iloc[ilocs_max]["new_cases_smoothed"]
        ax.scatter(date_peak, cases_peak, color="black", marker="p", lw=8)

        plt.tight_layout()

        plt.savefig("muertes-y-casos.png", dpi=150)

    with plt.style.context(style_plot):

        fig, ax = plt.subplots(figsize=(25, 12.5))
        fig.suptitle(country_name)
        ax.plot(date, cases_sm, color="green", linewidth=3)
        ax.set(xlabel="Fecha", ylabel="Nuevos Casos")

        ax2 = ax.twinx()
        ax2.plot(date, tests_sm, color="blue", linewidth=3)
        ax2.set(ylabel="Tests Suavizado")

        plt.tight_layout()

        plt.savefig("nuevos-casos-y-test.png", dpi=150)

    with plt.style.context(style_plot):  # Casos nuevos y muertes diarios
        # crear la figura
        fig, ax = plt.subplots(figsize=(25, 12.5))
        ax.plot(date, cases, color="green", linewidth=3)
        ax.set(xlabel="Fecha", ylabel="Casos Diarios")
        ax.fill_between(date, 0, cases, alpha=0.1, color="green")
        # usamos el mismo eje x
        ax2 = ax.twinx()
        ax2.plot(date, deaths, color="red", linewidth=3)
        ax2.set(ylabel="Muertes Diarias")

        # Picos, sirve para detectar los picos con una ventana de 14 días
        ilocs_max = argrelextrema(
            country_data["new_cases"].values, np.greater_equal, order=14
        )[0]
        date_peak = country_data.iloc[ilocs_max]["date"]
        cases_peak = country_data.iloc[ilocs_max]["new_cases"]
        ax.scatter(date_peak, cases_peak, color="black", marker="p", lw=8)

        plt.tight_layout()

        plt.savefig("Casos-diarios-y-muertes-diarias.png", dpi=150)

    # muertes diarias y vacunas acumuladas
    with plt.style.context(style_plot):
        # crear la figura
        fig, ax = plt.subplots(figsize=(25, 12.5))
        ax.plot(date, deaths, color="red", linewidth=0.5)
        ax.set(xlabel="Fecha", ylabel="Muertes Diarias")
        ax.fill_between(date, 0, deaths, alpha=0.1, color="red")
        # usamos el mismo eje x
        ax2 = ax.twinx()
        ax2.plot(date, full_vax_100, color="blue", linewidth=3)
        ax2.set(ylabel="Personas completamente vacunadas (cada 100)")

        # Picos, sirve para detectar los picos con una ventana de 14 días
        ilocs_max = argrelextrema(
            country_data["new_deaths"].values, np.greater_equal, order=30
        )[0]
        date_peak = country_data.iloc[ilocs_max]["date"]
        cases_peak = country_data.iloc[ilocs_max]["new_deaths"]
        ax.scatter(date_peak, cases_peak, color="black", marker="p", lw=8)

        plt.tight_layout()
        plt.savefig("Muertes-y-dosis.png", dpi=150)


from datetime import datetime

# Tuitear los resultados

import tweepy

API_Key = "123123SADJASJKLASJKLJKLASDJKAS"
API_Key_Secret = "12312312123434SADJASJKLASJKLJKLASDJKAS"
Access_Token = "122SADJASJKLASJKLJKLASDJKAS"
Access_Token_Secret = "XV5SADJASJKLASJKLJKLASDJKAS"

# Authenticate to Twitter
auth = tweepy.OAuthHandler(API_Key, API_Key_Secret)
auth.set_access_token(Access_Token, Access_Token_Secret)

# iniciar API
api = tweepy.API(auth, wait_on_rate_limit=True)

images = [
    "graficos-principales.png",
    "Casos-diarios-y-muertes-diarias.png",
    "Muertes-y-dosis.png",
]

media_ids = []
for image in images:
    res = api.media_upload(image)
    media_ids.append(res.media_id)

ultima_fecha = pd.to_datetime(country_data.iloc[-1]["date"]).date()
total_muertos = country_data.iloc[-1]["total_deaths"]
total_dosis = country_data.iloc[-1]["people_fully_vaccinated_per_hundred"]
total_contagios = country_data.iloc[-1]["total_cases"]

mensaje = (
    "Resumen del estado COVID19 en "
    + country_name
    + " a la fecha "
    + ultima_fecha.strftime("%d/%m/%Y")
    + " (Datos de OWID): \nCasos: "
    + str(total_contagios)
    + " ("
    + str(round(100 * total_contagios / population, 2))
    + " % pobl.)"
    + "\nMuertes: "
    + str(total_muertos)
    + " ("
    + str(round(100 * total_muertos / population, 2))
    + " % pobl.)"
    + "\nPersonas completamente vacunadas (cada 100): "
    + str(total_dosis)
)

# Tweet with multiple images

print('Se publicó el siguiente tweet: ',mensaje)

api.update_status(status=mensaje, media_ids=media_ids)

"""
iso_code 	            ISO 3166-1 alpha-3 – three-letter country codes
continent 	            Continent of the geographical location
location 	            Geographical location
date 	                Date of observation
population 	            Population
population_density 	    Number of people divided by land area, measured in square kilometers, most recent year available
median_age 	            Median age of the population, UN projection for 2020
aged_65_older 	        Share of the population that is 65 years and older, most recent year available
aged_70_older 	        Share of the population that is 70 years and older in 2015
gdp_per_capita 	        Gross domestic product at purchasing power parity (constant 2011 international dollars)
extreme_poverty 	    Share of the population living in extreme poverty, most recent year available since 2010
cardiovasc_death_rate 	Death rate from cardiovascular disease in 2017 (annual number of deaths per 100,000 people)
diabetes_prevalence 	Diabetes prevalence (% of population aged 20 to 79) in 2017
female_smokers 	        Share of women who smoke, most recent year available
male_smokers 	        Share of men who smoke, most recent year available
handwashing_facilities 	Share of the population with basic handwashing facilities on premises, most recent year available
hospital_beds_per_thousand 	Hospital beds per 1,000 people, most recent year available since 2010
life_expectancy 	    Life expectancy at birth in 2019
human_development_index
total_cases 	                Total confirmed cases of COVID-19
new_cases 	                    New confirmed cases of COVID-19
new_cases_smoothed 	            New confirmed cases of COVID-19 (7-day smoothed)
total_cases_per_million         Total confirmed cases of COVID-19 per 1,000,000 people
new_cases_per_million 	        New confirmed cases of COVID-19 per 1,000,000 people
new_cases_smoothed_per_million 	New confirmed cases of COVID-19 (7-day smoothed) per 1,000,000 people
total_deaths 	            Total deaths attributed to COVID-19
new_deaths 	                New deaths attributed to COVID-19
new_deaths_smoothed 	    New deaths attributed to COVID-19 (7-day smoothed)
total_deaths_per_million 	Total deaths attributed to COVID-19 per 1,000,000 people
new_deaths_per_million 	    New deaths attributed to COVID-19 per 1,000,000 people
new_deaths_smoothed_per_million 	New deaths attributed to COVID-19 (7-day smoothed) per 1,000,000 people
excess_mortality 	            Percentage difference between the reported number of weekly or monthly deaths in 2020–2021 and the projected number of deaths for the same period based on previous years.
excess_mortality_cumulative     Percentage difference between the cumulative number of deaths since 1 January 2020 and the cumulative projected deaths for the same period based on previous years.
excess_mortality_cumulative_absolute 	    Cumulative difference between the reported number of deaths since 1 January 2020 and the projected number of deaths for the same period based on previous years.
excess_mortality_cumulative_per_million 	Cumulative difference between the reported number of deaths since 1 January 2020 and the projected number of deaths for the same period based on previous years, per million people. For more information, see https://github.com/owid/covid-19-data/tree/master/public/data/excess_mortality
icu_patients 	            Number of COVID-19 patients in intensive care units (ICUs) on a given day
icu_patients_per_million 	Number of COVID-19 patients in intensive care units (ICUs) on a given day per 1,000,000 people
hosp_patients 	            Number of COVID-19 patients in hospital on a given day
hosp_patients_per_million 	Number of COVID-19 patients in hospital on a given day per 1,000,000 people
weekly_icu_admissions 	    Number of COVID-19 patients newly admitted to intensive care units (ICUs) in a given week
weekly_icu_admissions_per_million 	Number of COVID-19 patients newly admitted to intensive care units (ICUs) in a given week per 1,000,000 people
weekly_hosp_admissions 	    Number of COVID-19 patients newly admitted to hospitals in a given week
weekly_hosp_admissions_per_million 	Number of COVID-19 patients newly admitted to hospitals in a given week per 1,000,000 people
stringency_index 	        Government Response Stringency Index: composite measure based on 9 response indicators including school closures, workplace closures, and travel bans, rescaled to a value from 0 to 100 (100 = strictest response)
reproduction_rate 	        Real-time estimate of the effective reproduction rate (R) of COVID-19. See https://github.com/crondonm/TrackingR/tree/main/Estimates-Database
"""
