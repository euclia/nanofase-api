#!/usr/bin/env python
import xlrd
import collections
from collections import OrderedDict
from datetime import datetime, timedelta
import numpy as np
from utils.advective_processes_nano import lsFactor

#################################################################
#
#   CLiCC Nanomaterials F&T Model Developed by Dr. Garner
#	Model original devloped in MATLAB
#   Date: August 16th, 2016
#   Converted to Python by Dillon Elsbury
#   Updated by Dr. Garner on July 26, 2017
#
#################################################################


def load_bgConc(bgConc, presence):
    
    # convert to units of ug/m3
    ## always converts units so need to make sure that inputs are always kg
    bgValues = bgConc

    for key, value in bgValues.items():
        # unit conversion from kg/m^3 to mol/m^3
        # kg/m3 / kg/mol = mol/m3
        bgValues[key] = value * 10 ** 9

    bgValues = OrderedDict(bgValues)

    if presence['air'] == 0:
        bgValues['air'] = 0
        bgValues['aer'] = 0
        bgValues['gairc_n'] = 0
    if presence['fw'] == 0:
        bgValues['fw'] = 0
        bgValues['fSS'] = 0
        bgValues['fSedS'] = 0
        bgValues['fwdis'] = 0
        bgValues['fwSeddis'] = 0
    if presence['sw'] == 0:
        bgValues['sw'] = 0
        bgValues['sSS'] = 0
        bgValues['sSedS'] = 0
        bgValues['swdis'] = 0
        bgValues['swSeddis'] = 0
    if presence['soil1'] == 0:
        bgValues['soilS1'] = 0
        bgValues['soilW1'] = 0
        bgValues['dsoil1'] = 0
        bgValues['soilW1dis'] = 0
    if presence['soil2'] == 0:
        bgValues['soilS2'] = 0
        bgValues['soilW2'] = 0
        bgValues['dsoil2'] = 0
        bgValues['soilW2dis'] = 0
    if presence['soil3'] == 0:
        bgValues['soilS3'] = 0
        bgValues['soilW3'] = 0
        bgValues['dsoil3'] = 0
        bgValues['soilW3dis'] = 0
    if presence['soil4'] == 0:
        bgValues['soilS4'] = 0
        bgValues['soilW4'] = 0
        bgValues['dsoil4'] = 0
        bgValues['soilW4dis'] = 0

    bgConc = collections.OrderedDict()
    bgConc['A'] = bgValues['air']
    bgConc['Aer'] = bgValues['aer']
    bgConc['fW'] = bgValues['fw']
    bgConc['fSS'] = bgValues['fSS']
    bgConc['fwSed'] = bgValues['fSedS']
    bgConc['sW'] = bgValues['sw']
    bgConc['sSS'] = bgValues['sSS']
    bgConc['swSed'] = bgValues['sSedS']
    bgConc['S1'] = bgValues['soilS1']
    bgConc['soilW1'] = bgValues['soilW1']
    bgConc['S2'] = bgValues['soilS2']
    bgConc['soilW2'] = bgValues['soilW2']
    bgConc['S3'] = bgValues['soilS3']
    bgConc['soilW3'] = bgValues['soilW3']
    bgConc['S4'] = bgValues['soilS4']
    bgConc['soilW4'] = bgValues['soilW4']
    bgConc['fWdis'] = bgValues['fwdis']
    bgConc['fWSeddis'] = bgValues['fwSeddis']
    bgConc['Swdis'] = bgValues['swdis']
    bgConc['swSeddis'] = bgValues['swSeddis']
    bgConc['soilW1dis'] = bgValues['soilW1dis']
    bgConc['soilW2dis'] = bgValues['soilW2dis']
    bgConc['soilW3dis'] = bgValues['soilW3dis']
    bgConc['soilW4dis'] = bgValues['soilW4dis']
    bgConc['dsoil1'] = bgValues['dsoil1']
    bgConc['dsoil2'] = bgValues['dsoil2']
    bgConc['dsoil3'] = bgValues['dsoil3']
    bgConc['dsoil4'] = bgValues['dsoil4']
    bgConc['gairc'] = bgValues['gairc_n']

    return bgConc


def load_climate(climate_ws):

    # Create Datetime Objects
    new_datetime = []
    dt = zip(climate_ws['year'], climate_ws['month'], climate_ws['day'])
    for val in dt:
        mystring = ' '.join(map(str, val))
        dt = datetime.strptime(mystring, "%Y %m %d")
        new_datetime.append(dt)

    # climate = {}
    climate = OrderedDict()
    climate['dates'] = new_datetime
    climate['precip'] = climate_ws['precipitation']
    climate['windspeed'] = climate_ws['windspeeed']
    climate['flow'] = climate_ws['waterflow']
    climate['temp'] = climate_ws['temperature']
    climate['evap'] = climate_ws['evaporation']

    return climate


def load_ENM(params, presence):
    # ENM = {}
    ENM = OrderedDict(params)

    if presence['air'] == 0:
        ENM['khetA'] = 0
    if presence['fw'] == 0:
        ENM['kdisFW'] = 0
        ENM['kdisFWsed'] == 0
        ENM['ksedFW'] = 0
        ENM['khetFW'] = 0
    if presence['sw'] == 0:
        ENM['kdisSW'] = 0
        ENM['kdisSWsed'] = 0
        ENM['ksedSW'] = 0
        ENM['khetSW'] = 0
        ENM['enrichFactor'] = 0
    if presence['soil1'] == 0:
        ENM['kdisS1'] = 0
        ENM['elutionS1'] = 0
    if presence['soil2'] == 0:
        ENM['kdisS2'] = 0
        ENM['elutionS2'] = 0
    if presence['soil3'] == 0:
        ENM['kdisS3'] = 0
        ENM['elutionS3'] = 0
    if presence['soil4'] == 0:
        ENM['kdisS4'] = 0
        ENM['elutionS4'] = 0

    ENM['density'] = ENM['density'] * 10 ** 9
    ENM['khetA'] = np.true_divide(ENM['khetA'], 10 ** 9)
    ENM['khetFW'] = np.true_divide(ENM['khetFW'], 10 ** 9)
    ENM['khetSW'] = np.true_divide(ENM['khetSW'], 10 ** 9)

    return ENM


def load_env(environment, presence):
    
    env = {}

    for key, value in environment.items():
        if key != 'name':
            for k,v in value.items():
                env.update({k:v['value']})
        else: 
            env.update({key:value})
    env = OrderedDict(env)

    # %% convert all units from kg to pg
    # % concentration and density units are all in kg
    print(env.keys())
    env['airP'] = env['airP'] * 10 ** 9
    env['dynViscAir'] = env['dynViscAir'] * 10 ** 9
    env['aerP'] = env['aerP'] * 10 ** 9
    env['aerC'] = env['aerC'] * 10 ** 9
    env['freshwP'] = env['freshwP'] * 10 ** 9
    env['dynViscFW'] = env['dynViscFW'] * 10 ** 9
    env['freshssP'] = env['freshssP'] * 10 ** 9
    env['freshssC'] = env['freshssC'] * 10 ** 9
    env['dFWSedS'] = env['dFWSedS'] * 10 ** 9
    env['seawP'] = env['seawP'] * 10 ** 9
    env['dynViscSW'] = env['dynViscSW'] * 10 ** 9
    env['seassP'] = env['seassP'] * 10 ** 9
    env['seassC'] = env['seassC'] * 10 ** 9
    env['dSWSedS'] = env['dSWSedS'] * 10 ** 9
    env['dSS1'] = env['dSS1'] * 10 ** 9
    env['dSS2'] = env['dSS2'] * 10 ** 9
    env['dSS3'] = env['dSS3'] * 10 ** 9
    env['dSS4'] = env['dSS4'] * 10 ** 9

    # Air
    # Area of Air (m^2)
    env['area'] = env['freshwA'] + env['seawA'] + env['soilA1'] + env['soilA2'] + env['soilA3'] + env['soilA4']
    # Volume of air (m^3)
    env['airV'] = env['area'] * env['airH']
    # Volume fraction of aerosols
    env['aerVf'] = np.true_divide(env['aerC'], env['aerP'])
    # Aerosols volume (m^3)
    env['aerV'] = env['aerC'] * np.true_divide(env['airV'], env['aerP'])
    # Seawater
    # Volume of seawater (m^3)
    env['seawV'] = env['seawA'] * env['seawD']
    # Seawater suspended sediment volume (m^3)
    env['seassV'] = env['seassC'] * np.true_divide(env['seawV'], env['seassP'])
    # Area of marine sediment (m^2)
    env['sedSWA'] = env['seawA']
    # Volume of marine sediment (m^3)
    env['sedSWV'] = env['sedSWA'] * env['sedSWD']
    # Density of Seawater Sediment (kg/m3)
    env['sedSWP'] = env['dSWSedS'] * env['ssedpercSolid'] + env['seawP'] * (1 - env['ssedpercSolid'])
    # Freshwater
    # Volume of freshwater (m^3)
    env['freshwV'] = env['freshwA'] * env['freshwD']
    # Freshwater suspended sediment volume (m^3)
    env['freshssV'] = env['freshssC'] * np.true_divide(env['freshwV'], env['freshssP'])
    # Area of freshwater sediment (m^2)
    env['sedFWA'] = env['freshwA']
    # Volume of freshwater sediment (m^3)
    env['sedFWV'] = env['sedFWA'] * env['sedFWD']
    # Density of Freshwater Sediment (kg/m3)
    env['sedFWP'] = env['dFWSedS'] * env['fsedpercSolid'] + env['freshwP'] * (1 - env['fsedpercSolid'])
    # Soil 1
    # Soil Volume 1 (m^3)
    env['soilV1'] = env['soilA1'] * env['soilD1'] * (1 - env['soilWC1'] - env['soilAC1'])
    # Soil Density 1 (kg/m3)
    env['soilP1'] = env['dSS1'] * (1 - env['soilWC1'] - env['soilAC1']) + env['freshwP'] * env['soilWC1'] + env[
        'airP'] * env['soilAC1']
    # Soil Water Volume 1 (m^3)
    env['soilwV1'] = env['soilA1'] * env['soilD1'] * env['soilWC1']
    # Soil Air Volume 1 (m^3)
    env['soilaV1'] = env['soilA1'] * env['soilD1'] * env['soilAC1']
    # Length slope factor
    env['lenslope1'] = lsFactor(env['slope1'])
    # CN calculations of S
    env['CN1'] = np.true_divide(1000, env['CN1']) - 10
    # Deep Soil Volume 1 (m^3)
    env['deepsV1'] = env['soilA1'] * env['deepsD1']
    # Soil 2
    # Soil Volume 2 (m^3)
    env['soilV2'] = env['soilA2'] * env['soilD2'] * (1 - env['soilWC2'] - env['soilAC2'])
    # Soil Density 2 (kg/m3)
    env['soilP2'] = env['dSS2'] * (1 - env['soilWC2'] - env['soilAC2']) + env['freshwP'] * env['soilWC2'] + env[
        'airP'] * env['soilAC2']
    # Soil Water Volume 2 (m^3)
    env['soilwV2'] = env['soilA2'] * env['soilD2'] * env['soilWC2']
    # Soil Air Volume 2 (m^3)
    env['soilaV2'] = env['soilA2'] * env['soilD2'] * env['soilAC2']
    # Length slope factor
    env['lenslope2'] = lsFactor(env['slope2'])
    # CN calculations of S
    env['CN2'] = np.true_divide(1000, env['CN2']) - 10
    # Deep Soil Volume 2 (m^3)
    env['deepsV2'] = env['soilA2'] * env['deepsD2']
    # Soil 3
    # Soil Volume 3 (m^3)
    env['soilV3'] = env['soilA3'] * env['soilD3'] * (1 - env['soilWC3'] - env['soilAC3'])
    # Soil Density 3 (kg/m3)
    env['soilP3'] = env['dSS3'] * (1 - env['soilWC3'] - env['soilAC3']) + env['freshwP'] * env['soilWC3'] + env[
        'airP'] * env['soilAC3']
    # Soil Water Volume 3 (m^3)
    env['soilwV3'] = env['soilA3'] * env['soilD3'] * env['soilWC3']
    # Soil Air Volume 3 (m^3)
    env['soilaV3'] = env['soilA3'] * env['soilD3'] * env['soilAC3']
    # Length slope factor
    env['lenslope3'] = lsFactor(env['slope3'])
    # CN calculations of S
    env['CN3'] = np.true_divide(1000, env['CN3']) - 10
    # Deep Soil Volume 3 (m^3)
    env['deepsV3'] = env['soilA3'] * env['deepsD3']
    # Soil 4
    # Soil Volume 4 (m^3)
    env['soilV4'] = env['soilA4'] * env['soilD4'] * (1 - env['soilWC4'] - env['soilAC4'])
    # Soil Density 1 (kg/m3)
    env['soilP4'] = env['dSS4'] * (1 - env['soilWC4'] - env['soilAC4']) + env['freshwP'] * env['soilWC4'] + env[
        'airP'] * env['soilAC4']
    # Soil Water Volume 4 (m^3)
    env['soilwV4'] = env['soilA4'] * env['soilD4'] * env['soilWC4']
    # Soil Air Volume 4 (m^3)
    env['soilaV4'] = env['soilA4'] * env['soilD4'] * env['soilAC4']
    # Length slope factor
    env['lenslope4'] = lsFactor(env['slope4'])
    # CN calculations of S
    env['CN4'] = np.true_divide(1000, env['CN4']) - 10
    # Deep Soil Volume 4 (m^3)
    env['deepsV4'] = env['soilA4'] * env['deepsD4']

    if presence['air'] == 0:
        env['airA'] = 0
        env['airV'] = 0
        env['airH'] = 0
        env['dynViscAir'] = 0
        env['scavengingENM'] = 0
    if presence['aer'] == 0:
        env['aerVf'] = 0
        env['aerV'] = 0
        env['aerP'] = 0
        env['aerC'] = 0
        env['radiusParclesAer'] = 0
        env['scavenging'] = 0
    if presence['fw'] == 0:
        env['freshwA'] = 0
        env['freshwD'] = 0
        env['freshwV'] = 0
        env['freshwP'] = 0
        env['freshwpH'] = 0
        env['dynViscFW'] = 0
        env['freshssP'] = 0
        env['freshssC'] = 0
        env['freshssV'] = 0
        env['radiusParticlesFW'] = 0
        env['freshssOC'] = 0
        env['sedFWD'] = 0
        env['sedFWA'] = 0
        env['sedFWV'] = 0
        env['dFWSedS'] = 0
        env['fsedpercSolid'] = 0
        env['burialRateFW'] = 0
        env['resuspensionRateFW'] = 0
        env['fwadvfrac'] = 0
    if presence['fw'] == 0:
        env['freshwA'] = 0
        env['freshwD'] = 0
        env['freshwV'] = 0
        env['freshwP'] = 0
        env['freshwpH'] = 0
        env['dynViscFW'] = 0
        env['fwadvfrac'] = 0
    if presence['fSS'] == 0:
        env['freshssP'] = 0
        env['freshssC'] = 0
        env['freshssV'] = 0
        env['radiusParticlesFW'] = 0
        env['freshssOC'] = 0
    if presence['fSed'] == 0:
        env['sedFWD'] = 0
        env['sedFWA'] = 0
        env['sedFWV'] = 0
        env['dFWSedS'] = 0
        env['fsedpercSolid'] = 0
        env['burialRateFW'] = 0
        env['resuspensionRateFW'] = 0
    if presence['sw'] == 0:
        env['seawA'] = 0
        env['seawD'] = 0
        env['seawV'] = 0
        env['seawP'] = 0
        env['seawpH'] = 0
        env['dynViscSW'] = 0
        env['coastalA'] = 0
        env['seassP'] = 0
        env['seassC'] = 0
        env['seassV'] = 0
        env['radiusParticlesSW'] = 0
        env['marinessOC'] = 0
        env['sedSWD'] = 0
        env['sedSWA'] = 0
        env['sedSWV'] = 0
        env['dSWSedS'] = 0
        env['ssedpercSolid'] = 0
        env['sedSWOC'] = 0
        env['burialRateSW'] = 0
        env['resuspensionRateSW'] = 0
        env['swadvfrac'] = 0
    if presence['sw'] == 0:
        env['seawA'] = 0
        env['seawD'] = 0
        env['seawV'] = 0
        env['seawP'] = 0
        env['seawpH'] = 0
        env['dynViscSW'] = 0
        env['coastalA'] = 0
        env['swadvfrac'] = 0
    if presence['sSS'] == 0:
        env['seassP'] = 0
        env['seassC'] = 0
        env['seassV'] = 0
        env['radiusParticlesSW'] = 0
        env['marinessOC'] = 0
    if presence['sSed'] == 0:
        env['sedSWD'] = 0
        env['sedSWA'] = 0
        env['sedSWV'] = 0
        env['dSWSedS'] = 0
        env['ssedpercSolid'] = 0
        env['sedSWOC'] = 0
        env['burialRateSW'] = 0
        env['resuspensionRateSW'] = 0
    if presence['soil1'] == 0:
        env['soilA1'] = 0
        env['soilD1'] = 0
        env['soilV1'] = 0
        env['soilP1'] = 0
        env['dSS1'] = 0
        env['soilwV1'] = 0
        env['soilaV1'] = 0
        env['soilWpH1'] = 0
        env['deepsV1'] = 0
        env['deepswV1'] = 0
        env['deepsaV1'] = 0
        env['lenslope1'] = 0
        env['CN1'] = 0
        env['deepsD1'] = 0
        env['A1'] = 0
        env['TSV1'] = 0
        env['z_wind1'] = 0
        env['roughness1'] = 0
        env['Kconstant1'] = 0
        env['percWind1'] = 0
        env['windConstant1'] = 0
        env['percUncovered1'] = 0
        env['percSuspended1'] = 0
        env['Kfact1'] = 0
        env['slope1'] = 0
        env['cropManageFactor1'] = 0
        env['supportFactor1'] = 0
        env['leachingR1'] = 0
    if presence['soil2'] == 0:
        env['soilA2'] = 0
        env['soilD2'] = 0
        env['soilV2'] = 0
        env['soilP2'] = 0
        env['dSS2'] = 0
        env['soilwV2'] = 0
        env['soilaV2'] = 0
        env['soilWpH2'] = 0
        env['deepsV2'] = 0
        env['deepswV2'] = 0
        env['deepsaV2'] = 0
        env['lenslope2'] = 0
        env['CN2'] = 0
        env['deepsD2'] = 0
        env['A2'] = 0
        env['TSV2'] = 0
        env['z_wind2'] = 0
        env['roughness2'] = 0
        env['Kconstant2'] = 0
        env['percWind2'] = 0
        env['windConstant2'] = 0
        env['percUncovered2'] = 0
        env['percSuspended2'] = 0
        env['Kfact2'] = 0
        env['slope2'] = 0
        env['cropManageFactor2'] = 0
        env['supportFactor2'] = 0
        env['leachingR2'] = 0
    if presence['soil3'] == 0:
        env['soilA3'] = 0
        env['soilD3'] = 0
        env['soilV3'] = 0
        env['soilP3'] = 0
        env['dSS3'] = 0
        env['soilwV3'] = 0
        env['soilaV3'] = 0
        env['soilWpH3'] = 0
        env['deepsV3'] = 0
        env['deepswV3'] = 0
        env['deepsaV3'] = 0
        env['lenslope3'] = 0
        env['CN3'] = 0
        env['deepsD3'] = 0
        env['A3'] = 0
        env['TSV3'] = 0
        env['z_wind3'] = 0
        env['roughness3'] = 0
        env['Kconstant3'] = 0
        env['percWind3'] = 0
        env['windConstant3'] = 0
        env['percUncovered3'] = 0
        env['percSuspended3'] = 0
        env['Kfact3'] = 0
        env['slope3'] = 0
        env['cropManageFactor3'] = 0
        env['supportFactor3'] = 0
        env['leachingR3'] = 0
    if presence['soil4'] == 0:
        env['soilA4'] = 0
        env['soilD4'] = 0
        env['soilV4'] = 0
        env['soilP4'] = 0
        env['dSS4'] = 0
        env['soilwV4'] = 0
        env['soilaV4'] = 0
        env['soilWpH4'] = 0
        env['deepsV4'] = 0
        env['deepswV4'] = 0
        env['deepsaV4'] = 0
        env['lenslope4'] = 0
        env['CN4'] = 0
        env['deepsD4'] = 0
        env['A4'] = 0
        env['TSV4'] = 0
        env['z_wind4'] = 0
        env['roughness4'] = 0
        env['Kconstant4'] = 0
        env['percWind4'] = 0
        env['windConstant4'] = 0
        env['percUncovered4'] = 0
        env['percSuspended4'] = 0
        env['Kfact4'] = 0
        env['slope4'] = 0
        env['cropManageFactor4'] = 0
        env['supportFactor4'] = 0
        env['leachingR4'] = 0

    return env


def load_presence(presence):
    
    # presence = {}
    presence = OrderedDict(presence)

    # str_list = list(filter(None, presence.values()))

    # if the user ever wants to make unique changes to the presence/absence data
    # beyond simply the bulk compartments.  They would do it here for individual runs.
    # For example, the user might want freshwater without suspended sediment. By changing
    # line 51 set to 0 always, you eliminate the suspended sediment compartment.
    if presence['air'] == 1:
        presence['aer'] = 1
    else:
        presence['aer'] = 0
    if presence['fw'] == 1:
        presence['fw'] = 1
        presence['fSS'] = 1
        presence['fSed'] = 1
        presence['fSedS'] = 1
        presence['fSedW'] = 1
    else:
        presence['fw'] = 0
        presence['fSS'] = 0
        presence['fSed'] = 0
        presence['fSedS'] = 0
        presence['fSedW'] = 0
    if presence['sw'] == 1:
        presence['sw'] = 1
        presence['sSS'] = 1
        presence['sSed'] = 1
        presence['sSedS'] = 1
        presence['sSedW'] = 1
    else:
        presence['sw'] = 0
        presence['sSS'] = 0
        presence['sSed'] = 0
        presence['sSedS'] = 0
        presence['sSedW'] = 0
    if presence['soil1'] == 1:
        presence['soilS1'] = 1
        presence['soilW1'] = 1
        presence['soilDeep1'] = 1
    else:
        presence['soilS1'] = 0
        presence['soilW1'] = 0
        presence['soilDeep1'] = 0
    if presence['soil2'] == 1:
        presence['soilS2'] = 1
        presence['soilW2'] = 1
        presence['soilDeep2'] = 1
    else:
        presence['soilS2'] = 0
        presence['soilW2'] = 0
        presence['soilDeep2'] = 0
    if presence['soil3'] == 1:
        presence['soilS3'] = 1
        presence['soilW3'] = 1
        presence['soilDeep3'] = 1
    else:
        presence['soilS3'] = 0
        presence['soilW3'] = 0
        presence['soilDeep3'] = 0
    if presence['soil4'] == 1:
        presence['soilS4'] = 1
        presence['soilW4'] = 1
        presence['soilDeep4'] = 1
    else:
        presence['soilS4'] = 0
        presence['soilW4'] = 0
        presence['soilDeep4'] = 0

    return presence


def load_release(release, presence):
    
    release_inp = {k: [dic[k] for dic in release[0]] for k in release[0][0]}

    release_inp['scenario'] = release[1]
    # Create Datetime Objects
    new_datetime = []
    dt = zip(release_inp['year'], release_inp['month'], release_inp['day'])
    for val in dt:
        mystring = ' '.join(map(str, val))
        dt = datetime.strptime(mystring, "%Y %m %d")
        new_datetime.append(dt)

    # release = {}
    release = OrderedDict()
    release['dates'] = new_datetime
    release['air'] = [x * 10 ** 9 for x in release_inp['air']]
    release['fw'] = [x * 10 ** 9 for x in release_inp['freshwater']]
    release['fSS'] = [x * 10 ** 9 for x in release_inp['freshwater_ss']]
    release['fwSed'] = [x * 10 ** 9 for x in release_inp['freshwater_sed']]
    release['sw'] = [x * 10 ** 9 for x in release_inp['seawater']]
    release['sSS'] = [x * 10 ** 9 for x in release_inp['seawater_ss']]
    release['swSed'] = [x * 10 ** 9 for x in release_inp['seawater_sed']]
    release['soil1'] = [x * 10 ** 9 for x in release_inp['undeveloped_soil']]
    release['dsoil1'] = [x * 10 ** 9 for x in release_inp['undeveloped_deep_soil']]
    release['soil2'] = [x * 10 ** 9 for x in release_inp['urban_soil']]
    release['dsoil2'] = [x * 10 ** 9 for x in release_inp['urban_deep_soil']]
    release['soil3'] = [x * 10 ** 9 for x in release_inp['agricultural_soil']]
    release['dsoil3'] = [x * 10 ** 9 for x in release_inp['agricultural_deep_soil']]
    release['soil4'] = [x * 10 ** 9 for x in release_inp['agricultural_soil_biosolid']]
    release['dsoil4'] = [x * 10 ** 9 for x in release_inp['agricultural_deep_soil_biosolid']]

    if presence['air'] == 0:
        release['Air'] = [x * 0 for x in release_inp['air']]
    if presence['fw'] == 0:
        release['fw'] = [x * 0 for x in release_inp['freshwater']]
    if presence['sw'] == 0:
        release['sw'] = [x * 0 for x in release_inp['seawater']]
    if presence['soil1'] == 0:
        release['Soil1'] = [x * 0 for x in release_inp['undeveloped_soil']]
    if presence['soil2'] == 0:
        release['Soil2'] = [x * 0 for x in release_inp['urban_soil']]
    if presence['soil3'] == 0:
        release['Soil3'] = [x * 0 for x in release_inp['agricultural_soil']]
    if presence['soil4'] == 0:
        release['Soil4'] = [x * 0 for x in release_inp['agricultural_soil_biosolid']]

    return release, release_inp['scenario']


def load_data(region, release, material, start_date, days):
    # original start date will change if user does custom datasets...
    original_start_date = datetime.strptime('2005 1 1', "%Y %m %d")
    start_day = datetime.strptime(start_date, "%Y %m %d")
    end_day = start_day + timedelta(days=days)
    time = (end_day - start_day).days + 1

    presence = load_presence(region['Presence'])
    env = load_env(region['Environment'], presence)
    climate = load_climate(region['Climate'])
    bgConc = load_bgConc(release[0], presence)
    ENM = load_ENM(material['params'], presence)
    release_out, release_scenario = load_release(release[1:], presence)

    return time, presence, env, climate, bgConc, ENM, release_out, release_scenario