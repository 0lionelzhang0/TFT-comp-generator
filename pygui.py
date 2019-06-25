import PySimpleGUI as sg
import comp_generator as cg
import json

with open('heros.json') as json_file:
    allHeros = json.load(json_file)

hero_checkboxes = []
col = 5
count = 0
line = []
allHeros = sorted(allHeros)
for h in allHeros:
    if count == col:
        hero_checkboxes.append(line)
        line = []
        count = 0

    line.append(sg.Checkbox(h, key=h))
    count += 1
    # else:
    #     hero_checkboxes.append(line)
    #     line = []
    #     line.append(sg.Checkbox())
    #     count = 0
else:
    hero_checkboxes.append(line)

layout = [[sg.Text('Number of units in team'), sg.Input('3', size=(3,1), key='num_units')],
    [sg.Text('Number of comps to display'), sg.Input('10', size=(3,1), key='num_comps_to_display')],
    [sg.Text('Max cost of unit'), sg.Input('5', size=(3,1), key='max_cost')],
    [sg.Button('Reset Heros', key='RESET')]]

layout += hero_checkboxes
layout.append([sg.Button('Generate comps', key='GENERATE COMPS'), sg.Checkbox('Show synergies', key='show_synergies')])

w = sg.Window('Comp Generator v1.0').Layout(layout)

comp_gen = cg.CompGenerator('tft')
while True:
    event, values = w.Read()

    if event == None:
        break
    
    if event == "RESET":
        for h in allHeros:
            w.FindElement(h).Update(False)
    if event == "GENERATE COMPS":
        num = int(values['num_units'])
        max_cost = int(values['max_cost'])
        num_to_display = int(values['num_comps_to_display'])
        show_synergies = values['show_synergies']

        selected_heros = []
        for h in allHeros:
            if values[h]:
                selected_heros.append(h)

        warning_thresh = num - len(selected_heros)
        if (warning_thresh>4):
            warning = f"Calculation may take long time. Recommended to keep number of units in team at most 4 greater than number of selected units (current = {warning_thresh}). Continue anyways?"
            if (sg.PopupYesNo(warning) != "Yes"):
                continue

        comp_gen.generate_best_comps(selected_heros, max_cost, num)
        bc = comp_gen.get_best_comps().get_comp_list()

        if num_to_display > len(bc):
            num_to_display = len(bc)
        output_text = ''
        
        for i in range(num_to_display):
            c = bc[i]
            output_text += str(c.get_heros())
            output_text += str(comp_gen.get_costs_of_comp(c))
            output_text += str(c.get_total_synergy())
            output_text += '\n'
            if show_synergies:
                ss = c.get_synergy_scores()
                for c in ss['class']:
                    score = ss['class'][c]
                    if score:
                        output_text += f"{c} {score} \n"
                for o in ss['origin']:
                    score = ss['origin'][o]
                    if score:
                        output_text += f"{o} {score} \n"                
            output_text += '\n'

        sg.PopupScrolled(output_text)