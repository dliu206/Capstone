from flask import Flask, render_template, request, jsonify
import cap, geo
from blocks import main_blocks, info_blocks

app = Flask(__name__)
app.static_folder = 'static'

frames_list = list()
info_list = ['name', 'formatted_address', 'price_level', 'rating', 'map_url']

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        vals = request.form.getlist('choice')
        vals = [int(i) for i in vals]
        rules_vals = list(cap.predict(vals))
        return render_template('interests.html', len=len(rules_vals), interests=rules_vals, choices=main_blocks.choices, title='Interests')
    return render_template('main.html', len=len(info_blocks.choices), choices=info_blocks.choices, category=info_blocks.categories, color=info_blocks.colors)

@app.route('/Info')
def info():
    return render_template('info.html', title='Info')

@app.route('/Related')
def related():
    selected_interest = request.args.get('type')
    geo_data = geo.get_maps(geo.get_google_data(selected_interest))
    return render_template('related.html', len = len(geo_data), data=geo_data, selected=selected_interest, info=info_list, title='Related')