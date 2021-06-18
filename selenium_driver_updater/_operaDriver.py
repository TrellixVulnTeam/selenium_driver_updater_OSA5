import shutil
import subprocess
import wget
import os
import traceback
import logging
import time
import os
from selenium.common.exceptions import SessionNotCreatedException
from selenium.common.exceptions import WebDriverException

from typing import Tuple

import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from _setting import setting

import platform

import stat

from shutil import copyfile

from util.extractor import Extractor
from util.github_viewer import GithubViewer
from util.requests_getter import RequestsGetter
from browsers._operaBrowser import OperaBrowser

import pathlib

import re

from typing import Any

class OperaDriver():

    _repo_name = 'operasoftware/operachromiumdriver'
    
    def __init__(self, path : str, **kwargs):
        """Class for working with Selenium operadriver binary

        Args:
            path (str)                          : Specified path which will used for downloading or updating Selenium operadriver binary. Must be folder path.
            upgrade (bool)                      : If true, it will overwrite existing driver in the folder. Defaults to False.
            chmod (bool)                        : If true, it will make operadriver binary executable. Defaults to True.
            check_driver_is_up_to_date (bool)   : If true, it will check driver version before and after upgrade. Defaults to False.
            filename (str)                      : Specific name for operadriver. If given, it will replace name for operadriver. Defaults to empty string.
            version (str)                       : Specific version for operadriver. If given, it will downloads given version. Defaults to empty string.
            check_browser_is_up_to_date (bool)  : If true, it will check opera browser version before operadriver update/upgrade.
            system_name (Union[str, list[str]]) : Specific OS for driver. Defaults to empty string.
        """
        self.setting : Any = setting

        self.path : str = path
                    
        self.upgrade : bool = bool(kwargs.get('upgrade'))

        self.chmod : bool = bool(kwargs.get('chmod'))

        self.check_driver_is_up_to_date : bool = bool(kwargs.get('check_driver_is_up_to_date'))

        specific_system = str(kwargs.get('system_name'))
        self.system_name = "operadriver_win64.zip" if specific_system == 'windows' or specific_system == 'windows64' else\
                           "operadriver_win32.zip" if specific_system == 'windows32' else\
                           "operadriver_linux64.zip" if specific_system == 'linux' or specific_system == 'linux64' else\
                           "operadriver_mac64.zip" if specific_system == 'macos' else\
                           logging.error(f"You specified system_name: {specific_system} which unsupported by operadriver - so used default instead.")\
                           if specific_system else ''

        self.specific_driver_name = ''

        if not self.system_name:
        
            specific_filename = str(kwargs.get('filename'))
            self.filename = f"{specific_filename}.exe" if platform.system() == 'Windows' and specific_filename else\
                            specific_filename

            self.operadriver_path : str =  self.path + self.setting['OperaDriver']['LastReleasePlatform'] if not specific_filename else self.path + self.filename

        else:

            specific_filename = str(kwargs.get('filename'))
            self.filename = f"{specific_filename}.exe" if 'windows' in specific_system and specific_filename else\
                            specific_filename
                        
            self.specific_driver_name =    "operadriver.exe" if 'windows' in specific_system else\
                                            "operadriver"
                                    
            self.operadriver_path : str =  self.path + self.specific_driver_name if not specific_filename else self.path + self.filename

        self.version = str(kwargs.get('version'))

        self.check_browser_is_up_to_date = bool(kwargs.get('check_browser_is_up_to_date'))

        self.info_messages = bool(kwargs.get('info_messages'))

        self.extractor = Extractor
        self.github_viewer = GithubViewer
        self.requests_getter = RequestsGetter
        self.operabrowser = OperaBrowser(path=self.path, check_browser_is_up_to_date=self.check_browser_is_up_to_date)

    def main(self) -> Tuple[bool, str, str]:
        """Main function, checks for the latest version, downloads or updates operadriver binary or
        downloads specific version of operadriver.

        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            driver_path (str)       : Path where operadriver was downloaded or updated.
            
        Raises:
            Except: If unexpected error raised. 

        """
        result_run : bool = False
        message_run : str = ''
        driver_path : str = ''
        
        try:

            result, message = self.operabrowser.main()
            if not result:
                logging.error(message)
                return result, message, driver_path

            if not self.version:

                result, message, driver_path = self.__check_if_operadriver_is_up_to_date()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            else:

                result, message, driver_path = self.__download_driver(version=self.version)
                if not result:
                    logging.error(message)
                    return result, message, driver_path

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, driver_path

    def __get_current_version_operadriver(self) -> Tuple[bool, str, str]:
        """Gets current operadriver version via command in terminal


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            driver_version (str)    : Current operadriver version.

        Raises:
            SessionNotCreatedException: Occurs when current edgedriver could not start.

            WebDriverException: Occurs when current edgedriver could not start or critical error occured

            OSError: Occurs when chromedriver made for another CPU type

            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        driver_version : str = ''
        driver_version_terminal : str = ''
        
        try:
            
            if os.path.exists(self.operadriver_path):
            
                process = subprocess.Popen([self.operadriver_path, '--version'], stdout=subprocess.PIPE)
        
                driver_version_terminal = process.communicate()[0].decode('UTF-8')
                
                find_string = re.findall(self.setting["Program"]["wedriverVersionPattern"], driver_version_terminal)
                driver_version = find_string[0] if len(find_string) > 0 else ''

                logging.info(f'Current version of operadriver: {driver_version}')

            result_run = True

        except SessionNotCreatedException:
            message_run = f'SessionNotCreatedException error: {traceback.format_exc()}'
            logging.error(message_run)
            return True, message_run, driver_version

        except WebDriverException:
            message_run = f'WebDriverException error: {traceback.format_exc()}'
            logging.error(message_run)
            return True, message_run, driver_version

        except OSError:
            message_run = f'OSError error: {traceback.format_exc()}' #probably [Errno 86] Bad CPU type in executable:
            logging.error(message_run)
            return True, message_run, driver_version

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)
        
        return result_run, message_run, driver_version

    def __get_latest_version_operadriver(self) -> Tuple[bool, str, str]:
        """Gets latest operadriver version


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            latest_version (str)    : Latest version of operadriver
            
        Raises:
            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        latest_version : str = ''

        try:
            
            repo_name = OperaDriver._repo_name
            result, message, json_data = self.github_viewer.get_latest_release_data_by_repo_name(repo_name=repo_name)
            if not result:
                return result, message, latest_version

            latest_version = json_data.get('name')

            logging.info(f'Latest version of operadriver: {latest_version}')

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run , latest_version

    def __delete_current_operadriver_for_current_os(self) -> Tuple[bool, str]:
        """Deletes operadriver from specific folder


        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            
        Raises:
            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''

        try:

            if os.path.exists(self.operadriver_path):
                logging.info(f'Deleted existing operadriver operadriver_path: {self.operadriver_path}')
                file_to_rem = pathlib.Path(self.operadriver_path)
                file_to_rem.unlink()
            

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run
    
    def __check_if_operadriver_is_up_to_date(self) -> Tuple[bool, str, str]:
        """Main function, checks for the latest version, downloads or updates operadriver binary

        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            driver_path (str)       : Path where operadriver was downloaded or updated.
            
        Raises:
            Except: If unexpected error raised. 

        """
        result_run : bool = False
        message_run : str = ''
        driver_path : str = ''
        
        try:

            if self.check_driver_is_up_to_date and not self.system_name:

                result, message, is_driver_up_to_date, current_version, latest_version = self.__compare_current_version_and_latest_version()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

                if is_driver_up_to_date:
                    return True, message, self.operadriver_path

            result, message, driver_path = self.__download_driver()
            if not result:
                logging.error(message)
                return result, message, driver_path

            if self.check_driver_is_up_to_date and not self.system_name:

                result, message, is_driver_up_to_date, current_version, latest_version = self.__compare_current_version_and_latest_version()
                if not result:
                    logging.error(message)
                    return result, message, driver_path

                if not is_driver_up_to_date:
                    message = f'Problem with updating operadriver current_version: {current_version} latest_version: {latest_version}'
                    logging.error(message)
                    message = 'Trying to download previous latest version of operadriver'
                    logging.info(message)

                    result, message, driver_path = self.__download_driver(previous_version=True)
                    if not result:
                        logging.error(message)
                        return result, message, driver_path

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, driver_path

    def __compare_current_version_and_latest_version(self) -> Tuple[bool, str, bool, str, str]:
        """Compares current version of operadriver to latest version

        Returns:
            Tuple of bool, str and bool

            result_run (bool)           : True if function passed correctly, False otherwise.
            message_run (str)           : Empty string if function passed correctly, non-empty string if error.
            is_driver_up_to_date (bool) : If true current version of operadriver is up to date. Defaults to False.
            
        Raises:
            Except: If unexpected error raised. 

        """
        result_run : bool = False
        message_run : str = ''
        is_driver_up_to_date : bool = False
        current_version : str = ''
        latest_version : str = ''
        
        try:

            result, message, current_version = self.__get_current_version_operadriver()
            if not result:
                logging.error(message)
                return result, message, is_driver_up_to_date, current_version, latest_version

            if not current_version:
                return True, message_run, is_driver_up_to_date, current_version, latest_version

            result, message, latest_version = self.__get_latest_version_operadriver()
            if not result:
                logging.error(message)
                return result, message, is_driver_up_to_date, current_version, latest_version

            if current_version == latest_version:
                is_driver_up_to_date = True
                message = f'Your existing operadriver is up to date. current_version: {current_version} latest_version: {latest_version}' 
                logging.info(message)

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, is_driver_up_to_date, current_version, latest_version

    def __rename_driver(self, archive_folder_path : str, archive_operadriver_path : str) -> Tuple[bool, str]:
        """Renames operadriver if it was given

        Args:
            archive_folder_path (str)       : Path to the main folder
            archive_operadriver_path (str)  : Path to the operadriver archive

        Returns:
            Tuple of bool, str and bool

            result_run (bool)           : True if function passed correctly, False otherwise.
            message_run (str)           : Empty string if function passed correctly, non-empty string if error.
            
        Raises:
            Except: If unexpected error raised. 

        """
        result_run : bool = False
        message_run : str = ''
        renamed_driver_path : str = ''
        
        try:

            new_path = archive_folder_path + os.path.sep + self.filename

            if os.path.exists(new_path):
                os.remove(new_path)

            os.rename(archive_operadriver_path, new_path)
            
            renamed_driver_path = self.path + self.filename
            if os.path.exists(renamed_driver_path):
                os.remove(renamed_driver_path)

            copyfile(new_path, renamed_driver_path)

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run

    def __chmod_driver(self) -> Tuple[bool, str]:
        """Tries to give operadriver needed permissions

        Returns:
            Tuple of bool and str

            result_run (bool)           : True if function passed correctly, False otherwise.
            message_run (str)           : Empty string if function passed correctly, non-empty string if error.
            
        Raises:
            Except: If unexpected error raised. 

        """
        result_run : bool = False
        message_run : str = ''
        
        try:

            if os.path.exists(self.operadriver_path):

                logging.info('Trying to give operadriver needed permissions')

                st = os.stat(self.operadriver_path)
                os.chmod(self.operadriver_path, st.st_mode | stat.S_IEXEC)

                logging.info('Needed rights for operadriver were successfully issued')

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run
    
    def __get_latest_previous_version_operadriver_via_requests(self) -> Tuple[bool, str, str]:
        """Gets previous latest operadriver version


        Returns:
            Tuple of bool, str and str

            result_run (bool)               : True if function passed correctly, False otherwise.
            message_run (str)               : Empty string if function passed correctly, non-empty string if error.
            latest_version_previous (str)   : Latest previous version of operadriver.
            
        Raises:
            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        latest_previous_version : str = ''

        try:

            repo_name = OperaDriver._repo_name
            result, message, json_data = self.github_viewer.get_all_releases_data_by_repo_name(repo_name=repo_name)
            if not result:
                return result, message, latest_previous_version

            latest_previous_version = json_data[1].get('name')

            logging.info(f'Latest previous version of operadriver: {latest_previous_version}')

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run , latest_previous_version

    def __check_if_version_is_valid(self, url : str, version_url : str) -> Tuple[bool, str]:
        """Checks the specified version for existence.

        Args:
            url (str)           : Full download url of operadriver.
            version_url (str)   : Version that will be downloaded.

        Returns:
            Tuple of bool and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
        """
        result_run : bool = False
        message_run : str = ''
        archive_name : str = url.split("/")[len(url.split("/"))-1]
        is_found : bool = False

        try:

            result, message, json_data = self.github_viewer.get_all_releases_data_by_repo_name(OperaDriver._repo_name)
            if not result:
                logging.error(message)
                return result, message

            for data in json_data:
                if data.get('tag_name') == version_url or data.get('name') == version_url:
                    for asset in data.get('assets'):
                        if asset.get('name') == archive_name:
                            is_found = True
                            break

            if not is_found:
                message = f'Wrong version or system_name was specified. version_url: {version_url} url: {url}'
                logging.error(message)
                return False, message

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)
        
        return result_run, message_run

    def __download_driver(self, version : str = '', previous_version : bool = False) -> Tuple[bool, str, str]:
        """Function to download, delete or upgrade current operadriver

        Args:
            version (str)               : Specific operadriver version to download. Defaults to empty string.
            previous_version (boll)     : If true, operadriver latest previous version will be downloaded. Defaults to False.

        Returns:
            Tuple of bool, str and str

            result_run (bool)       : True if function passed correctly, False otherwise.
            message_run (str)       : Empty string if function passed correctly, non-empty string if error.
            file_name (str)         : Path to unzipped driver.
            
        Raises:
            Except: If unexpected error raised. 

        """

        result_run : bool = False
        message_run : str = ''
        file_name : str = ''
        url : str = ''
        latest_version : str = ''
        latest_previous_version : str = ''

        try:

            if self.upgrade:

                result, message = self.__delete_current_operadriver_for_current_os()
                if not result:
                    logging.error(message)
                    return result, message, file_name

            if version:

                url = self.setting["OperaDriver"]["LinkLastReleasePlatform"].format(version, version)

                logging.info(f'Started download operadriver specific_version: {version}')

            elif previous_version:

                result, message, latest_previous_version = self.__get_latest_previous_version_operadriver_via_requests()
                if not result:
                    logging.error(message)
                    return result, message, file_name

                url = self.setting["OperaDriver"]["LinkLastReleasePlatform"].format(latest_previous_version, latest_previous_version)

                logging.info(f'Started download operadriver latest_previous_version: {latest_previous_version}')

            else:

                result, message, latest_version = self.__get_latest_version_operadriver()
                if not result:
                    logging.error(message)
                    return result, message, file_name

                url = self.setting["OperaDriver"]["LinkLastReleasePlatform"].format(latest_version, latest_version)

                logging.info(f'Started download operadriver latest_version: {latest_version}')

            if self.system_name:
                url = url.replace(url.split("/")[len(url.split("/"))-1], '')
                url = url + self.system_name

                logging.info(f'Started downloading chromedriver for specific system: {self.system_name}')

            if any([version, self.system_name ,latest_previous_version]):
                version_url = version if version else latest_previous_version if latest_previous_version else latest_version
                result, message = self.__check_if_version_is_valid(url=url, version_url=version_url)
                if not result:
                    logging.error(message)
                    return result, message, file_name

            archive_name = url.split("/")[len(url.split("/"))-1]
            out_path = self.path + archive_name

            if os.path.exists(out_path):
                os.remove(out_path)

            logging.info(f'Started download operadriver by url: {url}')

            if self.info_messages:
                file_name = wget.download(url=url, out=out_path)
            else:
                file_name = wget.download(url=url, out=out_path, bar=None)

            logging.info(f'Operadriver was downloaded to path: {file_name}')

            time.sleep(2)

            archive_path = file_name
            out_path = self.path
            result, message = self.extractor.extract_all_zip_archive(archive_path=archive_path, out_path=out_path)
            if not result:
                logging.error(message)
                return result, message, file_name

            platform : str = self.setting['OperaDriver']['LastReleasePlatform'] if not self.specific_driver_name else self.specific_driver_name
            archive_folder_name = self.setting["OperaDriver"]["NamePlatformRelease"] if not self.system_name else self.system_name.replace(".zip", '')

            archive_folder_path = self.path + archive_folder_name
            archive_operadriver_path = archive_folder_path + os.path.sep + platform

            if not self.filename:
                
                copyfile(archive_operadriver_path, self.path + platform)

            else:

                result, message = self.__rename_driver(archive_folder_path=archive_folder_path,
                                                        archive_operadriver_path=archive_operadriver_path)
                if not result:
                    return result, message, file_name

            if os.path.exists(file_name):
                os.remove(file_name)

            if os.path.exists(archive_folder_path):
                shutil.rmtree(archive_folder_path)
            
            file_name = self.operadriver_path

            logging.info(f'Operadriver was successfully unpacked by path: {file_name}')

            if self.chmod:

                result, message = self.__chmod_driver()
                if not result:
                    return result, message, file_name

            result_run = True

        except:
            message_run = f'Unexcepted error: {traceback.format_exc()}'
            logging.error(message_run)

        return result_run, message_run, file_name