# NBA_Celtics_Report
### Summary
Obtaining data from a sports API to generate a pdf report with NBA team Boston Celtic's advanced stats as charts and
tables for Brad Stevens (Boston Celtic´s GM). Additionally, predicting the result for the following Celtic's match
based on betting house odds using webscraping

### Previous requirements

Once you have cloned the git repo on your computer, for the program to work correctly, some non-default libraries need
to be installed before executing the main .py program _ETL_Celtics.py_. All these indispensable libraries are included
in a _requirements.txt_ file, specifying the versions.

Before downloading these libraries you need to check the version of Google Chrome on your computer (open Google Chrome >
Menu > Help > About Google Chrome). Then you need to go to this web https://chromedriver.chromium.org/downloads and download
a zip file containing the Chrome Driver according to your version of Google Chrome and your operating system. Once you have
decompressed the zip file, you´ll need to remember the path of the file chromedriver.exe in your computer.

Now you can download all the libraries by running the following command in your terminal.
```
pip install -r requirements .txt
```
Moreover, you also need to edit the other txt file, _config.txt_, including your API key and the path of the executable file you have
just downloaded (chromedriver.exe). To obtain the API key you need to create an account in the web https://sportsdata.io/ and
suscribe to the NBA-API. The API key will be sent to you by email or you´ll be able to find it in here https://sportsdata.io/developers/api-documentation/nba
The _config.txt_ file must be edited and left with this format:
```
{
    'api-key': '<your_api_key>',
    'path': '<the_path_of_the_chromedriver.exe_file_on_your_computer>'
}
```
You are now ready to proceed

### Files
A brief explanation of the three .py files in this git repo will be done in the following paragraphs

#### ETL_Celtics.py
__This is the only file that must be runned for the report and the prediction to be created.__ The two other .py files
only contain functions and are used as libraries (if you try to run them nothing will happen), which are imported in the
beginning of _ETL_Celtics.py_. This file uses an ETL to extract the data from the API with three get requests using your API key,
transform and filter the data using pandas dataframes, and then load the resulting information in 4 csv files which are saved
in the directory _archivos_generados_, and in 16 images including charts and tables which are saved in the directory _imagenes_
Now the program calls the function _crear_reporte_GM()_ from the library _Crear_pdf.py_ to generate the pdf report and save it in the
directory _archivos generados_, and the function _pronostica()_ from the library _Pronosticador.py_ to predict the result of the
following match for the Boston Celtics 

#### Crear_pdf.py
This file uses fpdf library to generate a pdf executive report for Brad Stevens (Boston Celtic´s GM) including charts and tables
with all te stats obtained from the API that have been saved as images in the directory _imagenes_. The _crear_report_GM()_ is the only
callable function in this library, which is called in _ETL_Celtics.py_ after generating the images

#### Pronosticador.py
This file uses selenium library to do webscraping of this web https://www.sportytrader.es/ to obtain the betting odds for the next NBA
games. The function _pronostica()_ creates a webdriver and searches for the odds in the web for the next Boston Celtics match. It also
gives you a chance to predict the result of the next match for any other team that you wish. This function is called in _ETL_Celtics.py_
and with that, our program comes to an end

