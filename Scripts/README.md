# Scripts

- `Class_list`:

  Contiene la lógica del calculo de los TES haciendo uso de los diccionarios dentro de las funciones de la clase `TES_algorithm`. Para añadir una nueva terapia se tiene que añadir en la función `define_datasets_for_terapy_types` con el siguiente formato:

  ```python
  nombre: {"Dataset": tipo de datos que se usaran UVA o Ery,
           "Doses": lista con las dosis,
           "Filename init": nombre inicial del archivo de resultados,
           "Filenames": lista de nombres para cada dosis,}
  ```

- `Tes.py`:

  Inicia el calculo de los TES haciendo uso de el algoritmo dentro de `TES_algorithm` con los siguientes parametros:

  ```python
  parameters = {"hour initial":,
              "hour final": ,
              "hour limit": ,
              "path data": "",
              "Data folders": ["",""],
              "path results": "",
              }
  ```
