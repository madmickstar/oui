OUI
==
`oui` is an easy to use MAC address vendor lookup tool.

I regularly have to go to the internet to lookup MAC address vendor details. `oui` will lookup the 
vendor of a MAC address from the convenience of a CLI one liner. `oui` has the ability to lookup multiple 
MAC address simultaneously and present the MAC address in mutiple common formats.


OUI features
---------------

* Resolves multiple inputs simultaneously in one convenient CLI command
* Returns vendor name per MAC address
* Returns MAC address in the following formats
    * Standard  00:11:22:33:44:55
    * Windows   00-11-22-33-44-55
    * Cisco     0011.2233.4455
* Update application's OUI vendor details
* Py2exe setup script provided with source code


Create Win32 EXE from source using py2exe
-----------------------------------------
1. Install python dependencies for oui program
2. Change into source dir 
3. Create exe file using supplied py2exe script.
   See [py2exe website for tutorial](http://www.py2exe.org/index.cgi/Tutorial)
4. Copy dist\oui.exe to location in window's system path


```
pip install -r requirements.txt
cd oui
python setup_oui_py2exe.py py2exe
cp dist\oui.exe <windows\system\path>
```


Usage
-----
`
 oui {mac address} [ -u | -h | -d | --version ]
`

Argument  | Type   | Format               | Default           | Description
----------|--------|----------------------|-------------------|--------------------
mac address | string | {mac address} | No default value | mac address to format and return vendor name
-u | switch | -u | disabled | Update applications OUI vendor details
-h | switch | -h | disabled | Prints help to console   
-d | switch | -d | disabled | Enables debug output to console
--version | switch | --version | disabled | Displays version


Examples
--------
Lookup 3 MAC addresses
```
oui 00:11:22:33:44:55 112233445566 22-33-44-55-66-77
```

Lookup 3 MAC addresses and update application OUI vendor details
```
oui 00:11:22:33:44:55 112233445566 22-33-44-55-66-77 -u
```