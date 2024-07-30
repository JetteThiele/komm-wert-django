import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from pathlib import Path
import locale
import csv
import json
import sys
import os
import logging
import time

timestamp = int(time.time())
logging.debug("Script started")
logging.basicConfig(level=logging.DEBUG)
locale.setlocale(locale.LC_ALL, 'C')

if 'DYNO' in os.environ:
    # Heroku-Umgebung
    SEQUENCES_DIR = Path('/tmp/sequences')
    PLOTS_DIR = Path('/tmp/plots')
else:
    # Lokale Umgebung
    CURRENT_DIR = Path(__file__).resolve().parent
    SEQUENCES_DIR = CURRENT_DIR / 'data/sequences'
    PLOTS_DIR = CURRENT_DIR / 'tmp/plots'

try:
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
except Exception as e:
    sys.exit(1)

def read_form_data():
    data = {}
    try:
        with open(CURRENT_DIR / 'tmp/input_variables.csv', mode='r', encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                for key, value in row.items():
                    if key in []:  # divide percentage by 100
                        value = float(value) / 100
                    else:
                        try:
                            value = float(value)
                        except ValueError:
                            pass
                    data[key] = value

                flaechen_eigentuemer = {
                    'wea': [],
                    'apvv': [],
                    'apvh': [],
                    'pv': []
                }
                counter = 1
                while True:
                    wea_ownertype_key = f'wea_area_ownertype{counter}'
                    wea_flaechenanteil_key = f'wea_anteil_flaeche{counter}'
                    apvv_ownertype_key = f'apvv_area_ownertype{counter}'
                    apvv_flaechenanteil_key = f'apvv_anteil_flaeche{counter}'
                    apvh_ownertype_key = f'apvh_area_ownertype{counter}'
                    apvh_flaechenanteil_key = f'apvh_anteil_flaeche{counter}'
                    pv_ownertype_key = f'ffpv_area_ownertype{counter}'
                    pv_flaechenanteil_key = f'ffpv_anteil_flaeche{counter}'

                    found_any = False

                    if wea_ownertype_key in row and row[wea_ownertype_key]:
                        eigentuemer = {
                            'ownertype': row.get(wea_ownertype_key, 'default_ownertype'),
                            'flaechenanteil': float(row.get(wea_flaechenanteil_key, 0))  # Convert to float
                        }
                        flaechen_eigentuemer['wea'].append(eigentuemer)
                        found_any = True

                    if apvv_ownertype_key in row and row[apvv_ownertype_key]:
                        eigentuemer = {
                            'ownertype': row.get(apvv_ownertype_key, 'default_ownertype'),
                            'flaechenanteil': float(row.get(apvv_flaechenanteil_key, 0))  # Convert to float
                        }
                        flaechen_eigentuemer['apvv'].append(eigentuemer)
                        found_any = True

                    if apvh_ownertype_key in row and row[apvh_ownertype_key]:
                        eigentuemer = {
                            'ownertype': row.get(apvh_ownertype_key, 'default_ownertype'),
                            'flaechenanteil': float(row.get(apvh_flaechenanteil_key, 0))  # Convert to float
                        }
                        flaechen_eigentuemer['apvh'].append(eigentuemer)
                        found_any = True

                    if pv_ownertype_key in row and row[pv_ownertype_key]:
                        eigentuemer = {
                            'ownertype': row.get(pv_ownertype_key, 'default_ownertype'),
                            'flaechenanteil': float(row.get(pv_flaechenanteil_key, 0))  # Convert to float
                        }
                        flaechen_eigentuemer['pv'].append(eigentuemer)
                        found_any = True

                    if not found_any:
                        break

                    counter += 1

            default_eigentuemer = {
                'ownertype': 'Landes-/Bundeseigentum',
                'flaechenanteil': 0
            }

            if not flaechen_eigentuemer['wea']:
                flaechen_eigentuemer['wea'].append(default_eigentuemer)
            if not flaechen_eigentuemer['apvv']:
                flaechen_eigentuemer['apvv'].append(default_eigentuemer)
            if not flaechen_eigentuemer['apvh']:
                flaechen_eigentuemer['apvh'].append(default_eigentuemer)
            if not flaechen_eigentuemer['pv']:
                flaechen_eigentuemer['pv'].append(default_eigentuemer)

            # Ensure lists are of equal length for consistency
            max_length = max(len(flaechen_eigentuemer['wea']), len(flaechen_eigentuemer['apvv']),
                             len(flaechen_eigentuemer['apvh']), len(flaechen_eigentuemer['pv']))

            def extend_list(lst):
                while len(lst) < max_length:
                    lst.append({'ownertype': 'N/A', 'flaechenanteil': 0})
                return lst

            flaechen_eigentuemer['wea'] = extend_list(flaechen_eigentuemer['wea'])
            flaechen_eigentuemer['apvv'] = extend_list(flaechen_eigentuemer['apvv'])
            flaechen_eigentuemer['apvh'] = extend_list(flaechen_eigentuemer['apvh'])
            flaechen_eigentuemer['pv'] = extend_list(flaechen_eigentuemer['pv'])

            data['flaechen_eigentuemer'] = flaechen_eigentuemer

    except Exception as e:
        print(json.dumps({"status": "error", "message": f"Fehler beim Lesen der Formulardaten: {str(e)}"}))
        sys.exit(1)

    return data

# eeg and wind- and solar euro parameters
eeg_beteiligung = 2 # €/MWh
bb_euro_mw_wind = 5000 # €/MW
bb_euro_mw_pv = 2000 # €/MW
# taxes
ekst = 0.24 # 24% income tax
ekst_bb = 0.15 # 15% municipal share
year_income_bb = 24122 # average annual income in BB in €
freibetrag = 24500 # tax-free amount for partner companies
steuermessbetrag = 0.035 # fix for DE
income_betriebe_bb = 220000 # annual income of businesses
# area costs per ha
pv_area_costs = 3000 # €/ha
apv_area_costs = 830 # €/ha
wea_area_costs = 16000 # € / MW
# colors
htw_green = '#76B900'
htw_blue = '#0082D1'
htw_orange = '#FF5F00'
htw_grey = '#AFAFAF'
htw_yellow = '#FDDA0D'
def main():
    results = {}  # Define results dictionary before the try block to ensure accessibility in case of an error
    try:

        form_data = read_form_data()
        ffpv_area_max = form_data.get('ffpv_area_max', 0)
        apvv_area_max = form_data.get('apvv_area_max', 0)
        apvh_area_max = form_data.get('apvh_area_max', 0)
        wea_area_max = form_data.get('wea_area_max', 0)
        wea_eeg_share = form_data.get('wea_eeg_share', 100)
        wind_euro_share = form_data.get('wind_euro_share', 100)
        rotor_diameter = form_data.get('rotor_diameter', 130)
        system_output = form_data.get('system_output', 4)
        wea_p_max = form_data.get('wea_p_max', 0)
        pv_p_max = form_data.get('pv_p_max', 0)
        apv_ver_p_max = form_data.get('apv_ver_p_max', 0)
        apv_hor_p_max = form_data.get('apv_hor_p_max', 0)
        flaechen_eigentuemer = form_data.get('flaechen_eigentuemer', {})
        mun_key_value = form_data.get('mun_key_value', 334)
        levy_rate = form_data.get('levy_rate', 0.003)
        apvv_mw_ha = 0.35
        apvh_mw_ha = 0.65

        if levy_rate == 0:
            sz_ghm = 0.3
        else:
            sz_ghm = levy_rate * 100
        if mun_key_value == 0:
            hebesatz = 3.34
        else:
            hebesatz = mun_key_value / 100
        if wea_eeg_share == 0:
            wea_eeg_share = 1
        else:
            wea_eeg_share = wea_eeg_share / 100
        if wind_euro_share == 0:
            wind_euro_share = 1
        else:
            wind_euro_share = wind_euro_share / 100
        # Calculate max. power if only area is given
        if wea_p_max == 0 and wea_area_max != 0:
            A_wea = np.pi * rotor_diameter * 1.5 * rotor_diameter * 2.5
            N_wea = round((wea_area_max * 10000) / A_wea)
            wea_p_max = system_output * N_wea
        else:
            wea_p_max = wea_p_max
        if pv_p_max == 0 and ffpv_area_max != 0:
            pv_p_max = ffpv_area_max
        else:
            pv_p_max = pv_p_max
        if apv_ver_p_max == 0 and apvv_area_max != 0:
            apv_ver_p_max = apvv_area_max * apvv_mw_ha
        else:
            apv_ver_p_max = apv_ver_p_max
        if apv_hor_p_max == 0 and apvh_area_max != 0:
            apv_hor_p_max = apvh_area_max * apvh_mw_ha
        else:
            apv_hor_p_max = apv_hor_p_max

        # Calculate area if only power is given
        if wea_area_max == 0 and wea_p_max != 0:
            A_wea = np.pi * (rotor_diameter * 1.5) * (rotor_diameter * 2.5)
            N_wea = round(wea_p_max / system_output)
            wea_area_max = (A_wea * N_wea) / 10000
        else:
            wea_area_max = wea_area_max
        if ffpv_area_max == 0 and pv_p_max != 0:
            ffpv_area_max = pv_p_max
        else:
            ffpv_area_max = ffpv_area_max
        if apvv_area_max == 0 and apv_ver_p_max != 0:
            apvv_area_max = apv_ver_p_max / apvv_mw_ha
        else:
            apvv_area_max = apvv_area_max
        if apvh_area_max == 0 and apv_hor_p_max != 0:
            apvh_area_max = apvh_area_max / apvh_mw_ha
        else:
            apvh_area_max = apvh_area_max

        # invest costs for tec depending on power of tec
        if system_output < 4:
            wea_invest_cost = 1846000
        elif system_output < 5:
            wea_invest_cost = 1676000
        elif system_output < 6:
            wea_invest_cost = 1556000
        else:
            wea_invest_cost = 1561000

        if pv_p_max == 1:
            ffpv_invest_costs = 840000
        elif pv_p_max < 2:
            ffpv_invest_costs = 800000
        elif pv_p_max < 5:
            ffpv_invest_costs = 770000
        else:
            ffpv_invest_costs = 750000

        if apv_ver_p_max == 1:
            apvv_invest_costs = 840000*1.108
        elif apv_ver_p_max < 2:
            apvv_invest_costs = 800000*1.108
        elif apv_ver_p_max < 5:
            apvv_invest_costs = 770000*1.108
        else:
            apvv_invest_costs = 750000*1.108

        if apv_hor_p_max == 1:
            apvh_invest_costs = 840000*1.26
        elif apv_hor_p_max < 2:
            apvh_invest_costs = 800000*1.26
        elif apv_hor_p_max < 5:
            apvh_invest_costs = 770000*1.26
        else:
            apvh_invest_costs = 750000*1.26

        wind_profile = pd.read_csv(SEQUENCES_DIR / 'wind-onshore_profile.csv', delimiter=';')
        agri_pv_hor_profile = pd.read_csv(SEQUENCES_DIR / 'agri-pv_hor_ground_profile.csv', header=0, delimiter=';')
        agri_pv_ver_profile = pd.read_csv(SEQUENCES_DIR / 'agri-pv_ver_ground_profile.csv', header=0, delimiter=';')
        ff_pv_profile = pd.read_csv(SEQUENCES_DIR / 'solar-pv_ground_profile.csv', delimiter=';')

        plot_file_komm_wert_jaehrliche_pachteinnahmen = f'komm-wert-jaehrliche-pachteinnahmen_{timestamp}.png'
        plot_file_einnahmen_wind_solar_euro = f'einnahmen-wind-solar-euro_{timestamp}.png'
        plot_file_komm_wert_eeg_einnahmen = f'komm-wert-eeg-einnahmen_{timestamp}.png'

        # calculate income tax for the regular average income
        z_income = int(year_income_bb - 17005) / 10000
        est_income = int((181.19 * z_income + 2397) * z_income + 1025.38)

        def calc_tax_income(taxable_income):
            income = int(taxable_income)

            if income <= 11604:
                taxes = 0
            elif income <= 17005:
                y = (income - 11604) / 10000
                taxes = round((922.98 * y + 1400) * y)
            elif income <= 66760:
                z = (income - 17005) / 10000
                taxes = round((181.19 * z + 2397) * z + 1025.38)
            elif income <= 277825:
                taxes = round(0.42 * income - 10602.13)
            else:
                taxes = round(0.45 * income - 18936.88)

            return taxes

        gewerbesteuer_income = (income_betriebe_bb - freibetrag) * steuermessbetrag * hebesatz

        def process_area(max_area, ownertype, flaechenanteil, area_costs, income_betriebe_bb, steuermessbetrag,
                         hebesatz, gewerbesteuer_income, year_income_bb, est_income, ekst_bb, sz_ghm):
            flaechenanteil = flaechenanteil / 100  # Convert to decimal if percentage is given
            if ownertype == 'Gewerbliches Eigentum':
                area_gewst = int(((((max_area * area_costs * flaechenanteil) + income_betriebe_bb - freibetrag)
                                   * steuermessbetrag * hebesatz) - gewerbesteuer_income))
                area_gewst_total = area_gewst - int(
                    (((max_area * flaechenanteil * area_costs) * steuermessbetrag / hebesatz) * 0.35))
                area_income = 0
                ghm_est_income = 0
            elif ownertype == 'Privateigentum':
                area_income_max = area_costs * (max_area * flaechenanteil) + year_income_bb
                taxes_list = []
                for income in [area_income_max]:  # List for comprehension
                    taxes = calc_tax_income(income)
                    taxes_list.append(taxes - est_income)
                ghm_est_income = taxes_list[0] * ekst_bb * sz_ghm
                area_gewst_total = 0
                area_income = 0
            elif ownertype == 'Gemeindeeigentum':
                area_income = area_costs * max_area * flaechenanteil
                area_gewst_total = 0
                ghm_est_income = 0
            else:
                area_income = 0
                area_gewst_total = 0
                ghm_est_income = 0
            return area_income, area_gewst_total, ghm_est_income

        # Variables to accumulate the results
        apvh_area_income = apvh_area_gewst_total = ghm_est_income_apvh = 0
        apvv_area_income = apvv_area_gewst_total = ghm_est_income_apvv = 0
        pv_area_income = pv_area_gewst_total = ghm_est_income_pv = 0
        wea_area_income = wea_area_gewst_total = ghm_est_income_wea = 0

        # Processing each ownertype for each category
        for apvh_eigentuemer in flaechen_eigentuemer['apvh']:
            eigentuemer_input_apvh = (
                apvh_area_max, apvh_eigentuemer['ownertype'], apvh_eigentuemer['flaechenanteil'], apv_area_costs,
                income_betriebe_bb, steuermessbetrag, hebesatz, gewerbesteuer_income, year_income_bb, est_income,
                ekst_bb,
                sz_ghm
            )
            area_income, area_gewst_total, ghm_est_income = process_area(*eigentuemer_input_apvh)
            apvh_area_income += area_income
            apvh_area_gewst_total += area_gewst_total
            ghm_est_income_apvh += ghm_est_income

        for apvv_eigentuemer in flaechen_eigentuemer['apvv']:
            eigentuemer_input_apvv = (
                apvv_area_max, apvv_eigentuemer['ownertype'], apvv_eigentuemer['flaechenanteil'], apv_area_costs,
                income_betriebe_bb, steuermessbetrag, hebesatz, gewerbesteuer_income, year_income_bb, est_income,
                ekst_bb,
                sz_ghm
            )
            area_income, area_gewst_total, ghm_est_income = process_area(*eigentuemer_input_apvv)
            apvv_area_income += area_income
            apvv_area_gewst_total += area_gewst_total
            ghm_est_income_apvv += ghm_est_income

        for pv_eigentuemer in flaechen_eigentuemer['pv']:
            eigentuemer_input_pv = (
                ffpv_area_max, pv_eigentuemer['ownertype'], pv_eigentuemer['flaechenanteil'], pv_area_costs,
                income_betriebe_bb, steuermessbetrag, hebesatz, gewerbesteuer_income, year_income_bb, est_income,
                ekst_bb,
                sz_ghm
            )
            area_income, area_gewst_total, ghm_est_income = process_area(*eigentuemer_input_pv)
            pv_area_income += area_income
            pv_area_gewst_total += area_gewst_total
            ghm_est_income_pv += ghm_est_income

        for wea_eigentuemer in flaechen_eigentuemer['wea']:
            eigentuemer_input_wea = (
                wea_p_max, wea_eigentuemer['ownertype'], wea_eigentuemer['flaechenanteil'], wea_area_costs,
                income_betriebe_bb, steuermessbetrag, hebesatz, gewerbesteuer_income, year_income_bb, est_income,
                ekst_bb,
                sz_ghm
            )
            area_income, area_gewst_total, ghm_est_income = process_area(*eigentuemer_input_wea)
            wea_area_income += area_income
            wea_area_gewst_total += area_gewst_total
            ghm_est_income_wea += ghm_est_income

        area_costs_yearly = [wea_area_income, pv_area_income, apvh_area_income + apvv_area_income]
        area_gewst_yearly = [wea_area_gewst_total, pv_area_gewst_total, apvh_area_gewst_total + apvv_area_gewst_total]
        area_est_yearly = [ghm_est_income_wea, ghm_est_income_pv, ghm_est_income_apvh + ghm_est_income_apvv]
        '''
        EEG participation
        '''
        check = ff_pv_profile['GHM-solar-pv_ground-profile'].sum()
        wind_eeg_yearly = ((np.array(wind_profile['GHM-wind-onshore-profile']) * wea_p_max) * eeg_beteiligung).sum() * wea_eeg_share
        pv_eeg_yearly = ((ff_pv_profile['GHM-solar-pv_ground-profile'] * pv_p_max) * eeg_beteiligung).sum()
        apv_eeg_yearly = (((agri_pv_ver_profile['GHM-agri-pv_ver_ground-profile'] * apv_ver_p_max) + (
                    agri_pv_hor_profile['GHM-agri-pv_hor_ground-profile'] * apv_hor_p_max)) * eeg_beteiligung).sum()


        # performance degradation
        degradation_pv = 0.005
        degradation_wind = 0.006

        def calculate_degraded_sum(initial_value, degradation_rate, years=25):
            total = 0
            yearly_eeg = []

            for year in range(1, years + 1):
                degraded_value = initial_value * (1 - degradation_rate) ** year
                total += degraded_value
                yearly_eeg.append(degraded_value)

            return total, yearly_eeg

        iterations = 25

        wind_eeg_degradation_result, wind_eeg_degradation_yearly = calculate_degraded_sum(wind_eeg_yearly,
                                                                                          degradation_wind, iterations)
        pv_eeg_degradation_result, pv_eeg_degradation_yearly = calculate_degraded_sum(pv_eeg_yearly, degradation_pv,
                                                                                      iterations)
        apv_eeg_degradation_result, apv_eeg_degradation_yearly = calculate_degraded_sum(apv_eeg_yearly, degradation_pv,
                                                                                        iterations)

        '''
        Sonderregelung BB
        '''

        # Calculation with 6 WTGs into operation from 2025
        wind_sr_bb_yearly = (wea_p_max * bb_euro_mw_wind) * wind_euro_share
        pv_sr_bb_yearly = pv_p_max * bb_euro_mw_pv
        apv_sr_bb_yearly = (apv_ver_p_max + apv_hor_p_max) * bb_euro_mw_pv

        '''
        Plots
        '''

        # Yearly area costs and municipal revenue
        n_groups = 3
        # create plot
        fig, ax = plt.subplots()
        index = np.arange(n_groups) * 1.5 # Abstand einfügen
        bar_width = 0.3
        opacity = 1
        #ax_sec = ax.twinx()  # second y-axis

        def format_height(height):
            if height >= 1_000_000:
                return f"{height / 1_000_000:.1f}".replace(".", ",")
            elif height > 0:
                return f"{height / 1_000:.1f}".replace(".", ",")
            else:
                return str()

        def custom_formatter(x, pos):
            if x >= 1_000_000:
                return f'{x / 1_000_000:.1f} Mio €'.replace(".", ",")
            elif x >= 0:
                return f'{x / 1_000:.1f} T€'.replace(".", ",")
            else:
                return str(x)

        # Filter bars with height 0
        area_costs_yearly_filtered = area_costs_yearly
        indexes_costs_yearly_filtered = range(len(area_costs_yearly))

        plot_area_costs = ax.bar(index + bar_width * 2.5, area_costs_yearly, bar_width,
                                 alpha=opacity,
                                 color=htw_green,
                                 label='Direkte Pachteinnahmen',
                                 zorder=2)

        plot_area_ekst = ax.bar(index + bar_width * (-0.3), area_est_yearly, bar_width,
                                    alpha=opacity,
                                    color=htw_yellow,
                                    label='Komm. ESt-Anteil',
                                    zorder=2)

        plot_area_gewst = ax.bar(index + bar_width * 1.1, area_gewst_yearly, bar_width,
                                     alpha=opacity,
                                     color=htw_orange,
                                     label='Komm. GewSt-Anteil',
                                     zorder=2)

        # display values above the bar
        for rect in plot_area_costs + plot_area_ekst + plot_area_gewst:
            height = rect.get_height()
            formatted_height = format_height(height)
            ax.annotate(formatted_height,
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontweight='bold', fontsize='9')

        ax.set_ylabel('Einnahmen in €', fontweight='bold', fontsize='10', labelpad=10)
        plt.xticks(index + bar_width, ('WEA-MAX', 'FFPV-MAX', 'APV-MAX'))
        lines1, labels1 = ax.get_legend_handles_labels()
        plt.legend(lines1, labels1, bbox_to_anchor=(0.5, -0.1), loc='upper center', ncol=2,
                   shadow=False, frameon=False)
        ax.grid(True, linestyle='-', zorder=0, color='#ddd')
        ax.ticklabel_format(axis='y', style='plain', useOffset=False)

        ax.yaxis.set_major_formatter(custom_formatter)
        plt.tight_layout()
        plt.savefig(PLOTS_DIR / plot_file_komm_wert_jaehrliche_pachteinnahmen)
        plt.close()  # Wichtig: Figure schließen, um Speicher zu sparen

        # EEG participation + wind and solar euro
        def create_bar_plot(index, bar_labels, bar_values, bar_width, y_label, title, output_file, bar_colors
                            ):
            fig, ax = plt.subplots()
            n_bars = len(bar_labels)

            for i, (label, values, color) in enumerate(zip(bar_labels, bar_values, bar_colors)):
                ax.bar(index + i * 1.1 * bar_width, values, bar_width, alpha=1, label=label, zorder=2, color=color)

            # Zahlenwerte über den Balken anzeigen
            for rect in ax.patches:
                height = rect.get_height()
                formatted_height = format_height(height)

                if height != 0:
                    ax.annotate(formatted_height,
                                xy=(rect.get_x() + rect.get_width() / 2, height),
                                xytext=(0, 3),
                                textcoords="offset points",
                                ha='center', va='bottom', fontweight='bold', fontsize='8')

            ax.set_ylabel(y_label, fontweight='bold', fontsize='10', labelpad=10)
            plt.title(title, fontweight='bold', pad=10)
            plt.legend(bbox_to_anchor=(0.5, 0), loc='upper center', ncol=n_bars, shadow=False, frameon=False)
            plt.setp(ax.get_xticklabels(), visible=False)
            ax.tick_params(axis='x', which='both', length=0)
            ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{int(x):,} \u20ac".replace(",", ".")))
            ax.grid(True, linestyle='-', zorder=0, color='#ddd')
            plt.tight_layout()

            plt.savefig(PLOTS_DIR / output_file)
            plt.close()
        # eeg participation maximum
        index = np.arange(1)  # Eine Gruppe
        bar_labels = ['WEA-MAX', 'FFPV-MAX', 'APV-MAX']
        bar_values = [wind_eeg_yearly, pv_eeg_yearly, apv_eeg_yearly]
        bar_width = 0.2
        y_label = 'Einnahmen durch § 6 EEG in €'
        title = 'Jährl. Einnahmen durch § 6 EEG'
        output_file = plot_file_komm_wert_eeg_einnahmen
        bar_colors = [htw_orange, htw_green, htw_blue]

        create_bar_plot(index, bar_labels, bar_values, bar_width, y_label, title, output_file, bar_colors)


        # wind solar euro maximum
        wse_title = 'Jährliche Einnahmen durch Wind- & Solar-Euro'
        wse_output_file = plot_file_einnahmen_wind_solar_euro
        wse_y_label = 'Jährl. Einnahmen Wind-/Solar-Euro in €'
        create_bar_plot(index, bar_labels, [wind_sr_bb_yearly, pv_sr_bb_yearly, apv_sr_bb_yearly], bar_width,
                        wse_y_label, wse_title,
                        wse_output_file, bar_colors)

        ''' 
         Investitionskosten 
         '''

        def calculate_profit_year(title, eeg_anteil_gemeinde, investitionskosten, fremdkapitalanteil, zinshoehe,
                                  tilgungsdauer, jaehrliche_betriebskosten_ersten_10_jahre,
                                  jaehrliche_betriebskosten_ab_11_jahr, erzeugte_energiemenge, preis_pro_mengeneinheit,
                                  steuermessbetrag, hebesatz, freibetrag, tilgungsfreie_jahre, jaehrliche_abschreibung,
                                  abschreibungs_dauer, degradation, initial_loss_carryforward=0):
            # Initiale Berechnungen
            fremdkapital = investitionskosten * fremdkapitalanteil

            if tilgungsfreie_jahre == 1:
                zinsen_jahr_1 = fremdkapital * zinshoehe
                restschuld = fremdkapital
                jaehrliche_tilgung = restschuld / (tilgungsdauer - 2)

            else:
                restschuld = fremdkapital
                jaehrliche_tilgung = restschuld / tilgungsdauer

            kumulierte_kosten = 0
            kumulierte_einnahmen = 0
            kumulierte_jahresgewinne = 0
            jahr = 0
            jahresgewinne = []
            gewerbesteuer_tot = []
            gewerbesteuer = []
            gewinn_start_jahr = None
            total_loss_carryforward = initial_loss_carryforward

            for jahr in range(1, 26):  # Jahre 1 bis 25
                if jahr <= 10:
                    jaehrliche_betriebskosten = jaehrliche_betriebskosten_ersten_10_jahre
                else:
                    jaehrliche_betriebskosten = jaehrliche_betriebskosten_ab_11_jahr

                if jahr > abschreibungs_dauer:
                    jaehrliche_abschreibung = 0

                if jahr == 1:
                    jahresenergieertrag = erzeugte_energiemenge
                    eeg_jahrebetrag = eeg_anteil_gemeinde
                else:
                    jahresenergieertrag = erzeugte_energiemenge * ((1 - degradation) ** jahr)
                    eeg_jahrebetrag = eeg_anteil_gemeinde * ((1 - degradation) ** jahr)

                if jahr == 1 and tilgungsfreie_jahre == 1:
                    jaehrliche_zinsen = zinsen_jahr_1
                    tilgung = 0
                    jahreskosten = jaehrliche_betriebskosten + jaehrliche_zinsen + eeg_jahrebetrag
                elif jahr == 2 and tilgungsfreie_jahre == 1:
                    jaehrliche_zinsen = zinsen_jahr_1
                    tilgung = 0
                    jahreskosten = jaehrliche_betriebskosten + jaehrliche_zinsen + eeg_jahrebetrag
                else:
                    jaehrliche_zinsen = restschuld * zinshoehe
                    tilgung = min(jaehrliche_tilgung, restschuld)
                    restschuld = max(0, restschuld - tilgung)
                    jahreskosten = jaehrliche_betriebskosten + eeg_jahrebetrag + jaehrliche_zinsen

                kumulierte_kosten += jahreskosten
                jaehrliche_einnahmen = jahresenergieertrag * preis_pro_mengeneinheit

                if jaehrliche_einnahmen > 0:
                    kumulierte_einnahmen += jaehrliche_einnahmen

                if jahr <= 2:
                    jaehrlicher_gewinn = jaehrliche_einnahmen - jahreskosten - jaehrliche_abschreibung
                else:
                    jaehrlicher_gewinn = jaehrliche_einnahmen - jahreskosten - jaehrliche_abschreibung

                kumulierte_jahresgewinne += jaehrlicher_gewinn

                if jaehrlicher_gewinn < 0:
                    total_loss_carryforward += -jaehrlicher_gewinn
                    adjusted_profit = 0
                else:
                    adjusted_profit = jaehrlicher_gewinn

                    if total_loss_carryforward > 0 and adjusted_profit > 0:
                        # Bis zu 1 Mio. Verlust abziehen
                        subtracted_loss = min(1_000_000, adjusted_profit, total_loss_carryforward)
                        adjusted_profit -= subtracted_loss
                        total_loss_carryforward -= subtracted_loss

                        # 60% des restlichen Gewinns abziehen
                        if total_loss_carryforward > 0 and total_loss_carryforward > (adjusted_profit * 0.6):
                            extra_loss = adjusted_profit * 0.6
                            total_loss_carryforward -= extra_loss
                            adjusted_profit *= 0.4
                        elif total_loss_carryforward > 0 and total_loss_carryforward < (adjusted_profit * 0.6):
                            extra_loss = total_loss_carryforward
                            total_loss_carryforward -= extra_loss
                            adjusted_profit -= extra_loss

                jahresgewinne.append((jahr, adjusted_profit))

                if adjusted_profit > 0:
                    gewerbesteuer_tot_value = ((adjusted_profit * 0.9) - freibetrag) * steuermessbetrag * hebesatz
                    gewerbesteuer_value = gewerbesteuer_tot_value - (
                            (((adjusted_profit * 0.9) - freibetrag) * steuermessbetrag) * 0.35)
                else:
                    gewerbesteuer_tot_value = 0
                    gewerbesteuer_value = 0

                gewerbesteuer_tot.append((jahr, gewerbesteuer_tot_value))
                gewerbesteuer.append((jahr, gewerbesteuer_value))

                if jaehrlicher_gewinn > 0 and jahr >= 3:
                    if gewinn_start_jahr is None:
                        gewinn_start_jahr = jahr

            return (
                gewinn_start_jahr if gewinn_start_jahr is not None else "kein Gewinn"), jahresgewinne, gewerbesteuer, kumulierte_jahresgewinne

        def prepare_case_data(case_data):
            prepared_data = {}
            for item in case_data:
                # Überprüfen, ob item iterierbar ist und aus Tupeln (Jahr, Wert) besteht
                if isinstance(item, (list, tuple)) and len(item) == 2 and isinstance(item[0], int):
                    year, value = item
                    prepared_data[year] = prepared_data.get(year, 0) + value
                elif isinstance(item, (list, tuple)):
                    for year, value in item:
                        prepared_data[year] = prepared_data.get(year, 0) + value
            return list(prepared_data.items())

        def combine_cases(case_results, szenariennamen):
            combined_results = {i: 0 for i in range(1, 26)}  # Initialisierung für 25 Jahre
            for szenarioname in szenariennamen:
                scenario_results = case_results.get(szenarioname, [])
                for year, val in scenario_results:
                    combined_results[year] += val
            return list(combined_results.items())

        def plot_gewerbesteuer_summe(gewerbesteuer_results, szenariennamen_fuer_summe, title,
                                     filename):
            summierte_gewerbesteuer = [0] * 25  # Initialisierung für 25 Jahre

            # Summiere die Gewerbesteuer über die spezifischen Szenarien
            for szenarioname in szenariennamen_fuer_summe:
                for jahr, steuer in gewerbesteuer_results.get(szenarioname, []):
                    if jahr <= 25:
                        summierte_gewerbesteuer[jahr - 1] += steuer  # Jahr-1 wegen nullbasiertem Index

            # Erstelle die Listen für alle Jahre (1 bis 25)
            jahre = list(range(1, 26))
            steuern = [max(0, summierte_gewerbesteuer[jahr - 1]) for jahr in jahre]

            # Plot der summierten positiven Gewerbesteuerjahre
            figGW, axGW = plt.subplots()
            plt.bar(jahre, steuern, color=htw_green, width=0.9, zorder=2, label='Gewerbesteuereinnahmen')

            plt.xlabel('Jahre', fontweight='bold', fontsize='10', labelpad=10)
            plt.ylabel('Gewerbesteuereinnahmen', fontweight='bold', fontsize='10', labelpad=5)
            plt.title(title, fontweight='bold', pad=10)
            axGW.grid(True, linestyle='-', zorder=0, color='#ddd')
            axGW.ticklabel_format(axis='y', style='plain', useOffset=False)
            axGW.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{int(x):,} €".replace(",", ".")))
            plt.legend(shadow=False)
            plt.xticks(range(1, 26))  # Alle Jahre von 1 bis 25 anzeigen
            plt.tight_layout()
            plt.savefig(PLOTS_DIR / filename)
            plt.close()

        def run_scenario(params, results):
            # Überprüfung der Parameter auf NoneType und Zuweisung von Standardwerten
            berechnete_mw = params.get("berechnete_mw", 0)
            genehmigte_anlagen = params.get("genehmigte_anlagen", 0)
            eeg_beteiligung = params.get("eeg_beteiligung", 0)
            profil = params.get("profil", pd.Series([0]))
            investitionskosten = params.get("investitionskosten", 0)
            betriebskosten10 = params.get("betriebskosten10", 0)
            betriebskosten20 = params.get("betriebskosten20", 0)
            sr_bb_euro = params.get("sr_bb_euro", 0)
            erzeugte_energiemenge = params.get("erzeugte_energiemenge", 0)
            preis_pro_mengeneinheit = params.get("preis_pro_mengeneinheit", 0)
            tilgungsfreie_jahre = params.get("tilgungsfreie_jahre", 0)
            degradation = params.get("degradation", 0)
            title = params.get("title", "Unknown Scenario")

            # Individuelle Berechnungen je nach Szenario
            wind_euro_2026 = berechnete_mw - genehmigte_anlagen if genehmigte_anlagen < berechnete_mw else 0
            investitionskosten = investitionskosten * berechnete_mw
            fremdkapitalanteil = params.get("fremdkapitalanteil", 0.8)  # Standard 80%
            zinshoehe = params.get("zinshoehe", 0.05)  # Standard 5%
            tilgungsdauer = params.get("tilgungsdauer", 15)
            freibetrag = params.get("freibetrag", 0)
            abschreibungs_dauer = params.get("abschreibungs_dauer", 0)

            sr_bb_euro = wind_euro_2026 * sr_bb_euro + ((genehmigte_anlagen / 6) * 10000)
            eeg_anteil_gemeinde = ((profil * berechnete_mw) * eeg_beteiligung).sum()
            jaehrliche_betriebskosten_ersten_10_jahre = betriebskosten10 * berechnete_mw + sr_bb_euro
            jaehrliche_betriebskosten_ab_11_jahr = betriebskosten20 * berechnete_mw + sr_bb_euro
            erzeugte_energiemenge = erzeugte_energiemenge * berechnete_mw
            preis_pro_mengeneinheit = preis_pro_mengeneinheit  # Preis pro kWh in €
            tilgungsfreie_jahre = tilgungsfreie_jahre
            if abschreibungs_dauer != 0:
                jaehrliche_abschreibung = investitionskosten / abschreibungs_dauer
            else:
                jaehrliche_abschreibung = 0
            profit_year, jahresgewinne, gewerbesteuer, kumulierte_jahresgewinne = calculate_profit_year(title,
                                                                                                        eeg_anteil_gemeinde,
                                                                                                        investitionskosten,
                                                                                                        fremdkapitalanteil,
                                                                                                        zinshoehe,
                                                                                                        tilgungsdauer,
                                                                                                        jaehrliche_betriebskosten_ersten_10_jahre,
                                                                                                        jaehrliche_betriebskosten_ab_11_jahr,
                                                                                                        erzeugte_energiemenge,
                                                                                                        preis_pro_mengeneinheit,
                                                                                                        steuermessbetrag,
                                                                                                        hebesatz,
                                                                                                        freibetrag,
                                                                                                        tilgungsfreie_jahre,
                                                                                                        jaehrliche_abschreibung,
                                                                                                        abschreibungs_dauer,
                                                                                                        degradation)

            # Speichern der Gewerbesteuer im Resultate-Dictionary
            results[params["name"]] = gewerbesteuer

        # Gewerbesteuer-Resultate für verschiedene Szenarien speichern
        gewerbesteuer_results = {}

        # Szenarien durchlaufen
        szenarien = [  # Wind 100%
            {"berechnete_mw": wea_p_max, "erzeugte_energiemenge": 2550000,
             "preis_pro_mengeneinheit": 0.0828, "eeg_beteiligung": 2,
             "profil": wind_profile['GHM-wind-onshore-profile'], "sr_bb_euro": 5000,
             "investitionskosten": wea_invest_cost,
             "betriebskosten10": 44000, "betriebskosten20": 53000, "fremdkapitalanteil": 0.8, "zinshoehe": 0.05,
             "tilgungsdauer": 15, "title": "Gewerbesteuer der WEA-MAX",
             "filename": "komm-wert-gwst-anlagenbetreibende-wind100.png", "freibetrag": 0, "tilgungsfreie_jahre": 1,
             "name": 'Wind100', "abschreibungs_dauer": 16, "degradation": 0.006},  # FF-PV 100%
            {"berechnete_mw": pv_p_max, "genehmigte_anlagen": 0, "erzeugte_energiemenge": 1000000,
             "preis_pro_mengeneinheit": 0.073, "eeg_beteiligung": 2,
             "profil": ff_pv_profile['GHM-solar-pv_ground-profile'], "sr_bb_euro": 2000, "investitionskosten": ffpv_invest_costs,
             "betriebskosten10": 14300, "betriebskosten20": 14300, "fremdkapitalanteil": 0.8, "zinshoehe": 0.03,
             "tilgungsdauer": 15, "title": "Gewerbesteuer der FFPV-MAX",
             "filename": "komm-wert-gwst-anlagenbetreibende-ff-pv-100.png", "freibetrag": 24500,
             "tilgungsfreie_jahre": 1, "name": 'FFPV100', "abschreibungs_dauer": 20, "degradation": 0.005},
            # Agri-PV hor. 100%
            {"berechnete_mw": apv_hor_p_max, "genehmigte_anlagen": 0, "erzeugte_energiemenge": apvh_invest_costs,
             "preis_pro_mengeneinheit": 0.088, "eeg_beteiligung": 2,
             "profil": agri_pv_hor_profile['GHM-agri-pv_hor_ground-profile'], "sr_bb_euro": 2000,
             "investitionskosten": 945000, "betriebskosten10": 12870, "betriebskosten20": 12870,
             "fremdkapitalanteil": 0.8, "zinshoehe": 0.03, "tilgungsdauer": 15,
             "title": "Max. Gewerbesteuer der Agri-PV-Anlagen (hor.)",
             "filename": "komm-wert-gwst-anlagenbetreibende-agri-pv-hor-1.png", "freibetrag": 24500,
             "tilgungsfreie_jahre": 1, "name": 'APVH100', "abschreibungs_dauer": 20, "degradation": 0.005},
            # Agri-PV ver. 100%
            {"berechnete_mw": apv_ver_p_max, "genehmigte_anlagen": 0, "erzeugte_energiemenge": apvv_invest_costs,
             "preis_pro_mengeneinheit": 0.088, "eeg_beteiligung": 2,
             "profil": agri_pv_ver_profile['GHM-agri-pv_ver_ground-profile'], "sr_bb_euro": 2000,
             "investitionskosten": 831000, "betriebskosten10": 11440, "betriebskosten20": 11440,
             "fremdkapitalanteil": 0.8, "zinshoehe": 0.03, "tilgungsdauer": 15,
             "title": "Max. Gewerbesteuer der Agri-PV-Anlagen (ver.)",
             "filename": "komm-wert-gwst-anlagenbetreibende-agri-pv-ver-1.png", "freibetrag": 24500,
             "tilgungsfreie_jahre": 1, "name": 'APVV100', "abschreibungs_dauer": 20, "degradation": 0.005},
            # Fügen Sie hier weitere Szenarien hinzu
        ]
        for szenario in szenarien:
            run_scenario(szenario, gewerbesteuer_results)

        # Beispiel: Zusammenrechnung der Gewerbesteuer für spezifische Szenarien
        szenariennamen_fuer_summe_1 = ["FFPV100"]
        szenariennamen_fuer_summe_2 = ["APVV100", "APVH100"]
        szenariennamen_fuer_summe_3 = ["Wind100"]

        def max_annual_sum(gewerbesteuer_results, szenariennamen_fuer_summe):
            summierte_steuern = [0] * 25  # Initialisiere eine Liste für 20 Jahre

            # Summiere die Gewerbesteuer je Jahr über die spezifischen Szenarien hinweg
            for jahr in range(1, 26):
                for szenarioname in szenariennamen_fuer_summe:
                    for j, steuer in gewerbesteuer_results[szenarioname]:
                        if j == jahr:
                            summierte_steuern[jahr - 1] += steuer

            # Finde den maximalen Wert der summierten Gewerbesteuer pro Jahr
            max_steuer = max(summierte_steuern)
            return max_steuer

        gesamt_gewerbesteuer_1 = sum(
            sum(jahressteuer for jahr, jahressteuer in gewerbesteuer_results[szenarioname] if jahressteuer > 0) for
            szenarioname in szenariennamen_fuer_summe_1)

        gesamt_gewerbesteuer_2 = sum(
            sum(jahressteuer for jahr, jahressteuer in gewerbesteuer_results[szenarioname] if jahressteuer > 0) for
            szenarioname in szenariennamen_fuer_summe_2)
        gesamt_gewerbesteuer_3 = sum(
            sum(jahressteuer for jahr, jahressteuer in gewerbesteuer_results[szenarioname] if jahressteuer > 0) for
            szenarioname in szenariennamen_fuer_summe_3)

        plot_file_gewerbesteuer_wind = f'gewerbesteuer-wind_{timestamp}.png'
        plot_file_gewerbesteuer_ff_pv = f'gewerbesteuer-ff-pv_{timestamp}.png'
        plot_file_gewerbesteuer_agri_pv = f'gewerbesteuer-agri-pv_{timestamp}.png'

        plot_gewerbesteuer_summe(gewerbesteuer_results, szenariennamen_fuer_summe_1, "Gewerbesteuereinnahmen FFPV-MAX",
                                 plot_file_gewerbesteuer_ff_pv)
        plot_gewerbesteuer_summe(gewerbesteuer_results, szenariennamen_fuer_summe_2, "Gewerbesteuereinnahmen APV-MAX",
                                 plot_file_gewerbesteuer_agri_pv)
        plot_gewerbesteuer_summe(gewerbesteuer_results, szenariennamen_fuer_summe_3, "Gewerbesteuereinnahmen WEA-MAX",
                                 plot_file_gewerbesteuer_wind)

        def format_numbers(value):
            return f"{value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

        apv_area_income = apvh_area_income + apvv_area_income
        apv_pacht_est = ghm_est_income_apvh + ghm_est_income_apvv
        apv_pacht_gewst = apvh_area_gewst_total + apvv_area_gewst_total

        wind_eeg_yearly = format_numbers(wind_eeg_yearly)
        pv_eeg_yearly = format_numbers(pv_eeg_yearly)
        apv_eeg_yearly = format_numbers(apv_eeg_yearly)
        wind_sr_bb_yearly = format_numbers(wind_sr_bb_yearly)
        pv_sr_bb_yearly = format_numbers(pv_sr_bb_yearly)
        apv_sr_bb_yearly = format_numbers(apv_sr_bb_yearly)
        wea_area_income = format_numbers(wea_area_income)
        pv_area_income = format_numbers(pv_area_income)
        apv_area_income = format_numbers(apv_area_income)
        ghm_est_income_wea = format_numbers(ghm_est_income_wea)
        ghm_est_income_pv = format_numbers(ghm_est_income_pv)
        apv_pacht_est = format_numbers(apv_pacht_est)
        wea_area_gewst_total = format_numbers(wea_area_gewst_total)
        pv_area_gewst_total = format_numbers(pv_area_gewst_total)
        apv_pacht_gewst = format_numbers(apv_pacht_gewst)

        results.update({"wind_eeg_yearly": wind_eeg_yearly,
                   "pv_eeg_yearly": pv_eeg_yearly,
                   "apv_eeg_yearly":apv_eeg_yearly,
                      "wind_sr_bb_yearly":  wind_sr_bb_yearly,
                        "pv_sr_bb_yearly": pv_sr_bb_yearly,
                        "apv_sr_bb_yearly": apv_sr_bb_yearly,
                   "plot_file_komm_wert_jaehrliche_pachteinnahmen": plot_file_komm_wert_jaehrliche_pachteinnahmen,
                   "plot_file_einnahmen_wind_solar_euro": plot_file_einnahmen_wind_solar_euro,
                   "plot_file_komm_wert_eeg_einnahmen": plot_file_komm_wert_eeg_einnahmen,
                        "gesamt_gewerbesteuer_1": gesamt_gewerbesteuer_1,
                        "gesamt_gewerbesteuer_2": gesamt_gewerbesteuer_2,
                        "gesamt_gewerbesteuer_3": gesamt_gewerbesteuer_3,
                        "plot_file_gewerbesteuer_agri_pv": plot_file_gewerbesteuer_agri_pv,
                        "plot_file_gewerbesteuer_ff_pv": plot_file_gewerbesteuer_ff_pv,
                        "plot_file_gewerbesteuer_wind": plot_file_gewerbesteuer_wind,
                        'wea_pachteinnahmen': wea_area_income,
                        'pv_pachteinnahmen': pv_area_income,
                        'apv_pachteinnahmen': apv_area_income,
                        'wea_pacht_est':ghm_est_income_wea,
                        'pv_pacht_est':ghm_est_income_pv,
                        'apv_pacht_est': apv_pacht_est,
                        'wea_pacht_gewst': wea_area_gewst_total,
                        'pv_pacht_gewst': pv_area_gewst_total,
                        'apv_pacht_gewst': apv_pacht_gewst,

                   })

        try:
            json_output = json.dumps(results)
            print(json_output)
        except (TypeError, ValueError) as e:
            print(json.dumps({"status": "error", "message": "Invalid JSON output"}))
            sys.exit(1)

    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()