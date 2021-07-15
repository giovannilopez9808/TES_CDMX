import numpy as np
import datetime
import os


class TES_algorithm:
    """
    Algoritmo que calcula los tiempos de exposicion solar para los seis tipos de fototipos.

    #### inputs

    + parameters -> diccionario que contiene las siguientes propiedades:
        + `hour initial` -> Hora inicial en la cual se calcularan los TES
        + `hour final` -> Hora final en   la cual se calcularan los TES
        + `hour limit` -> Hora limite para que los calculos no tiendan a infinito
        + `path data` -> Direccion donse se encuentran los datos
        + `Data folders` -> Carpetas donde se encuetran los datos (division de años)
        + `path results` -> Direccion donde se guardaran los archivos de resultados
    """

    def __init__(self, parameters={}):
        self.parameters = parameters
        self.define_datasets_for_terapy_types()
        self.define_total_time_in_minutes()
        self.define_cloud_factor_list()
        self.create_folder_results()

    def define_total_time_in_minutes(self):
        """
        Calcula el numero total de minutos entre las hora final e inicial y los adjunta a el diccionario self.parameters con el nombre ``Total minutes`` 
        """
        total_time = {"Total minutes": 60*(self.parameters["hour final"]-self.parameters["hour initial"]),
                      "Total hours": 60*(self.parameters["hour limit"]-self.parameters["hour initial"]), }
        self.parameters.update(total_time)

    def define_cloud_factor_list(self):
        """
        Definicion de los tipos de cielo despejado, para cada valor debera añadirse su nombre en el diccionacio self.cloud_conditions
        """
        cloud_factor = {"Cloud factor": {"Despejado": 1,
                                         "Medio nublado": 0.9,
                                         "Nublado": 0.6, }
                        }
        self.parameters.update(cloud_factor)

    def define_datasets_for_terapy_types(self):
        """
        Definicion de los MED que se calcularan conla base de datos. Para añadir más debera seguir el siguiente patrón:
        ```
        ``nombre`` : {"Dataset": tipo de datos que se usaran UVA o Ery,
                    "Doses": lista con las dosis,
                    "Filename init": nombre inicial del archivo de resultados,
                    "Filenames": lista de nombres para cada dosis,}
        """
        self.data_sets = {"Psoriasis": {"Dataset": "UVA",
                                        "Doses": [10000, 15000, 20000, 30000],
                                        "Filename init": "dosis",
                                        "Filenames": ["Pso1", "Pso1_5", "Pso2", "Pso3"], },
                          "MED": {"Dataset": "Ery",
                                  "Filename init": "Max",
                                  "Doses": [200, 250, 300, 450, 600, 1000],
                                  "Filenames": ["I", "II", "III", "IV", "V", "VI"], }
                          }

    def create_folder_results(self):
        """
        Creacion de la carpeta de resultados
        """
        mkdir(path=self.parameters["path results"])

    def init_system(self):
        """
        Inicializacion de las matrices de resultados
        """
        self.time = np.zeros([self.parameters["Total minutes"],
                              365,
                              2])
        self.hourly_mean = np.zeros([self.parameters["Total minutes"],
                                     2])
        self.monthly_mean = np.zeros([self.parameters["Total minutes"],
                                      12,
                                      2])

    def run(self):
        """
        Ejecución el algoritmo para calcular los TES
        """
        # Ciclo para variar en los data_sets
        for terapy_type in self.data_sets:
            print("Calculando TES para {}".format(terapy_type))
            data_set = self.data_sets[terapy_type]
            # Ciclo para variar en las condiciones de cielo
            for cloud_i, cloud in enumerate(self.parameters["Cloud factor"]):
                print("\tCondicion de cielo {}".format(cloud))
                cloud_value = self.parameters["Cloud factor"][cloud]
                # Ciclo para varias en las dosis de cada tipo de terapia
                for doses_i, doses_value in enumerate(data_set["Doses"]):
                    self.init_system()
                    # Ciclo para varias en las carpetas de datos
                    for path_folder in self.parameters["Data folders"]:
                        self.obtain_stations(path_folder)
                        # Ciclo para variar en las estaciones de monitoreo
                        for station in self.stations:
                            self.obtain_path_measurements(station)
                            self.obtain_dates_from_data()
                            for date in self.dates:
                                self.obtain_measurements_from_date(date,
                                                                   data_set)
                                self.obtain_date_from_name(date)
                                self.conse_day = date2consecutive_day(self.year,
                                                                      self.month,
                                                                      self.day)
                                self.calculate_TES(doses_value,
                                                   cloud_value,
                                                   self.data,
                                                   self.time)

                    self.obtain_mean_per_minute(self.time)
                    self.obtain_monthly_mean(self.time,
                                             self.monthly_mean)
                    self.obtain_hourly_mean(self.time,
                                            self.hourly_mean)
                    self.fill_data_from_lost_days(self.time,
                                                  self.monthly_mean,
                                                  self.hourly_mean)
                    self.write_results(data_set,
                                       doses_i,
                                       cloud_i,
                                       self.time)

    def obtain_stations(self, folder=""):
        """
        Obtiene la dirección y una lista con las estaciones de los datos por año
        """
        if folder == "2016":
            self.path_stations = "{}{}".format(self.parameters["path data"],
                                               folder)
            self.stations = [""]
        else:
            self.path_stations = "{}{}/Stations/".format(self.parameters["path data"],
                                                         folder)
            self.stations = os.listdir(self.path_stations)

    def obtain_path_measurements(self, station=""):
        """
        Obtiene la direccion de los parametros y las mediciones de cada estacion
        #### inputs
        + station -> nombre de la estación
        """
        self.path_parameters = "{}{}/".format(self.path_stations,
                                              station)
        self.path_measurements = "{}{}/ResultadosTUV/".format(self.path_stations,
                                                              station)

    def obtain_dates_from_data(self):
        """
        Obtiene las fechas que se usaran para calcular los TES a partir de la lista de parametros
        """
        self.dates = np.loadtxt("{}datos.txt".format(self.path_parameters),
                                skiprows=1,
                                usecols=0,
                                dtype=str)

    def obtain_measurements_from_date(self, date="", data_set={}):
        """
        Obtiene los datos de cada fecha
        """
        self.data = np.loadtxt("{}{}{}mo.txt".format(self.path_measurements,
                                                     date,
                                                     data_set["Dataset"]),
                               usecols=1,
                               skiprows=self.parameters["hour initial"]*60,
                               max_rows=self.parameters["Total hours"])

    def obtain_date_from_name(self, name=""):
        """
        Obtiene el año, mes y dia dependiendo del nombre del archivo en formato yymmdd
        """
        self.day = int(name[4:6])
        self.month = int(name[2:4])
        self.year = int(name[0:2])

    def calculate_TES(self, doses_value=250,  cloud_value=0.5, data=[], time=[]):
        """
        Calcula los TES para un dia completo dependiendo la dosis, la condicion de cielo y los datos
        """
        for hour in range(self.parameters["Total minutes"]):
            self.calculate_integral(doses_value,
                                    cloud_value,
                                    hour,
                                    data,
                                    time)

    def calculate_integral(self, doses_value=250, cloud_value=0.5, hour=10, data=[], time=[]):
        """
        Calcula los TES para una hora dependiendo la dosis, la condicion de cielo y los datos
        """
        doses = 0
        i = hour
        while doses < doses_value and i < self.parameters["Total hours"]-1:
            if data[i] != 0:
                doses += data[i]*60*cloud_value
            i += +1
        if doses != 0:
            if i < self.parameters["Total hours"]-1:
                min = i+1-hour
            else:
                min = self.parameters["Total hours"]-hour
            time[hour, self.conse_day,  0] += min
            time[hour, self.conse_day, 1] += 1

    def obtain_mean_per_minute(self, time=[]):
        """
        Obtiene el promedio de los TES para cada minuto y dia
        """
        for hour in range(self.parameters["Total minutes"]):
            for day in range(365):
                data_count = time[hour, day, 1]
                if data_count != 0:
                    data_sum = time[hour, day, 0]
                    time[hour, day, 0] = data_sum // data_count + 1

    def obtain_monthly_mean(self, time=[], month_mean=[]):
        """
        Obtiene el promedio mensual de los TES para cada minuto
        """
        for hour in range(self.parameters["Total minutes"]):
            for day in range(365):
                month = obtain_month_from_consecutive_day(day)
                time_day = time[hour, day,  0]
                if time_day != 0:
                    month_mean[hour, month,  0] += time_day
                    month_mean[hour, month,  1] += 1
            for month in range(12):
                data_sum = month_mean[hour, month, 0]
                data_count = month_mean[hour, month, 1]
                if data_count != 0:
                    month_mean[hour, month, 0] = data_sum//data_count+1

    def obtain_hourly_mean(self, time=[], hourly_time=[]):
        """
        obtiene el promedio por hora de los TES
        """
        for hour in range(self.parameters["Total minutes"]):
            for day in range(365):
                time_day = time[hour, day,  0]
                if time_day != 0:
                    hourly_time[hour,  0] += time_day
                    hourly_time[hour,  1] += 1
            data_count = hourly_time[hour,  1]
            data_sum = hourly_time[hour,  0]
            hourly_time[hour,  0] = data_sum//data_count+1

    def fill_data_from_lost_days(self,  time=[], month_mean=[], hourly_time=[]):
        """
        Asigna valores a los dias que no se calcularon los TES con el promedio mensual o horario
        """
        for hour in range(self.parameters["Total minutes"]):
            for day in range(365):
                if time[hour, day,  0] == 0:
                    month = obtain_month_from_consecutive_day(day)
                    if month_mean[hour, month,  0] != 0:
                        time[hour, day, 0] = month_mean[hour, month,  0]
                    else:
                        time[hour, day, 0] = hourly_time[hour,  0]

    def write_results(self, data_set={}, doses_i=1, cloud_i=0, time=[]):
        """
        Escritura de los archivos de resultados
        """
        init_name = data_set["Filename init"]
        terapy_name = data_set["Filenames"][doses_i]
        filename = "{}{}_{}_{}.csv".format(self.parameters["path results"],
                                           init_name,
                                           terapy_name,
                                           cloud_i)
        file = open(filename,
                    "w")
        file.write("Hour")
        for day in range(365):
            date = consecutive_day2date(day)
            header = self.mm_dd_format(date)
            file.write(","+header)
        file.write("\n")
        for hour in range(self.parameters["Total minutes"]):
            hour_index = self.hh_mm_format(hour)
            file.write(hour_index)
            for day in range(365):
                time_day_hour = time[hour, day, 0]
                file.write(",{:.2f}".format(time_day_hour))
            file.write("\n")
        file.close()

    def hh_mm_format(self, minute=59):
        """
        Formateo de la hora con los minutos: hh:mm
        """
        hour = self.parameters["hour initial"]+minute//60
        minute = minute-(minute//60)*60
        hour = self.header_file_format(hour)
        minute = self.header_file_format(minute)
        time = "{}:{}".format(hour,
                              minute)
        return time

    def mm_dd_format(self, date=datetime.date(2000, 12, 31)):
        """
        Formateo del dia y mes: mm:dd
        """
        month = self.header_file_format(date.month)
        day = self.header_file_format(date.day)
        date = "{}-{}".format(month,
                              day)
        return date

    def header_file_format(self, number=5):
        """
        Formateo del caracter a dos strings
        """
        number = str(number).zfill(2)
        return number


def date2consecutive_day(year=2000, month=12, day=31):
    """
    Funcion para obtener el dia consecutivo a partir de una fecha
    """
    num = (datetime.date(year, month, day)-datetime.date(year, 1, 1)).days
    if num > 364:
        num = num-1
    return num


def obtain_month_from_consecutive_day(day=100):
    """
    Funcion para obtener el numero de mes de una fecha en dias consecutivos
    """
    date = consecutive_day2date(day)
    month = date.month-1
    return month


def consecutive_day2date(day=100):
    """
    Funcion para obtener la fecha a partir del dia consecutivo
    """
    date = datetime.date(2019, 1, 1)+datetime.timedelta(day)
    return date


def mkdir(path="", name=""):
    try:
        os.mkdir("{}{}".format(path,
                               name))
    except FileExistsError:
        pass
