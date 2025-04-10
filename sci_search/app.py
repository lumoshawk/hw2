from flask import Flask, render_template, request, jsonify
import os
from main import search_scientist, get_publications, save_publications

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    name = request.form.get('name', '')
    
    if not name:
        return jsonify({'error': 'Name is required'})
    
    # Use the updated search_scientist function that returns a list of matches
    scientists = search_scientist(name)
    
    if not scientists:
        return jsonify({'error': 'Scientist not found'})
    
    # If a list is returned, format it for the frontend
    if isinstance(scientists, list):
        return jsonify({
            'multiple': True,
            'scientists': scientists
        })
    else:
        # If a single scientist is returned (for backward compatibility)
        return jsonify(scientists)

@app.route('/select_scientist', methods=['POST'])
def select_scientist():
    name = request.form.get('name', '')
    index = request.form.get('index', '')
    
    if not name:
        return jsonify({'error': 'Name is required'})
    
    if not index.isdigit():
        return jsonify({'error': 'Invalid selection index'})
    
    # Convert index to integer
    index = int(index)
    
    # Get the specific scientist
    scientist = search_scientist(name, index)
    
    if not scientist:
        return jsonify({'error': 'Scientist not found'})
    
    return jsonify(scientist)

@app.route('/publications', methods=['POST'])
def publications():
    url = request.form.get('url', '')
    name = request.form.get('name', '')
    
    if not url or not name:
        return jsonify({'error': 'URL and name are required'})
    
    publications = get_publications(url)
    
    if not publications:
        return jsonify({'error': 'No publications found'})
    
    filepath = save_publications(name, publications, os.path.join(os.path.dirname(__file__), 'data'))
    
    # Group publications by year for display
    by_year = {}
    for pub in publications:
        year = pub.get('year', 'Unknown')
        if year not in by_year:
            by_year[year] = []
        by_year[year].append(pub)
    
    # Order the years
    ordered_pubs = []
    for year in sorted(by_year.keys(), reverse=True):
        ordered_pubs.append({
            'year': year,
            'publications': by_year[year]
        })
    
    return jsonify({
        'publications': ordered_pubs,
        'total': len(publications),
        'filepath': filepath
    })

if __name__ == '__main__':
    # Ensure the data directory exists
    os.makedirs(os.path.join(os.path.dirname(__file__), 'data'), exist_ok=True)
    app.run(debug=True, port=5001)