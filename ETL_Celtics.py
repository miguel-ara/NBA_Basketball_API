import requests
import warnings
import sys
import signal
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import Crear_pdf as pdf
import Pronosticador as pronosticador

# Definimos como constantes los 3 endpoints o links de la API a los que
# haremos las peticiones más adelante

URL_INFO = "https://api.sportsdata.io/v3/nba/scores/json/Players/BOS"
URL_STATS = "https://api.sportsdata.io/v3/nba/projections/json/PlayerSeasonProjectionStatsByTeam/2022/BOS"
URL_EQUIPO = "https://api.sportsdata.io/v3/nba/scores/json/Standings/2023"


# Definimos un manejador de señales
def handler_signal(signal, frame):
    print("\n\n Interrupción! Saliendo del programa de manera ordenada")
    sys.exit(1)


# Definimos la señal de control usando el manejador de señales por si el
# usuario introduce Ctrl + C para parar el programa de forma ordenada. También
# cambiamos el número máximo de columnas que podemos imprimir de un dataframe,
# y definimos que no aparezcan por pantalla los avisos que no afectan a la
# ejecución del programa

signal.signal(signal.SIGINT, handler_signal)
pd.set_option('display.max_columns', 40)
warnings.filterwarnings('ignore')


def extract(url_info: str, url_stats: str, url_equipo: str):

    # Leemos el archivo de config.txt para obtener la clave de la API que el
    # usuario debe haber introducido en ese archivo previamente. Definimos los
    # headers que pasaremos como argumento al hacer una petición a la API

    api_key = eval(open('config.txt').read())['api-key']
    headers = {'Ocp-Apim-Subscription-Key': api_key}

    # Realizamos las 3 peticiones que necesitamos a la API con get, pasamos
    # las respuestas a json y creamos dataframes con dichos jsons, que es lo
    # que devolverá la función

    response = requests.get(url_info, headers=headers).json()
    info_players = pd.DataFrame(response)

    response = requests.get(url_stats, headers=headers).json()
    stats_players = pd.DataFrame(response)

    response = requests.get(url_equipo, headers=headers).json()
    stats_team = pd.DataFrame(response)

    return info_players, stats_players, stats_team


def transform(info_players: pd.DataFrame, stats_players: pd.DataFrame,
              stats_team: pd.DataFrame):

    # Recibe 3 dataframes, info_players con información general de los
    # jugadores, stats_players con estadísticas de los jugadores, stats_team
    # con estadísticas de los equipos

    # Primero, debemos filtrar stats_team para obtener solo las estadísticas
    # de los Boston Celtics, que es el quipo que nos interesa para hacer el
    # reporte ejecutivo pdf. Para ello ordenamos por la columna 'Key' y
    # accedemos a la tercera fila, que es la de los celtics

    stats_team = stats_team.sort_values(by='Key').head(3).tail(1)

    # Vamos a crear un dataframe boston que contenga la información que nos
    # interesa de los Celtics, una de las columnas de este dataframe contendrá
    # los nombres de ciertos apartados estadísticos y la otra columna
    # contendrá los valores de esos apartados estadísticos

    team_info = ['Conference', 'Division', 'Wins', 'Losses', 'Win Percentage',
                 'Home Wins', 'Home Losses', 'Away Wins', 'Away Losses',
                 'Points Scored Per Game', 'Points Received Per Game',
                 'Streak', 'Conference Rank']

    # Obtenemos por tanto solo las columnas que nos interesan del dataframe de
    # stats_team y luego accedemos a los valores del dataframe pasándolos a
    # una lista

    stats_team = stats_team[['Conference', 'Division', 'Wins', 'Losses',
                             'Percentage', 'HomeWins', 'HomeLosses',
                             'AwayWins', 'AwayLosses', 'PointsPerGameFor',
                             'PointsPerGameAgainst', 'Streak',
                             'ConferenceRank']].values.tolist()[0]

    boston = pd.DataFrame()
    boston['Stats'] = team_info
    boston['Values'] = stats_team

    # Añadimos y trasnformamos algunas columnas del dataframe de info_players.
    # Creamos una coluna con el nombre completo, renombramos las columnas con
    # la altura y el peso, rellenamos los NaNs de la columna de los salarios y
    # pasamos los valores de dicha columna a entero, algo que haremos también
    # con la columna de años jugados

    info_players['Name'] = info_players['FirstName'] + ' ' + info_players['LastName']
    info_players['Height(in)'] = info_players['Height']
    info_players['Weight(lb)'] = info_players['Weight']
    info_players['Salary($)'] = info_players['Salary'].fillna(
                                info_players['Salary'].mean()).astype(int)
    info_players['Years Played'] = info_players['Experience'].astype(int)

    # Una vez hemos transformado y las columnas que queríamos y tenemos el
    # dataframe procesado, obtenemos solo las columnas que nos interesan, que
    # son las que incluiremos en una tabla más adelante

    info_players = info_players[['Name', 'Position', 'Status', 'Jersey',
                                 'Height(in)', 'Weight(lb)', 'Salary($)',
                                 'Years Played', 'BirthCountry', 'BirthCity',
                                 'College']]

    # Para el dataframe de stats_players, obtenemos solo las columnas que nos
    # interesan, que son con las que crearemos una tabla más adelante

    stats_players = stats_players[['Name', 'Position', 'Games', 'Points',
                                   'Assists', 'Rebounds', 'OffensiveRebounds',
                                   'DefensiveRebounds', 'Steals',
                                   'BlockedShots', 'PersonalFouls',
                                   'Turnovers', 'FieldGoalsMade',
                                   'FieldGoalsPercentage',
                                   'TrueShootingPercentage', 'TwoPointersMade',
                                   'TwoPointersPercentage',
                                   'ThreePointersMade',
                                   'ThreePointersPercentage', 'FreeThrowsMade',
                                   'FreeThrowsPercentage']]

    # En casi todos los informes con estadísticas de la NBA, dentro de cada
    # categoría aparece el promedio por partido. Sin embargo, en el dataframe
    # hasta ahora tenemos la cantidad total para cada categoría y por lo tanto
    # vamos a dividir cada columna entre la columna de partidos jugados y
    # redondear el resultado a 2 decimales. De tal manera, para cada jugador
    # tendremos todas las estadísticas que tenía el dataframe pero ahora en
    # términos medios por partido. Al hacer esto, creamos nuevas columnas con
    # nombres abreviados para cada categoría

    stats_players['PPG'] = round((stats_players['Points'] /
                                 stats_players['Games']), 2)
    stats_players['APG'] = round((stats_players['Assists'] /
                                 stats_players['Games']), 2)
    stats_players['RPG'] = round((stats_players['Rebounds'] /
                                 stats_players['Games']), 2)
    stats_players['DRPG'] = round((stats_players['OffensiveRebounds'] /
                                  stats_players['Games']), 2)
    stats_players['ORPG'] = round((stats_players['DefensiveRebounds'] /
                                  stats_players['Games']), 2)
    stats_players['SPG'] = round((stats_players['Steals'] /
                                 stats_players['Games']), 2)
    stats_players['BPG'] = round((stats_players['BlockedShots'] /
                                 stats_players['Games']), 2)
    stats_players['PFPG'] = round((stats_players['PersonalFouls'] /
                                  stats_players['Games']), 2)
    stats_players['TPG'] = round((stats_players['Turnovers'] /
                                 stats_players['Games']), 2)
    stats_players['TSP'] = stats_players['TrueShootingPercentage']
    stats_players['FGMPG'] = round((stats_players['FieldGoalsMade'] /
                                   stats_players['Games']), 2)
    stats_players['FGP'] = stats_players['FieldGoalsPercentage']
    stats_players['2PMPG'] = round((stats_players['TwoPointersMade'] /
                                   stats_players['Games']), 2)
    stats_players['2PP'] = stats_players['TwoPointersPercentage']
    stats_players['3PMPG'] = round((stats_players['ThreePointersMade'] /
                                   stats_players['Games']), 2)
    stats_players['3PP'] = stats_players['ThreePointersPercentage']
    stats_players['FTMPG'] = round((stats_players['FreeThrowsMade'] /
                                   stats_players['Games']), 2)
    stats_players['FTP'] = stats_players['FreeThrowsPercentage']

    # Una vez hemos obtenido las nuevas columnas con las categorías ahora en
    # promedio por partido, eliminamos las columnas anteriores con las
    # cantidades totales, que ya no nos interesan. Esto lo hacemos con el
    # método drop de pandas, indicando con inplace=True que se modifique el
    # propio dataframe

    stats_players.drop(['Points', 'Assists', 'Rebounds', 'OffensiveRebounds',
                        'DefensiveRebounds', 'Steals', 'BlockedShots',
                        'PersonalFouls', 'Turnovers', 'FieldGoalsMade',
                        'FieldGoalsPercentage', 'TrueShootingPercentage',
                        'TwoPointersMade', 'TwoPointersPercentage',
                        'ThreePointersMade', 'ThreePointersPercentage',
                        'FreeThrowsMade', 'FreeThrowsPercentage'],
                       axis=1,
                       inplace=True)

    # Para facilitar la comprensión de las estadísticas de los jugadores,
    # vamos a crear un dataframe que asocie a cada abreviatura su significado
    # completo, lo cual incluiremos a modo de leyenda en una tabla al final
    # del reporte ejecutivo pdf. El dataframe lo llamaremos leyenda

    abreviaturas = ['PPG', 'APG', 'RPG', 'DRPG', 'ORPG', 'SPG', 'BPG', 'PFPG',
                    'TPG', 'TSP', 'FGMPG', 'FGP', '2PMPG', '2PP', '3PMPG',
                    '3PP', 'FTMPG', 'FTP']

    descripciones = ['Points Per Game', 'Assists Per Game',
                     'Rebounds Per Game', 'Defensive Rebounds Per Game',
                     'Offensive Rebounds Per Game', 'Steals Per Game',
                     'Blocks Per Game', 'Personal Fouls Per Game',
                     'Turnovers Per Game', 'True Shooting Percentage',
                     'Field Goals Made Per Game', 'Field Goals Percentage',
                     'Two Pointers Made Per Game', 'Two Pointers Percentage',
                     'Three Pointers Made Per Game',
                     'Three Pointers Percentage', 'Free Throws Made Per Game',
                     'Free Throws Percentage']

    leyenda = pd.DataFrame()
    leyenda['Abbreviations'] = abreviaturas
    leyenda['Descriptions'] = descripciones

    # La función devuelve el dataframe con la información de los jugadores ya
    # filtrado, el dataframe con las estadísticas de los jugadores con las
    # columnas renombradas y los datos trabajados para darlos en términos por
    # partido, el dataframe con la leyenda de las categorías o apartados
    # estadísticos, y el dataframe boston con la información que nos interesa
    # del equipo de los Celtics

    return info_players, stats_players, leyenda, boston


def load(info_players: pd.DataFrame, stats_players: pd.DataFrame,
         leyenda: pd.DataFrame, boston: pd.DataFrame):

    # Si no se han creado aún las carpetas que queremos para guardar todos los
    # archivos que vamos a generar, creamos dichas carpetas:
    # archivos_generados e imagenes

    if not os.path.exists('archivos_generados'):
        os.mkdir('archivos_generados')

    if not os.path.exists('imagenes'):
        os.mkdir('imagenes')

    # Cargamos los dataframes en archivos csv que metemos en la carpeta de
    # archivos_generados, por si al usuario le interesa visualizar los datos
    # obtenidos de esta manera

    info_players.to_csv('archivos_generados/Celtics_Players_2023.csv',
                        index=False)
    stats_players.to_csv('archivos_generados/Celtics_Players_Stats_2022.csv',
                         index=False)
    leyenda.to_csv('archivos_generados/Legend.csv',
                   index=False)
    boston.to_csv('archivos_generados/Boston_Stats.csv',
                  index=False)

    # Para los apartados estadísticos de puntos por partido, asistencias por
    # partido y rebotes por partido generamos un gráfico de barras en
    # horizontal con el top 6 mejores y con el top 6 peores. Para ello
    # tendremos que ir creando copias del dataframe original de stats_players
    # ordenándolo en orden ascendente y descentente por los valores de las 3
    # categorías, generando en total 6 dataframes adicionales. Le ponemos el
    # título a cada gráfica en verde y pintamos la gráfica con distintos tonos
    # de verde usando una paleta de seaborn. Cambiamos el tamaño de las
    # anotaciones del eje x. Guardamos las 6 imágenes dentro de la carpeta de
    # imagenes

    max_anotadores = stats_players.sort_values('PPG', ascending=False).head(6)
    sns.set_style('darkgrid')
    plt.figure()
    plt.title("Max Scorers", fontsize=28, fontweight='bold',
              color='forestgreen')
    ax = sns.barplot(y='Name', x='PPG', data=max_anotadores, orient='h',
                     palette=sns.light_palette("forestgreen", 8, reverse=True))
    plt.xticks(fontsize=10)
    plt.savefig('imagenes/Max_Scorers.png', dpi=300, bbox_inches='tight')

    min_anotadores = stats_players.sort_values('PPG', ascending=False).tail(6)
    plt.figure()
    plt.title("Min Scorers", fontsize=28, fontweight='bold',
              color='forestgreen')
    ax = sns.barplot(y='Name', x='PPG', data=min_anotadores, orient='h',
                     palette=sns.light_palette("forestgreen", 8, reverse=True))
    plt.xticks(fontsize=10)
    plt.savefig('imagenes/Min_Scorers.png', dpi=300, bbox_inches='tight')

    max_asisitentes = stats_players.sort_values('APG', ascending=False).head(6)
    sns.set_style('darkgrid')
    plt.figure()
    plt.title("Max Assistors", fontsize=28, fontweight='bold',
              color='forestgreen')
    ax = sns.barplot(y='Name', x='APG', data=max_asisitentes, orient='h',
                     palette=sns.light_palette("forestgreen", 8, reverse=True))
    plt.xticks(fontsize=10)
    plt.savefig('imagenes/Max_Assistors.png', dpi=300, bbox_inches='tight')

    min_asistentes = stats_players.sort_values('APG', ascending=False).tail(6)
    plt.figure()
    plt.title("Min Assistors", fontsize=28, fontweight='bold',
              color='forestgreen')
    ax = sns.barplot(y='Name', x='APG', data=min_asistentes, orient='h',
                     palette=sns.light_palette("forestgreen", 8, reverse=True))
    plt.xticks(fontsize=10)
    plt.savefig('imagenes/Min_Assistors.png', dpi=300, bbox_inches='tight')

    max_rebounders = stats_players.sort_values('RPG', ascending=False).head(6)
    sns.set_style('darkgrid')
    plt.figure()
    plt.title("Max Rebounders", fontsize=28, fontweight='bold',
              color='forestgreen')
    ax = sns.barplot(y='Name', x='RPG', data=max_rebounders, orient='h',
                     palette=sns.light_palette("forestgreen", 8, reverse=True))
    plt.xticks(fontsize=10)
    plt.savefig('imagenes/Max_Rebounders.png', dpi=300, bbox_inches='tight')

    min_rebounders = stats_players.sort_values('RPG', ascending=False).tail(6)
    plt.figure()
    plt.title("Min Rebounders", fontsize=28, fontweight='bold',
              color='forestgreen')
    ax = sns.barplot(y='Name', x='RPG', data=min_rebounders, orient='h',
                     palette=sns.light_palette("forestgreen", 8, reverse=True))
    plt.xticks(fontsize=10)
    plt.savefig('imagenes/Min_Rebounders.png', dpi=300, bbox_inches='tight')

    # Para generar las tablas, creamos un nuevo dataframe que sea el de
    # info_players sin la columa de nombres, ya que queremos que aparezca
    # dicha columna a modo de índice en la tabla. Lo mismo hacemos con el
    # dataframe de stats_players

    info_sin_nombres = info_players.drop(['Name'], axis=1)
    info_nombres = info_players['Name'].to_list()

    stats_sin_nombres = stats_players.drop(['Name'], axis=1)
    stats_nombres = stats_players['Name'].to_list()

    # Creamos en total 4 tablas, todas con los nombres de las columnas y filas
    # coloreadas en verde. Ponemos los títulos en verde también. Debemos
    # quitar los ejes para que no aparezcan de fondo en las imágenes que se
    # generan. Debemos centrar los valores de cada celda y definir la anchura
    # de las columnas de la tabla. Además, para que sea más visual, cambiamos
    # el tamaño de fuente de las celdas. Por último, guardamos las tablas como
    # imagénes dentro de la carpeta de imagenes. Tenemos 4 dataframes y
    # creamos una tabla con cada uno de ellos

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.axis('tight')
    ax.axis('off')
    plt.title('Boston Celtics Players Stats 2022', fontsize=24,
              fontweight='bold', color='forestgreen')
    tabla1 = ax.table(cellText=stats_sin_nombres.values,
                      rowColours=['palegreen']*len(stats_sin_nombres),
                      colColours=['palegreen']*len(stats_sin_nombres.columns),
                      cellLoc='center', colWidths=[0.052]*20,  loc='center',
                      rowLabels=stats_nombres,
                      colLabels=stats_sin_nombres.columns)
    tabla1.auto_set_font_size(False)
    tabla1.set_fontsize(7)
    plt.savefig('imagenes/Celtics_Players_Stats_2022.png', dpi=400,
                bbox_inches='tight')

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.axis('tight')
    ax.axis('off')
    plt.title('Boston Celtics Players 2023', fontsize=24, fontweight='bold',
              color='forestgreen')
    tabla3 = ax.table(cellText=info_sin_nombres.values,
                      rowColours=['palegreen']*len(info_sin_nombres),
                      rowLabels=info_nombres,
                      colColours=['palegreen']*len(info_sin_nombres.columns),
                      cellLoc='center', colLabels=info_sin_nombres.columns,
                      loc='center',
                      colWidths=[0.08, 0.08, 0.08, 0.08, 0.08, 0.11, 0.09,
                                 0.14, 0.155, 0.12])
    tabla3.auto_set_font_size(False)
    tabla3.set_fontsize(8)
    plt.savefig('imagenes/Celtics_Players_2023.png', dpi=300,
                bbox_inches='tight')

    fig, ax = plt.subplots(figsize=(4, 5))
    ax.axis('tight')
    ax.axis('off')
    plt.title('Legend', fontsize=20, fontweight='bold', color='forestgreen')
    tabla2 = ax.table(cellText=leyenda.values, colColours=['palegreen']*2,
                      cellLoc='left', colWidths=[0.25, 0.55],
                      colLabels=['Abbreviations', 'Descriptions'],
                      loc='center')
    tabla2.auto_set_font_size(False)
    tabla2.set_fontsize(7)
    plt.savefig('imagenes/Legend.png', dpi=300, bbox_inches='tight')

    fig, ax = plt.subplots(figsize=(3, 3))
    ax.axis('tight')
    ax.axis('off')
    plt.title('Team Stats', fontsize=16, fontweight='bold',
              color='forestgreen')
    tabla4 = ax.table(cellText=boston.values, colColours=['palegreen']*2,
                      cellLoc='left', colWidths=[0.7, 0.25],
                      colLabels=['Stats', 'Values'], loc='center')
    tabla4.auto_set_font_size(False)
    tabla4.set_fontsize(8)
    plt.savefig('imagenes/Team_Stats.png', dpi=300, bbox_inches='tight')

    # Ahora vamos a crear 2 gráficos de barra más, uno con las victorias y
    # derrotas del equipo en esta temporada NBA 22-23, y otro con los puntos
    # anotados y recibidos de media por partido. Para ello definimos un estilo
    # y una paleta de seaborn. Ponemos los títulos de ambas gráficas en verde
    # y cambiamos el tamaño de las anotaciones del eje x. Para pintar estas
    # gráficas usaremos el dataframe de boston. Guardamos las dos imágenes
    # en la carpeta de imagenes

    sns.set_style('darkgrid')
    sns.set_palette('Set2')
    plt.figure(figsize=(6, 8))
    plt.title("Wins/Losses", fontsize=32, fontweight='bold',
              color='forestgreen')
    ax = sns.barplot(x=['Wins', 'Losses'],
                     y=[boston['Values'][2], boston['Values'][3]])
    plt.xticks(fontsize=16)
    plt.savefig('imagenes/Wins_Losses.png', dpi=300, bbox_inches='tight')

    plt.figure(figsize=(6, 8))
    plt.title("Points Per Game", fontsize=32, fontweight='bold',
              color='forestgreen')
    ax = sns.barplot(x=['Scored', 'Received'],
                     y=[boston['Values'][9], boston['Values'][10]])
    plt.xticks(fontsize=16)
    plt.savefig('imagenes/Points_per_game.png', dpi=300, bbox_inches='tight')

    # Generamos ahora dos gráficos circulares conocidos como pie charts usando
    # el dataframe de boston. El primero será con las victorias y derrotas en
    # casa, y el segundo será con las victorias y derrotas fuera de casa,
    # incluyendo en ambos casos los porcentajes. Guardamos las dos imágenes
    # en la carpeta de imagenes

    expandir = [0, 0]
    plt.figure()
    plt.title("Home Stats", fontsize=32, fontweight='bold',
              color='forestgreen')
    plt.pie([boston['Values'][5], boston['Values'][6]], expandir,
            ['Wins', 'Losses'], autopct='%.0f%%',
            textprops={'size': 16, 'fontweight': 'bold'})
    plt.savefig('imagenes/Home.png', dpi=300, bbox_inches='tight')

    plt.figure()
    plt.title("Away Stats", fontsize=32, fontweight='bold',
              color='forestgreen')
    plt.pie([boston['Values'][7], boston['Values'][8]], expandir,
            ['Wins', 'Losses'], autopct='%.0f%%',
            textprops={'size': 16, 'fontweight': 'bold'})
    plt.savefig('imagenes/Away.png', dpi=300, bbox_inches='tight')

    # Por último usando la librería requests obtenemos con links una imagen
    # del logo de los Celtics y una imagen de Jayson Tatum jugando un partido.
    # Guardamos ambas en la carpeta de imagenes accediendo al contenido de la
    # respuesta

    f = open('imagenes/Celtics_logo.png', 'wb')
    response = requests.get('https://s3.amazonaws.com/freebiesupply/large/2x/boston-celtics-logo-transparent.png')
    f.write(response.content)
    f.close()

    f2 = open('imagenes/Jayson_Tatum.jpg', 'wb')
    response = requests.get('https://wallpaper.dog/large/10929455.jpg')
    f2.write(response.content)
    f2.close()


def ETL(url_info: str, url_stats: str, url_equipo: str):

    # Extraemos los datos en forma de dataframe de la API usando los 3
    # endpoints o links que se pasan como argumento a la función,
    # transformamos los dataframes limpiando y añadiendo columnas y por último
    # cargamos los datos en gráficas (imágenes) y archivos (csv)

    info_players, stats_players, stats_team = extract(url_info,
                                                      url_stats,
                                                      url_equipo)
    info_procesado, stats_procesado, leyenda, boston = transform(info_players,
                                                                 stats_players,
                                                                 stats_team)
    load(info_procesado, stats_procesado, leyenda, boston)


if __name__ == '__main__':

    # Llamamos a la función ETL (Extract Transform Load) con los tres
    # endpoints de la API como argumentos. Después de haber generado todos los
    # archivos e imágenes, llamamos a la función crear_reporte_ejecutivo de la
    # librería Crear_pdf que nos hemos definido en otro archivo .py, y por
    # último llamamos a la función pronostica de la librería Pronosticador que
    # nos hemos definido también en otro archivo .py

    ETL(URL_INFO, URL_STATS, URL_EQUIPO)
    pdf.crear_reporte_GM('Boston_Celtics')
    pronosticador.pronostica('Boston Celtics')
