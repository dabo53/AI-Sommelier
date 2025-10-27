import pandas as pd

data = {
    'Steak': [
        'Argentinisches Entrecôte (Rib Eye)', 
        'US Prime Delmonico Rib Eye', 
        'Argentinisches Filet', 
        'US Prime Tenderloin Filet', 
        'Spanisches Iberico Filet', 
        'Neuseeländisches Weidelamm-Filet', 
        'Argentinisches Rumpsteak', 
        'US Prime New York Strip (Rumpsteak)', 
        'Argentinisches Hüftsteak', 
        'US Prime Hüftsteak', 
        'US Prime Flank Steak', 
        'US Prime Hacksteak vom Wagyu Rind', 
        'US Prime Medaillon aus dem Striploin', 
        'Spanische Iberico Steaks'
    ],
    'Klassische Steakbezeichnung': [
        'Ribeye', 
        'Ribeye', 
        'Filet', 
        'Filet', 
        'Filet', 
        'Filet', 
        'Strip', 
        'Strip', 
        'Rump', 
        'Rump', 
        'Flank', 
        'Zusätzliche Cuts', 
        'Zusätzliche Cuts', 
        'Zusätzliche Cuts'
    ],
    'Herkunft': [
        'Argentinien', 
        'USA', 
        'Argentinien', 
        'USA', 
        'Spanien', 
        'Neuseeland', 
        'Argentinien', 
        'USA', 
        'Argentinien', 
        'USA', 
        'USA', 
        'USA', 
        'USA', 
        'Spanien'
    ]
}

df = pd.DataFrame(data)

def test_ribeye_mapping():
    ribeye_steaks = df[df['Klassische Steakbezeichnung'] == 'Ribeye']
    assert len(ribeye_steaks) == 2
    assert set(ribeye_steaks['Herkunft']) == {'Argentinien', 'USA'}

def test_filet_mapping():
    filet_steaks = df[df['Klassische Steakbezeichnung'] == 'Filet']
    assert len(filet_steaks) == 4
    assert set(filet_steaks['Herkunft']) == {'Argentinien', 'USA', 'Spanien', 'Neuseeland'}

def test_strip_mapping():
    strip_steaks = df[df['Klassische Steakbezeichnung'] == 'Strip']
    assert len(strip_steaks) == 2
    assert set(strip_steaks['Herkunft']) == {'Argentinien', 'USA'}

def test_rump_mapping():
    rump_steaks = df[df['Klassische Steakbezeichnung'] == 'Rump']
    assert len(rump_steaks) == 2
    assert set(rump_steaks['Herkunft']) == {'Argentinien', 'USA'}

def test_additional_cuts():
    additional_cuts = df[df['Klassische Steakbezeichnung'] == 'Zusätzliche Cuts']
    assert len(additional_cuts) == 3
    assert set(additional_cuts['Herkunft']) == {'USA', 'Spanien'}

def run_all_tests():
    test_ribeye_mapping()
    test_filet_mapping()
    test_strip_mapping()
    test_rump_mapping()
    test_additional_cuts()
    print("Alle Tests erfolgreich bestanden!")

run_all_tests()
print(df)