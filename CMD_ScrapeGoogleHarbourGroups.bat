rem To be used to setup all the packages

r:
cd \PythonPlayground
md \PythonPlayground\ScrapeGoogleHarbourGroups

call Setvenv ScrapeGoogleHarbourGroups
call pip3_ScrapeGoogleHarbourGroups

call pip3_list.bat

cd R:\PythonPlayground\ScrapeGoogleHarbourGroups
cmd
