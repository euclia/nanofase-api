import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
import os
from collections import OrderedDict
from openpyxl import load_workbook

color_air_water = ['palegreen', 'lightgreen', 'forestgreen', 'limegreen', 'aquamarine']
color_air = ['lightblue', 'dodgerblue']
color_water = ['palegreen', 'lightgreen', 'forestgreen', 'limegreen',
               'aquamarine', 'turquoise', 'lightseagreen', 'teal']
color_soil = ['bisque', 'turquoise', 'tan', 'darkgoldenrod', 'bisque', 'turquoise', 'tan', 'darkgoldenrod',
              'bisque', 'turquoise', 'tan', 'darkgoldenrod', 'bisque', 'turquoise', 'tan', 'darkgoldenrod']

class GenerateResult:

    def __init__(self):
        pass

    def store_output(self, chem_type, chem_name, region_name, release_scenario, release,
                     date_array, process_array, V_bulk_list, funC_df_list, funM_df_list):
        
        header = ['air', 'fw', 'fw_sed', 'sw', 'sw_sed', 'undeveloped_soil', 'deep_undeveloped_soil', 'urban_soil',
                           'deep_urban_soil', 'agricultural_soil', 'deep_agricultural_soil', 'biosolids_soil', 'deep_biosolids_soil'] # 13

        header_non_nano_sub = ['air', 'aerosol', 'fw', 'fw_sus_sed', 'fw_sed_water', 'fw_sed_solid', 'sw', 'sw_sus_sed',
                               'sw_sed_water', 'sw_sed_solid', 'undeveloped_soil_air', 'undeveloped_soil_water',
                               'undeveloped_soil_solid', 'deep_undeveloped_soil', 'urban_soil_air', 'urban_soil_water',
                               'urban_soil_solid', 'deep_urban_soil', 'agricultural_soil_air', 'agricultural_soil_water',
                               'agricultural_soil_solid', 'deep_agricultural_soil', 'biosolids_soil_air',
                               'biosolids_soil_water', 'biosolids_soil_solid', 'deep_biosolids_soil'] # 26

        results = []
        results.append(dict(zip(header, np.array(funC_df_list[0]).T)))
        results.append(dict(zip(header, np.array(funM_df_list[0]).T)))
        
        if chem_type != 'Nanomaterial':
            results.append(dict(zip(header_non_nano_sub, np.array(funC_df_list[1]).T)))
            results.append(dict(zip(header_non_nano_sub, np.array(funM_df_list[1]).T)))

       
        if chem_type == 'IonizableOrganic':
            results.append(dict(zip(header, np.array(funC_df_list[2]).T)))
            results.append(dict(zip(header_non_nano_sub, np.array(funC_df_list[3]).T)))
            results.append(dict(zip(header, np.array(funM_df_list[2]).T)))
            results.append(dict(zip(header_non_nano_sub, np.array(funM_df_list[3]).T)))
        
        else:
            metalNano = False
            if chem_type == 'Metal':
                metalNano = True
                index1, index2 = 2, 4
                txt1, txt2 = 'colloidal', 'dissolved'
            elif chem_type == 'Nanomaterial':
                metalNano = True
                index1, index2 = 1, 2
                txt1, txt2 = 'free nano', 'dissolved'

            if metalNano:
                results.append(dict(zip(header, np.array(funC_df_list[index1]).T)))
                results.append(dict(zip(header, np.array(funM_df_list[index1]).T)))
                results.append(dict(zip(header, np.array(funC_df_list[index2]).T)))
                results.append(dict(zip(header, np.array(funM_df_list[index2]).T)))
        
        return results