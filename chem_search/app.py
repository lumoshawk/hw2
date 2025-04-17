from flask import Flask, render_template, request, jsonify, session
import json
import os
import sys
from chem_search import symbol_to_atomic, interact_with_website, Element, format_element_data

# Get the current directory where this script is located
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Define the elements directory path
ELEMENTS_DIR = os.path.join(CURRENT_DIR, 'elements')

app = Flask(__name__)
app.secret_key = 'element_search_secret_key'  # Required for session

@app.route('/')
def index():
    # Initialize session if not already done
    if 'search_history' not in session:
        session['search_history'] = []
    
    # Render the form with any previous search history
    return render_template('index.html', search_history=session['search_history'])

@app.route('/search', methods=['POST'])
def search():
    element_symbol = request.form.get('element_symbol', '').strip()
    
    # Initialize session if not already done
    if 'search_history' not in session:
        session['search_history'] = []
    
    if not element_symbol:
        return render_template('index.html', error='No element symbol provided', search_history=session['search_history'])
    
    # Convert symbol to atomic number
    element_atomic = symbol_to_atomic(element_symbol)
    
    if not element_atomic:
        return render_template('index.html', error=f'Element "{element_symbol}" not found', 
                              element_symbol=element_symbol, search_history=session['search_history'])
    
    # Check for cached data
    os.makedirs(ELEMENTS_DIR, exist_ok=True)
    json_file_path = os.path.join(ELEMENTS_DIR, f'{element_symbol.capitalize()}.json')
    if os.path.exists(json_file_path):
        try:
            with open(json_file_path, 'r') as f:
                element_data_json = json.load(f)
                # Add to search history only if not already present
                if not any(item.get('symbol', {}).get('value') == element_data_json['symbol']['value'] 
                           for item in session['search_history']):
                    session['search_history'].insert(0, element_data_json)
                    session.modified = True
                
                return render_template('index.html', 
                                       element_data=element_data_json, 
                                       element_symbol=element_symbol,
                                       search_history=session['search_history'])
        except Exception as e:
            print(f"Error reading cached data: {e}")
    
    try:
        # Use the existing function to get element data
        clicked_text, data_text, compounds = interact_with_website(
            url="https://ptable.com/?lang=en#Properties", 
            click_selector_type="data-atomic", 
            click_selector_value=element_atomic, 
            read_selector_type="id", 
            read_selector_value="DataRegion"
        )
        
        # Check if we got valid data
        if not clicked_text or not data_text:
            return render_template('index.html', error='Failed to retrieve element data', 
                                  element_symbol=element_symbol, search_history=session['search_history'])
        
        # Format the data using the existing function
        element_data = format_element_data(clicked_text, data_text, compounds)
        
        try:
            # Save data to a JSON file for caching
            with open(json_file_path, 'w') as f:
                json.dump(element_data, f, default=lambda o: o.__dict__, indent=2)
        except Exception as e:
            print(f"Error caching data: {e}")
        
        # Add to search history only if not already present
        element_dict = json.loads(json.dumps(element_data, default=lambda o: o.__dict__))
        if not any(item.get('symbol', {}).get('value') == element_dict['symbol']['value'] 
                   for item in session['search_history']):
            session['search_history'].insert(0, element_dict)
            session.modified = True
        
        return render_template('index.html', 
                               element_data=element_data, 
                               element_symbol=element_symbol,
                               search_history=session['search_history'])
    except Exception as e:
        return render_template('index.html', error=f'Error: {str(e)}', 
                              element_symbol=element_symbol, search_history=session['search_history'])

if __name__ == '__main__':
    # Run the app on port 5004
    app.run(debug=True, port=5004)