#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re               # import regex module
import os
import sys              # import handles errors probably other important stuff
import csv
import shutil
import logging
import urllib2
from codecs import open
from argparse import ArgumentParser, RawTextHelpFormatter
from win32api import LoadResource
from StringIO import StringIO


# processes cli arguments and usage guide
def process_cli(version):

    parser = ArgumentParser(
        prog='oui',
        description='''MAC address formatter and vendor lookup tool, supports multiple MAC addresses
    and formats the MAC address to multiple formats used in industries''',
        epilog='''Command line examples

    oui 00-11-22-33-44-55''',
        formatter_class = RawTextHelpFormatter)
    parser.add_argument('mac',
                        nargs='+',
                        help='MAC address to lookup')
    parser.add_argument('-u', '--update',
                        action="store_true",
                        help='Run update, grab up to date oui file, default = disabled')
    parser.add_argument('-d', '--debug',
                        action="store_true",
                        help='enable program flow debug')
    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s v'+version)

    # pass args into variable
    args = parser.parse_args()
    return args


def print_debug_arguments(args):
    """
    Prints out cli arguments in nice format when debugging is enabled
    """
    logger = logging.getLogger(__name__)
    counter_mac = 0
    logger.debug('')
    logger.debug('CLI Arguments, %s', args)
    for macs in args.mac:
        counter_mac += 1
        logger.debug('CLI Arguments, mac %s %s', counter_mac, macs)
    logger.debug('')


def configure_logging(args):
    """
    Creates logging configuration and sets logging level based on cli argument

    Args:
        args: all arguments parsed from cli

    Returns:
        logging: logging configuration
    """
    if args.debug:
        logging.basicConfig(stream=sys.stdout,
                            level=logging.DEBUG,
                            format='%(levelname)-8s - %(name)-10s - %(message)s')
        print_debug_arguments(args)
    else:
        logging.basicConfig(stream=sys.stdout,
                            level=logging.INFO,
                            format='%(message)s')
    return logging


class ScriptDetails():
    """
    Detects if frozen or not and defines path

    Returns:
       Frozen state as True or False
       Script execution path
    """
    def __init__(self):

        self.fronzen_state = hasattr(sys, "frozen")

        if self.fronzen_state:
            self.path_script = os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding( )))
            self.path_dl_file = os.path.join(self.path_script, 'oui_temp.csv')
            self.path_csv_file = os.path.join(self.path_script, 'oui.csv')
        else:
            self.path_script = os.path.dirname(unicode(__file__, sys.getfilesystemencoding( )))
            self.path_dl_file = os.path.join(self.path_script, 'data', 'oui_temp.csv')
            self.path_csv_file = os.path.join(self.path_script, 'data', 'oui.csv')

    def im_frozen(self):
        return self.fronzen_state

    def get_script_paths(self):
        return self.path_dl_file, self.path_csv_file


class UpdateOui():
    """
    downloads updated oui data in csv format
    """
    def __init__(self, oui_url, dl_file, csv_file):
        self._oui_url = oui_url
        self.dl_file = dl_file
        self.csv_file = csv_file

        self.dl_success = False
        self.move_success = False
        if self._download_update():
            self.dl_success = True
            if self._move_file():
                self.move_success = True

    def dl_was_successful(self):
        return self.dl_success

    def move_was_successful(self):
        return self.move_success

    def _download_update(self):
        req = urllib2.Request(self._oui_url)
        try:
            response = urllib2.urlopen(req)
        except urllib2.URLError as e:
            raise urllib2.URLError("URLError: Server returned %s" % e)
        except:
            raise
        else:
            data = response.read()
            with open(self.dl_file, 'wb') as f:
                 f.write(data)
            return True

    def _move_file(self):
        # if source does not exist
        if os.path.isfile(self.dl_file):
             try:
                 shutil.move(self.dl_file, self.csv_file)
             except (IOError, os.error) as why:
                 raise IOError(str(why))
             except:
                 raise
             else:
                 return True
        else:
            return False


class OuiResource():

    """ get contents of embedded or local oui.csv file """

    def __init__(self, csv_path):
        """
        Args:
            csv_path: path to csv file

        Returns:
            csv_resource: oui.csv in a variable
        """
        self.csv_path = csv_path

        if os.path.isfile(self.csv_path):
            with open(self.csv_path, 'rb') as f:
                self.csv_resource = f.read()
        else:
            self.csv_file = StringIO(LoadResource(0, u'ouicsv', 1))
            self.csv_resource = self.csv_file.getvalue()

    def get_resource(self):
        return self.csv_resource


class ProfileMAC:

    def __init__(self, mac, oui_resource):
        """
        validates and profiles mac addresses

        Args:
            mac: mac address to validate and profile
            fronzen_state: Frozen state as a True or False
            oui_resource: If frozen oui resource supplied by py2exe, otherwise its None

        Raises:
            ValueError: if validation fails
        """
        self._mac = mac
        self._oui_resource = oui_resource

        p = re.compile('[-\._:]', re.VERBOSE)
        self._cleaned_mac = p.sub(r'', self._mac)

        if not len(self._cleaned_mac) == 12:
            raise ValueError("%-20s Invalid length -" % self._mac)
        if not self._validate_mac():
            raise ValueError("%-20s Invalid characters -" % self._mac)

        self._cisco_mac = '.'.join(a+b+c+d for a,b,c,d in zip(self._cleaned_mac[::4], self._cleaned_mac[1::4], self._cleaned_mac[2::4], self._cleaned_mac[3::4]))
        self._windows_mac = '-'.join(a+b for a,b in zip(self._cleaned_mac[::2], self._cleaned_mac[1::2]))
        self._standard_mac = ':'.join(a+b for a,b in zip(self._cleaned_mac[::2], self._cleaned_mac[1::2]))
        self._iou_search_mac = self._cleaned_mac[:6]

        if self._read_csv() is not None:
            self._vendor = self._read_csv()
        else:
            self._vendor = 'Vendor Unknown'

    def cisco_mac(self):
        return self._cisco_mac.lower()

    def windows_mac(self):
        return self._windows_mac.upper()

    def standard_mac(self):
        return self._standard_mac.upper()

    def cleaned_mac(self):
        return self._cleaned_mac

    def iou_search_mac(self):
        return self._iou_search_mac

    def vendor(self):
        return self._vendor

    def _validate_mac(self):
        try:
            valid = re.search('^([0-9a-f]){12}$', self._cleaned_mac, re.M|re.I)
            valid.group(1)
            return True
        except:
            return False

    def _read_csv(self):
        vendor = None
        oui_reader = csv.reader(self._oui_resource.splitlines(), delimiter=',')
        for row in oui_reader:
            if self._iou_search_mac.lower() in row[1].lower():
                vendor = row[2]
                break
        # returns None if no vendor matching OUI is found
        return vendor


def print_header():
    """
    Prints column headers in preparations for results
    """
    logger = logging.getLogger(__name__)
    logger.info('')
    logger.info('|      Normal       |      Windows      |     Cisco      |     Vendor')
    logger.info('|-------------------|-------------------|----------------|-----------------------------------')


def move_file(src_file, dst_file):
    # going to need restore directory
    logger = logging.getLogger(__name__)

    # if source does not exist
    if os.path.isfile(src_file):
         try:
             shutil.move(src_file, dst_file)
             logger.info('')
             logger.info('Successfully updated %s', dst_file)
         except Exception as err:
             logger.error('')
             logger.error('Failed to update %s %s', dst_file, err)
    else:
        logger.error('')
        logger.error('Failed to update %s, can not find downloaded update %s', dst_file)


def main():

    from _version import __version__
    version=__version__

    # get cli arguments
    args = process_cli(version)
    logging = configure_logging(args)
    logger = logging.getLogger(__name__)

    p = ScriptDetails()
    path_dl_file, path_csv_file = p.get_script_paths()
    logger.debug('Update oui.csv path %s', path_dl_file)
    logger.debug('Local oui.csv path %s', path_csv_file)

    if args.update:
        oui_url = 'http://standards-oui.ieee.org/oui/oui.csv'
        #oui_url = 'https://standards.ieee.org/develop/regauth/oui/oui.csv'
        logger.info('')
        logger.debug('Downloading update from %s', oui_url)
        try:
            u = UpdateOui(oui_url, path_dl_file, path_csv_file)
        except urllib2.URLError as err:
            logger.error('Failed to update oui.csv, download failed')
            logger.error('%s', err[0])
        except IOError as err:
            logger.error('Failed to updated oui.csv, move file failed')
            logger.error('%s', err)
        except Exception as err:
            logger.error('Failed to update oui.csv')
            logger.error('Unknown error %s', err)
        else:
            if u.dl_was_successful():          
                logger.info('Update successful %s', path_csv_file)
            else:
                logger.info('Failed to update %s', path_csv_file)
        finally:
            if os.path.isfile(path_dl_file):
                os.remove(path_dl_file)
            
    logger.debug('Reading %s', path_csv_file)
    r = OuiResource(path_csv_file)
    oui_resource = r.get_resource()

    print_header()
    # cycle through domains
    for macs in args.mac:
        try:
            a = ProfileMAC(macs, oui_resource)
        except Exception, err:
            logger.error('%s Skipping', err)
            continue
        if args.debug:
            logger.debug('| %s | %s | %s | %s %s %s', a.standard_mac(), a.windows_mac(), a.cisco_mac(), a.vendor(), a.cleaned_mac(), a.iou_search_mac())
        else:
            logger.info('| %s | %s | %s | %s', a.standard_mac(), a.windows_mac(), a.cisco_mac(), a.vendor())


if __name__ == "__main__":
    main()