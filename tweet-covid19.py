import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema
import requests
import pycountry
from tqdm import tqdm
from datetime import datetime
import tweepy

# Configuraciones y Variables Globales
country_iso = "ARG"
style_plot = "fivethirtyeight"
cmap = "viridis"
csv_file = "owid-covid.csv"

API_Key = "Your_API_Key"
API_Key_Secret = "Your_API_Secret_Key"
Access_Token = "Your_Access_Token"
Access_Token_Secret = "Your_Access_Token_Secret"

def get_data(url="https://covid.ourworldindata.org/data/owid-covid-data.csv", outfile=csv_file):
    """
    Descarga los datos de COVID-19 desde el URL especificado y los guarda en un archivo CSV.

    Parámetros:
    url (str): URL desde donde se descargan los datos.
    outfile (str): Nombre del archivo donde se guardarán los datos.

    Manejo de Errores:
    - Verifica que la descarga sea completa.
    - Si hay un error durante la descarga, imprime un mensaje y termina la ejecución.
    """
    try:
        response = requests.get(url, stream=True)
        total_size_in_bytes = int(response.headers.get("content-length", 0))
        progress_bar = tqdm(total=total_size_in_bytes, unit="iB", unit_scale=True)
        with open(outfile, "wb") as file:
            for data in response.iter_content(1024):
                progress_bar.update(len(data))
                file.write(data)
        progress_bar.close()

        # Verificar si la descarga fue completa
        if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
            raise ValueError("La descarga del archivo no se completó correctamente.")
    
    except requests.exceptions.RequestException as e:
        print(f"Error durante la descarga: {e}")
        raise SystemExit(e)

# Descargar y cargar los datos
get_data()
try:
    df = pd.read_csv(csv_file, parse_dates=["date"])
except FileNotFoundError as e:
    print(f"Error: El archivo {csv_file} no fue encontrado. Asegúrate de que la descarga se completó correctamente.")
    raise SystemExit(e)

# Filtrar datos por país
country_data = df[df["iso_code"] == country_iso]
if country_data.empty:
    raise ValueError(f"No se encontraron datos para el código de país: {country_iso}")
    
country_name = pycountry.countries.get(alpha_3=country_iso).name

# Asignación de columnas relevantes
cols = ["date", "new_cases", "new_deaths", "new_cases_smoothed", 
        "new_deaths_smoothed", "new_vaccinations", 
        "new_vaccinations_smoothed", "new_tests", 
        "new_tests_smoothed", "excess_mortality", 
        "total_tests", "total_cases", "total_deaths", 
        "total_vaccinations", "people_fully_vaccinated_per_hundred"]

date, cases, deaths, cases_sm, death_sm, vax, vax_sm, tests, tests_sm, excess, total_tests, total_cases, total_deaths, total_vaccinations, full_vax_100 = [country_data[col] for col in cols]
population = country_data.iloc[-1]["population"]

def plot_main_graphs():
    """
    Genera y guarda una figura con cuatro gráficos:
    - Casos diarios y promedio de 7 días.
    - Muertes diarias y promedio de 7 días.
    - Vacunaciones diarias y promedio de 7 días.
    - Tests diarios y promedio de 7 días.
    
    Manejo de Errores:
    - Verifica que las columnas necesarias existan antes de graficar.
    """
    try:
        plt.style.use(style_plot)
        plt.rcParams["font.size"] = "20"
        fig1, axes = plt.subplots(2, 2, figsize=(32, 18))
        fig1.suptitle(country_name, fontsize=40)
        
        plots = [
            (axes[0, 0], date, cases, cases_sm, "Casos", "Casos diarios"),
            (axes[0, 1], date, deaths, death_sm, "Muertes", "Muertes diarias"),
            (axes[1, 0], date, vax, vax_sm, "Vacunaciones", "Vacunaciones diarias"),
            (axes[1, 1], date, tests, tests_sm, "Tests diarios", "Tests diarios")
        ]
        
        for ax, x, y1, y2, ylabel, title in plots:
            ax.plot(x, y1, linestyle="-", linewidth=0.5, alpha=0.5)
            ax.plot(x, y2, linestyle="-", linewidth=3, color="black")
            ax.set(ylabel=ylabel, title=title)

        fig1.tight_layout()
        plt.savefig("graficos-principales.png", dpi=150)
        plt.show()
    
    except KeyError as e:
        print(f"Error: No se encontró la columna necesaria para graficar: {e}")
        raise SystemExit(e)

def plot_combined_graphs():
    """
    Genera y guarda gráficos combinados:
    - Casos diarios suavizados y muertes diarias suavizadas.
    - Casos diarios suavizados y tests diarios suavizados.
    - Muertes diarias y personas completamente vacunadas.
    
    Manejo de Errores:
    - Verifica que las columnas necesarias existan antes de graficar.
    """
    try:
        plt.style.use(style_plot)

        # Casos nuevos y muertes nuevas suavizadas
        fig, ax = plt.subplots(figsize=(25, 12.5))
        ax.plot(date, cases_sm, color="green", linewidth=3)
        ax.fill_between(date, 0, cases_sm, alpha=0.1, color="green")
        ax.set(xlabel="Fecha", ylabel="Casos Diarios (promedio 7 días)")
        
        ax2 = ax.twinx()
        ax2.plot(date, death_sm, color="red", linewidth=3)
        ax2.set(ylabel="Muertes Diarias (promedio 7 días)")

        ilocs_max = argrelextrema(cases_sm.values, np.greater_equal, order=14)[0]
        ax.scatter(date.iloc[ilocs_max], cases_sm.iloc[ilocs_max], color="black", marker="p", lw=8)

        plt.tight_layout()
        plt.savefig("muertes-y-casos.png", dpi=150)

        # Otros gráficos combinados
        fig, ax = plt.subplots(figsize=(25, 12.5))
        ax.plot(date, cases_sm, color="green", linewidth=3)
        ax2 = ax.twinx()
        ax2.plot(date, tests_sm, color="blue", linewidth=3)
        ax.set(xlabel="Fecha", ylabel="Nuevos Casos")
        ax2.set(ylabel="Tests Suavizado")
        plt.tight_layout()
        plt.savefig("nuevos-casos-y-test.png", dpi=150)

        fig, ax = plt.subplots(figsize=(25, 12.5))
        ax.plot(date, deaths, color="red", linewidth=0.5)
        ax.fill_between(date, 0, deaths, alpha=0.1, color="red")
        ax2 = ax.twinx()
        ax2.plot(date, full_vax_100, color="blue", linewidth=3)
        ax.set(xlabel="Fecha", ylabel="Muertes Diarias")
        ax2.set(ylabel="Personas completamente vacunadas (cada 100)")
        plt.tight_layout()
        plt.savefig("Muertes-y-dosis.png", dpi=150)
    
    except KeyError as e:
        print(f"Error: No se encontró la columna necesaria para graficar: {e}")
        raise SystemExit(e)

def tweet_results():
    """
    Autentica con la API de Twitter y publica un tweet con el resumen del estado de COVID-19 en el país seleccionado,
    incluyendo gráficos generados anteriormente.

    Manejo de Errores:
    - Verifica la autenticación en Twitter.
    - Verifica que la subida de medios y el tweet se realicen correctamente.
    """
    try:
        auth = tweepy.OAuthHandler(API_Key, API_Key_Secret)
        auth.set_access_token(Access_Token, Access_Token_Secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)

        images = ["graficos-principales.png", "muertes-y-casos.png", "nuevos-casos-y-test.png", "Muertes-y-dosis.png"]
        media_ids = [api.media_upload(image).media_id for image in images]

        ultima_fecha = pd.to_datetime(country_data.iloc[-1]["date"]).date()
        total_muertos = total_deaths.iloc[-1]
        total_contagios = total_cases.iloc[-1]
        total_dosis = full_vax_100.iloc[-1]

        mensaje = (
            f"Resumen del estado COVID19 en {country_name} a la fecha {ultima_fecha.strftime('%d/%m/%Y')} (Datos de OWID): \n"
            f"Casos: {total_contagios} ({round(100 * total_contagios / population, 2)}% pobl.)\n"
            f"Muertes: {total_muertos} ({round(100 * total_muertos / population, 2)}% pobl.)\n"
            f"Personas completamente vacunadas (cada 100): {total_dosis}"
        )

        api.update_status(status=mensaje, media_ids=media_ids)
        print(f'Se publicó el siguiente tweet: {mensaje}')

    except tweepy.TweepError as e:
        print(f"Error al interactuar con la API de Twitter: {e}")
        raise SystemExit(e)

# Ejecución de las funciones
plot_main_graphs()
plot_combined_graphs()
tweet_results()
