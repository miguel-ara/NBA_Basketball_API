from fpdf import FPDF


class PDF(FPDF):

    # Esta clase servirá para manejar el pdf

    def footer(self):

        # Ponemos un pie de página con el número de página, se incluirá de
        # manera automática al añadir una página al pdf

        self.set_y(-20)
        self.set_font('Times', '', 11)
        self.cell(0, 10, f'Página {str(self.page_no())}', align='C',
                  border=False)

    def colour_rect(self):

        # Crea bordes de página y los colorea. Esto se consigue pintando
        # primero un rectángulo verde y luego por encima de este, otro
        # rectángulo blanco

        self.set_fill_color(0, 255, 0)
        self.rect(5, 5, 287, 200, 'DF')
        self.set_fill_color(255, 255, 255)
        self.rect(8, 8, 281, 194, 'DF')

    def portada(self):

        # Añade la página de la portada con el título del reporte pdf y una
        # imagen con el logo del equipo, los Boston Celtics

        self.add_page()
        self.colour_rect()
        self.set_xy(0, 25)
        self.set_font('Times', 'B', 40)
        self.cell(w=297.0, h=20.0, align='C', txt="BOSTON CELTICS",
                  border=False, ln=True)
        self.set_xy(0, 45)
        self.cell(w=297.0, h=20.0, align='C', txt="PLAYERS & TEAM ANALYSIS",
                  border=False, ln=True)
        self.image('imagenes/Celtics_logo.png', 95, 70, 105)
        self.set_font('Times', 'B', 15)
        self.set_y(-25)
        self.cell(0, 5, align='R', txt="Miguel Ara Adánez   ",
                  border=False, ln=True)

    def team_stats1(self):

        # Añade una página con estadísticas generales del equipo, una tabla y
        # una imagen

        self.add_page()
        self.colour_rect()
        self.image('imagenes/Team_Stats.png', 25, 35, 115)
        self.image('imagenes/Points_per_game.png', 155, 30, 110)

    def team_stats2(self):

        # Añade una página con estadísticas sobre las victorias y derrotas del
        # equipo, tres imágenes en total

        self.add_page()
        self.colour_rect()
        self.image('imagenes/Wins_Losses.png', 30, 25, 120)
        self.image('imagenes/Home.png', 180, 25, 75)
        self.image('imagenes/Away.png', 180, 115, 75)

    def scorers(self):

        # Añade una página que incluye una imagen con los máximos anotadores y
        # otra con los mínimos

        self.add_page()
        self.colour_rect()
        self.image('imagenes/Max_Scorers.png', 9, 40, 137, 130)
        self.image('imagenes/Min_Scorers.png', 147, 40, 137, 130)

    def assistors(self):

        # Añade una página que incluye una imagen con los máximos asistentes y
        # otra con los mínimos

        self.add_page()
        self.colour_rect()
        self.image('imagenes/Max_Assistors.png', 9, 40, 137, 130)
        self.image('imagenes/Min_Assistors.png', 147, 40, 137, 130)

    def rebounders(self):

        # Añade una página que incluye una imagen con los máximos reboteadores
        # y otra con los mínimos

        self.add_page()
        self.colour_rect()
        self.image('imagenes/Max_Rebounders.png', 9, 40, 137, 130)
        self.image('imagenes/Min_Rebounders.png', 147, 40, 137, 130)

    def player_info(self):

        # Añade una página con una tabla de información sobre los jugadores

        self.add_page()
        self.colour_rect()
        self.image('imagenes/Celtics_Players_2023.png', 18, 35, 260, 130)

    def player_stats(self):

        # Añade una página con una tabla de estadísticas de los jugadores

        self.add_page()
        self.colour_rect()
        self.image('imagenes/Celtics_Players_Stats_2022.png', 18, 40, 260, 130)

    def stats_legend(self):

        # Añade una página con una leyenda para la tabla de la página anterior
        # y una imagen del mejor jugador del equipo en un partido

        self.add_page()
        self.colour_rect()
        self.image('imagenes/Legend.png', 22, 25, 128)
        self.image('imagenes/Jayson_Tatum.jpg', 175, 35, 80)


def crear_reporte_GM(equipo: str):

    # Crea el reporte ejecutivo en pdf (9 páginas incluyendo portada)

    executive_report = PDF(orientation='L', unit='mm', format='A4')
    executive_report.set_author('Miguel Ara Adánez')  # Autor del pdf
    executive_report.portada()
    executive_report.team_stats1()
    executive_report.team_stats2()
    executive_report.scorers()
    executive_report.assistors()
    executive_report.rebounders()
    executive_report.player_info()
    executive_report.player_stats()
    executive_report.stats_legend()
    executive_report.output(f'archivos_generados/{equipo}_GM_Report.pdf', 'F')
