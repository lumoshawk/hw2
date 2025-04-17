from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
import time
import json

class Property:
    def __init__(self, name="", value="", unit=""):
        self.name = name
        self.value = value
        self.unit = unit
    
class Element:
    def __init__(self, atomic_number, symbol, name, mass, energy_levels, electronegativity, melting_point, boiling_point, electron_affinity, compounds):
        self.atomic_number = Property(name="Atomic Number", value=atomic_number, unit="")
        self.symbol = Property(name="Symbol", value=symbol, unit="")
        self.name = Property(name="Name", value=name, unit="")
        self.mass = Property(name="Mass", value=mass, unit="u")
        self.energy_levels = Property(name="Energy Levels", value=energy_levels, unit="")
        self.electronegativity = Property(name="Electronegativity", value=electronegativity, unit="")
        self.melting_point = Property(name="Melting Point", value=melting_point, unit="°C")
        self.boiling_point = Property(name="Boiling Point", value=boiling_point, unit="°C")
        self.electron_affinity = Property(name="Electron Affinity", value=electron_affinity, unit="kJ/mol")
        self.compounds = Property(name="Common Compounds", value=compounds, unit="")

    units=[]

def interact_with_website(url, click_selector_type, click_selector_value, 
                         read_selector_type, read_selector_value, timeout=10):
    """
    Fetch a dynamic website, click on element A, read value from element B, and print both.
    
    Args:
        url: The website URL to navigate to
        click_selector_type: The attribute type to find element A (id, class, xpath, css, data-*)
        click_selector_value: The value of the attribute for element A
        read_selector_type: The attribute type to find element B 
        read_selector_value: The value of the attribute for element B
        timeout: Maximum time to wait for elements in seconds
        
    Returns:
        tuple: (clicked element text, read element text, compounds)
    """
    # 无头模式， 无窗口
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--disable-gpu")  
    chrome_options.add_argument("--no-sandbox")  
    chrome_options.add_argument("--disable-dev-shm-usage")  
    
    # 初始化 WebDriver 
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # 打开URL
        driver.get(url+'#Properties')
        
        # 等待可点击并选择该元素
        click_element = None
        if click_selector_type.lower() == "id":
            click_element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.ID, click_selector_value))
            )
        elif click_selector_type.lower() == "class":
            click_element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.CLASS_NAME, click_selector_value))
            )
        elif click_selector_type.lower() == "xpath":
            click_element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, click_selector_value))
            )
        elif click_selector_type.lower() == "css":
            click_element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, click_selector_value))
            )
        # Handle data-* attributes through CSS selectors
        elif click_selector_type.lower():
            data_attribute = click_selector_type.lower()
            css_selector = f"[{data_attribute}='{click_selector_value}']"
            click_element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
            )
        else:
            raise ValueError(f"Unsupported click selector type: {click_selector_type}")
        
        click_element_text = click_element.text
        
        element_lines = click_element_text.strip().split('\n')
        element_symbol = element_lines[1] if len(element_lines) > 1 else ""
        
        # Click the element
        click_element.click()
        
        # Give time for JavaScript to update the page content after click
        # 定位 read element
        read_element = None
        if read_selector_type.lower() == "id":
            read_element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.ID, read_selector_value))
            )
        elif read_selector_type.lower() == "class":
            read_element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, read_selector_value))
            )
        elif read_selector_type.lower() == "xpath":
            read_element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, read_selector_value))
            )
        elif read_selector_type.lower() == "css":
            read_element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, read_selector_value))
            )
        elif read_selector_type.lower():
            data_attribute = read_selector_type.lower()
            css_selector = f"[{data_attribute}='{read_selector_value}']"
            read_element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
            )
        else:
            raise ValueError(f"Unsupported read selector type: {read_selector_type}")
        
        #确保内容已全部更新完成
        # Get initial content to compare for changes
        initial_content = read_element.text
        
        # Wait for content to change or stabilize (up to 5 seconds)
        max_wait = 5
        start_time = time.time()
        content_stabilized = False
        
        while time.time() - start_time < max_wait and not content_stabilized:
            time.sleep(0.5)  # Check every 500ms
            current_content = read_element.text
            
            # If content has changed from initial empty state or hasn't changed in the last check
            if (initial_content == "" and current_content != "") or (current_content != "" and current_content == initial_content):
                content_stabilized = True
            else:
                initial_content = current_content
        
        read_element_text = read_element.text
        
        # Extract compounds containing the element
        driver.get(url+'#Compounds')
        # compounds = extract_compounds(driver, element_symbol)
        
        compounds = fetch_formatted_compounds(element_symbol)
        # Format and print the element data in an organized way
        formatted_data = format_element_data(click_element_text, read_element_text, compounds)
        
        return (click_element_text, read_element_text, compounds)
    
    except TimeoutException:
        print("Timed out waiting for elements to load")
        return (None, None, None)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return (None, None, None)
    finally:
        # Always close the driver to avoid orphaned browser instances
        driver.quit()

def format_element_data(element_text, data_text, compounds=None):
    """
    Format the element data in a structured way with key=value unit format.
    
    Args:
        element_text: Text from the clicked element (atomic number, symbol, name, mass)
        data_text: Raw text data from the data region
        compounds: List of compounds containing the element (optional)
        
    Returns:
        Element: Element object with all properties
    """
    if not data_text:
        return "No data available"
    
    # 元素基本信息
    element_lines = element_text.strip().split('\n')
    atomic_number = element_lines[0] if len(element_lines) > 0 else ""
    symbol = element_lines[1] if len(element_lines) > 1 else ""
    name = element_lines[2] if len(element_lines) > 2 else ""
    mass = element_lines[3] if len(element_lines) > 3 else ""
    
    
    element_data = {
        "Number": atomic_number,
        "Symbol": symbol,
        "Name": name,
        "Mass": mass,
    }
    
    # 处理属性信息
    lines = data_text.strip().split('\n')
   
    
    looking_element = Element(
        atomic_number=element_data["Number"],
        symbol=element_data["Symbol"],
        name=element_data["Name"],
        mass=element_data["Mass"],
        energy_levels="",
        electronegativity="",
        melting_point="",
        boiling_point="",
        electron_affinity="",
        compounds=compounds,
    )
    for i, line in enumerate(lines):
        if "Energy levels" in line:
            looking_element.energy_levels = Property(name="Energy Levels", value=lines[i + 1], unit="")
        elif "Electronegativity" in line:
            looking_element.electronegativity = Property(name="Electronegativity", value=lines[i + 1], unit="")
        elif "Melting point" in line:
            looking_element.melting_point = Property(name="Melting Point", value=lines[i + 1], unit="Celsius")
        elif "Boiling point" in line:
            looking_element.boiling_point = Property(name="Boiling Point", value=lines[i + 1], unit="Celsius")
        elif "Electron affinity" in line:
            looking_element.electron_affinity = Property(name="Electron Affinity", value=lines[i + 1], unit="kJ/mol")
    
    # # Add compounds to the element if provided
    # if compounds:
    #     looking_element.compounds = Property(name="Common Compounds", value=compounds, unit="")
    
    return looking_element

import requests

def fetch_formatted_compounds(formula):
    """
    Fetch compound info from ptable and return formatted list like 'AgBr; silver bromide'.
    
    Args:
        formula (str): Chemical formula to search for, e.g., "AgBr", "Ag"
    
    Returns:
        list of str: List of 'formula; primary name' strings
    """
    url = f"https://ptable.com/JSON/compounds/formula={formula}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        compounds = []
        for match in data.get("matches", []):
            molecular_formula = match.get("molecularformula", "")
            all_names = match.get("allnames", [])
            primary_name = all_names[0] if all_names else "(no name)"
            compounds.append(f"{molecular_formula}: {primary_name}")

        return compounds

    except Exception as e:
        print(f"Error: {e}")
        return []

def extract_compounds(driver, element_symbol, limit=5):
    """
    Extract compounds containing the specified element from the CompoundResults section.
    
    Args:
        driver: The WebDriver instance
        element_symbol: The symbol of the element to search compounds for
        limit: Maximum number of compounds to return
        
    Returns:
        list: List of compound formulas containing the element
    """
    try:
        # # 选择CompoundResults section 
        # compound_list = WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.ID, "CompoundResults"))
        # )
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//ul[@id='CompoundResults']"))
             )

        # Get updated list of compounds
        # Retry mechanism to ensure compound list is populated
        max_retries = 10
        retry_count = 0
        compound_list = []

        while retry_count < max_retries and not compound_list:
            compound_list = driver.find_elements(By.CSS_SELECTOR, "#DataRegion #CompoundResults li")
            if not compound_list:
                time.sleep(0.1)  # Wait for 1 second before retrying
                retry_count += 1
        compound_items=[]
        
        for compound in compound_list:
            compound_items.append(compound)    
            print(compound.text)
           
        # Extract compounds containing the element
        looking_compounds = []
        for item in compound_items:
            try:
                label_element = element_symbol
                if label_element:
                    formula = item.text
                    # Check if the compound contains the element symbol
                    if label_element in formula:
                        looking_compounds.append(formula)
                        if len(looking_compounds) >= limit:
                            break
            except Exception:
                # Skip if any error occurs processing this item
                continue
                
        return looking_compounds
        
    except Exception as e:
        print(f"Error extracting compounds: {str(e)}")
        return []

def symbol_to_atomic(symbol):
    """
    Given an element symbol (case-insensitive), return the atomic number as a string.
    Returns None if not found.
    """
    symbol = symbol.capitalize()
    symbol_to_atomic_map = {
        'H': 1, 'He': 2, 'Li': 3, 'Be': 4, 'B': 5, 'C': 6, 'N': 7, 'O': 8, 'F': 9, 'Ne': 10,
        'Na': 11, 'Mg': 12, 'Al': 13, 'Si': 14, 'P': 15, 'S': 16, 'Cl': 17, 'Ar': 18, 'K': 19, 'Ca': 20,
        'Sc': 21, 'Ti': 22, 'V': 23, 'Cr': 24, 'Mn': 25, 'Fe': 26, 'Co': 27, 'Ni': 28, 'Cu': 29, 'Zn': 30,
        'Ga': 31, 'Ge': 32, 'As': 33, 'Se': 34, 'Br': 35, 'Kr': 36, 'Rb': 37, 'Sr': 38, 'Y': 39, 'Zr': 40,
        'Nb': 41, 'Mo': 42, 'Tc': 43, 'Ru': 44, 'Rh': 45, 'Pd': 46, 'Ag': 47, 'Cd': 48, 'In': 49, 'Sn': 50,
        'Sb': 51, 'Te': 52, 'I': 53, 'Xe': 54, 'Cs': 55, 'Ba': 56, 'La': 57, 'Ce': 58, 'Pr': 59, 'Nd': 60,
        'Pm': 61, 'Sm': 62, 'Eu': 63, 'Gd': 64, 'Tb': 65, 'Dy': 66, 'Ho': 67, 'Er': 68, 'Tm': 69, 'Yb': 70,
        'Lu': 71, 'Hf': 72, 'Ta': 73, 'W': 74, 'Re': 75, 'Os': 76, 'Ir': 77, 'Pt': 78, 'Au': 79, 'Hg': 80,
        'Tl': 81, 'Pb': 82, 'Bi': 83, 'Po': 84, 'At': 85, 'Rn': 86, 'Fr': 87, 'Ra': 88, 'Ac': 89, 'Th': 90,
        'Pa': 91, 'U': 92, 'Np': 93, 'Pu': 94, 'Am': 95, 'Cm': 96, 'Bk': 97, 'Cf': 98, 'Es': 99, 'Fm': 100,
        'Md': 101, 'No': 102, 'Lr': 103, 'Rf': 104, 'Db': 105, 'Sg': 106, 'Bh': 107, 'Hs': 108, 'Mt': 109,
        'Ds': 110, 'Rg': 111, 'Cn': 112, 'Fl': 114, 'Lv': 116, 'Ts': 117, 'Og': 118
    }
    atomic = symbol_to_atomic_map.get(symbol)
    return str(atomic) if atomic else None

# Remove the automatic execution code and replace with a main function
def main():
    element_atomic=symbol_to_atomic(input("Enter element symbol: "))
    if element_atomic:
        interact_with_website(
            url="https://ptable.com/", 
            click_selector_type="data-atomic", 
            click_selector_value=element_atomic, 
            read_selector_type="id", 
            read_selector_value="DataRegion"
        )
    else:
        print("Element not found.")

# Only run if this script is executed directly (not imported)
if __name__ == "__main__":
    main()