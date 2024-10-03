import requests
import urllib
import os
import pandas as pd
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.request import urlopen, urlretrieve
import logging
import os

log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
'''
Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
'''
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{log_directory}/script_log.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def requests_retry_session(retries=3, backoff_factor=0.2, status_forcelist=(500, 502, 504), session=None):
    """
        This function is create a session with retry logic and notifies user of any errors.

        Parameters
        ----------
        retries : int, optional, default retry set to 3
            this is the number of retries program will perform before quitting
        backoff_factor : float, optional, default set to 0.2
            this is based on backoff algorithm to hit the web resource to avoid multiple retries in same time
        status_forecelist : Collection[int], optional, default to 5XX errors
            this is to set any error code which need to be force retried
        session : session object from requests API, optional, default to None
            if no session is provided, a new reqeusts session object will be created to check the header response

        Returns
        -------
        session : requests session object
            this will be used to check the header of the file or to check any error
    """
    session = session or requests.Session()
    retry = Retry(total=retries, read=retries, connect=retries, backoff_factor=backoff_factor, 
                  status_forcelist=status_forcelist, raise_on_status=False)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

# Path to a local file where you store the last modified timestamp
last_modified_file = 'last_modified.txt'

def get_last_modified(url):
    """
    This function checks if the contents have been modified on the provided url

    Parameters
    ----------
    url : str, required
        this string object is the url of the website which needs to be monitored
    
    Returns
    -------
    response header: requests api response header object
        this is required to check for any changes in the webpage
    """
    try:
        response = requests_retry_session().get(url, timeout=3)
        response.raise_for_status()
        # response = requests.head(url)
        if 'Last-Modified' in response.headers:
            return response.headers['Last-Modified']
        else:
            logger.info("No 'Last-Modified' header found for this file.")
            return None
    except requests.RequestException as e:
        logger.error(f"Error checking the file: {e}")
        return None

def save_last_modified(last_modified):
    """
    this function saves the contents of last modified to text file

    Parameters
    ----------
    last_modified : string
        this is the string object which stores the content of the last modified header
    """
    with open(last_modified_file, 'w') as file:
        file.write(last_modified)


def has_file_changed(url, last_modified_file):
    """
    this function checks if the file has been changed on the web resource

    Parameters
    ----------
    last_modified_file : file
        this is the txt file which stores the content of the last modified header
    
    Returns
    -------
    bool : True/False
        notifies the program whether file has been changed or not in boolean
    """
    last_modified_online = get_last_modified(url)
    if not last_modified_online:
        return False

    if os.path.exists(last_modified_file):
        with open(last_modified_file, 'r') as file:
            last_modified_local = file.read().strip()

        if last_modified_local == last_modified_online:
            logger.info("File has not changed.")
            return False
        else:
            logger.info("File has changed.")
            save_last_modified(last_modified_local)
            return True
    else:
        logger.info("No local record of 'Last-Modified'. Hitting the url for first time.")
        return True

def download_file(url):
    """
    this function downloads the excel file from the web url requested and saves to local disk

    Parameters
    ----------
    url : str
        this string object is the url of the website which needs to be scraped
    
    Returns
    -------
    Saves the file to local disk
    """
    u = urlopen(url)
    try:
        html_content = u.read().decode('utf-8')
    finally:
        u.close()

    soup = BeautifulSoup(html_content, "html.parser")
    for link in soup.find_all('a', href=True):
        if 'ET_3.1_SEP_24.xlsx' in link.get('href'):
            file = link.get('href')
            break

    filename = os.path.join('', file.split('/', 5)[-1])
    print(filename)
    logger.info(f"Downloading {file} to {filename}")
    urlretrieve(file, filename)
    logger.info("File Download Complete!\n")

def transform_quarterly_data(local_xls_file_name, dataframe_cols, output_dir='cleaned_quarter_data'):
    """
    this function transforms the excel file which contains quarter data using pandas dataframe and after cleaning, writes the dataframe
    back to a csv file to the directory location specified by user while running the program

    Parameters
    ----------
    local_xls_file_name : file
        this file contains the quarter data in a excel worksheet
    output_dir : str
        location of the output directory where the csv needs to be saved
    dataframe_cols : Collection(str)
        list of dataframe columns which needs to be passed onto the transposed dataframe after cleanup
    Returns
    -------
    Saves the dataframe in csv format in the output directory provided by user
    """
    df_quarter = pd.read_excel(local_xls_file_name, sheet_name='Quarter', skiprows=4)

    df_quarter_transposed = df_quarter.transpose()
    df_quarter_transposed.index = df_quarter_transposed.index.set_names('Quarter')
    df_quarter_transposed.columns = dataframe_cols
    df_quarter_transposed = df_quarter_transposed.reset_index()
    df_quarter_transposed = df_quarter_transposed[1:]
    df_quarter_transposed['Quarter'] = df_quarter_transposed['Quarter'].apply(lambda x: x.replace(' ', ''))
    replacements = {'\n1stquarter': '-Q1', '\n2ndquarter': '-Q2', '\n3rdquarter': '-Q3', '\n3ndquarter': '-Q3', 
                    '\n4thquarter': '-Q4', '/[provisional]/': ''}
    df_quarter_transposed = df_quarter_transposed.apply(lambda x: x.replace(replacements, regex=True))
    df_quarter_transposed['date'] = pd.to_datetime(df_quarter_transposed['Quarter'].str.replace(r'(Q\d) (\d+)', r'\2-\1'),
                                                   errors='coerce')
    df_quarter_transposed = df_quarter_transposed.fillna('')

    dataframe_cols.append('Quarter')
    dataframe_cols.append('date')
    try:
        if set(df_quarter_transposed.columns.values.tolist()) != set(dataframe_cols):
            logger.info(set(dataframe_cols))
            logger.info(set(df_quarter_transposed.columns.values.tolist()))
            logger.info('Columns do not match. Exit the program and check the input file')
        else:
            #save to CSV
            try:
                if not os.path.exists(output_dir):
                    os.mkdir(output_dir)
                absolute_file_name = os.path.join(output_dir, 'quarter.csv')
                df_quarter_transposed.to_csv(absolute_file_name)
                return df_quarter_transposed
            except Exception as E:
                logger.error(f"An error occurred while saving the data to csv\n {E}")
    except Exception as ColumnErr:
        logger.error(f"Error checking the file: Colum Mismatch {ColumnErr}")

    