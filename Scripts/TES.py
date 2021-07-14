from Class_list import *
parameters = {"hour initial": 8,
              "hour final": 18,
              "hour limit": 21,
              "path data": "../Data/",
              "Data folders": ["2016", "2017-2018"],
              "path results": "../Data/TES/",
              }
TES = TES_algorithm(parameters=parameters)
TES.run()
