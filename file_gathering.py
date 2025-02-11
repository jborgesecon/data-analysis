import navigation as nav
import time


years = list(range(2014, 2025))
months = list(range(1, 13))

for year in years:
    for month in months:
        if month < 10:
            y = str(str(year) + '0' + str(month))
        else:
            y = str(str(year) + str(month))
        
        nav.ptransp_download('ptransp_orcamento', nav.all_datasets['ptransp']['despesas'], 'despesas', y)

