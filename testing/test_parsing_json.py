import os
import sys
import json
import testhelper

sys.path.append(os.path.join(testhelper.TESTDIR, '..'))
import OPRDatacard  # nopep8

armyBookHdf = testhelper.readJsonFile(os.path.join(testhelper.TESTDATADIR, 'armybook_hdf_3.json'))


def test_addEquipment():
    upgrade = armyBookHdf["upgradePackages"][0]["sections"][0]["options"][0]
    upgrade = "Forward Observer"

    for upgradePackages in armyBookHdf["upgradePackages"]:
        for section in upgradePackages['sections']:
            for option in section['options']:
                if option['gains'][0]['name'].lower() == upgrade.lower():
                    gains = option['gains'][0]
                    break

    result = OPRDatacard.addEquipment(gains)
    expected = {'name': 'Forward Observer', 
                    'specialRules': [
                        {'key': 'take aim', 
                        'name': 'Take Aim', 
                        'type': 'ArmyBookRule', 
                        'label': 'Take Aim', 
                        'modify': False, 
                        'rating': ''
                        }
                    ]
                }

    assert result['name'] == "Forward Observer"
    assert len(result['specialRules']) == 1
    assert result['specialRules'][0]['key'] == "take aim"
    assert result['specialRules'][0]['name'] == "Take Aim"
    assert result['specialRules'][0]['label'] == "Take Aim"
    assert type(result['specialRules'][0]['rating']) == str
    assert result == expected


def test_getSpecialRules_Weapons():
    testCases = [
        {'unit': 'Company Leader', 'equipment': 'Master Rifle', 
            'expected': []},
        {'unit': 'Storm Leader', 'equipment': 'Master Heavy Rifle', 
            'expected': [{'key': 'ap', 'name': 'AP', 'rating': '1', 'modify': False, 'label': 'AP(1)'}]},
        {'unit': 'Cavalry', 'equipment': 'Hunting Lance', 
            'expected': [{'key': 'ap', 'name': 'AP', 'rating': '1', 'modify': False, 'label': 'AP(1)'}, {'key': 'lance', 'name': 'Lance', 'rating': '', 'modify': False, 'label': 'Lance'}]},

    ]

    units = armyBookHdf["units"]
    
    for test in testCases:
        specialRules = None
        for unit in units:
            if unit['name'].lower() == test['unit'].lower():
                for equipment in unit['equipment']:
                    if equipment['name'].lower() == test['equipment'].lower():
                        specialRules = equipment['specialRules']
                        break
            if specialRules is not None:
                break
        
        result = OPRDatacard.getSpecialRules(specialRules)
        assert result == test['expected'], "Test for unit " + str(test['unit']) + " equipment " + str(test['equipment'])

def test_getWeapon():
    testCases = [
        {'unit': 0, 'equipment': 1, 'expected': {'attacks': 1, 'name': 'Rifle', 'range': 24, 'specialRules': [], 'count': 1}},
        {'unit': 1, 'equipment': 1, 'expected': {'attacks': 1, 'name': 'Heavy Rifle',
                                                 'range': 24, 'specialRules': [], 'ap': '1', 'count': 1}},
        {'unit': 4, 'equipment': 1, 'expected': {'attacks': 1, 'name': 'Plasma Rifle',
                                                 'range': 24, 'specialRules': [], 'ap': '4', 'count': 1}},
        {'unit': 8, 'equipment': 1, 'expected': {'attacks': 1, 'name': 'Mortar', 'range': 30, 'specialRules': [
            {'key': 'blast', 'name': 'Blast', 'rating': '3', 'modify': False, 'label': 'Blast(3)'}, {'key': 'indirect', 'name': 'Indirect', 'rating': '', 'modify': False, 'label': 'Indirect'}], 'count': 1}},
        {'unit': 9, 'equipment': 1, 'expected': {'attacks': 1, 'name': 'Sniper Rifle', 'range': 30, 'specialRules': [
            {'key': 'sniper', 'name': 'Sniper', 'rating': '', 'modify': False, 'label': 'Sniper'}], 'ap': '1', 'count': 1}},
        {'unit': 10, 'equipment': 1, 'expected': {'attacks': 1, 'name': 'Mini GL', 'range': 18, 'specialRules': [
            {'key': 'blast', 'name': 'Blast', 'rating': '3', 'modify': False, 'label': 'Blast(3)'}], 'count': 1}},
    ]

    for test in testCases:
        weapon = armyBookHdf["units"][test['unit']]["equipment"][test['equipment']]
        result = OPRDatacard.getWeapon(weapon)
        assert result == test['expected'], "Test for unit " + str(test['unit']) + " equipment " + str(test['equipment'])


def test_removeWeapon():
    weapons = [{'name': 'CCW', 'count': 1}, {'name': 'Heavy Rifle', 'count': 1}, {
        'name': 'Heavy Pistol', 'count': 1}, {'name': 'CCWs', 'count': 1}, {'name': 'Grenades', 'count': 2}]
    testCases = [
        {'remove': [], 'count': 1, 'expected': [
            {'name': 'CCW', 'count': 1}, {'name': 'Heavy Rifle', 'count': 1}, {'name': 'Heavy Pistol',
                                                                               'count': 1}, {'name': 'CCWs', 'count': 1}, {'name': 'Grenades', 'count': 2}
        ]},
        {'remove': ['CCW'], 'count': 1, 'expected': [
            {'name': 'Heavy Rifle', 'count': 1}, {
                'name': 'Heavy Pistol', 'count': 1}, {'name': 'CCWs', 'count': 1}, {'name': 'Grenades', 'count': 2}
        ]},
        {'remove': ['Heavy Pistol'], 'count': 1, 'expected': [
            {'name': 'CCW', 'count': 1}, {'name': 'Heavy Rifle', 'count': 1}, {
                'name': 'CCWs', 'count': 1}, {'name': 'Grenades', 'count': 2}
        ]},
        {'remove': ['Some'], 'count': 1, 'expected': [
            {'name': 'CCW', 'count': 1}, {'name': 'Heavy Rifle', 'count': 1}, {
                'name': 'Heavy Pistol', 'count': 1}, {'name': 'CCWs', 'count': 1}, {'name': 'Grenades', 'count': 2}
        ]},
        {'remove': ['CCW', 'Heavy Rifle'], 'count': 1, 'expected': [
            {'name': 'Heavy Pistol',
             'count': 1}, {'name': 'CCWs', 'count': 1}, {'name': 'Grenades', 'count': 2}
        ]},
        {'remove': ['CCW', 'CCW'], 'count': 1, 'expected': [
            {'name': 'Heavy Rifle', 'count': 1},
            {'name': 'Heavy Pistol', 'count': 1}, {'name': 'Grenades', 'count': 2}
        ]},
        {'remove': ['Grenade'], 'count': 1, 'expected': [
            {'name': 'CCW', 'count': 1}, {'name': 'Heavy Rifle', 'count': 1}, {
                'name': 'Heavy Pistol', 'count': 1}, {'name': 'CCWs', 'count': 1}, {'name': 'Grenades', 'count': 1}
        ]},
        {'remove': ['Grenade'], 'count': 1, 'expected': [
            {'name': 'CCW', 'count': 1}, {'name': 'Heavy Rifle', 'count': 1}, {
                'name': 'Heavy Pistol', 'count': 1}, {'name': 'CCWs', 'count': 1}
        ]},
        {'remove': ['Heavy Pistols', 'CCW'], 'count': 1, 'expected': [
            {'name': 'Heavy Rifle', 'count': 1}, {'name': 'CCWs', 'count': 1}, {'name': 'Grenades', 'count': 1}
        ]},
    ]

    for test in testCases:
        result = OPRDatacard.removeWeapon(test['remove'], test['count'], weapons.copy())
        assert result == test['expected'], "Weapon remove error for: " + ", ". join(test['remove'])


def test_getUnitUpgrades():
    book = {}
    book['TestArmyId'] = armyBookHdf
    unitFromList = {'id': "dwJg2Bu", "armyId": "TestArmyId", "selectedUpgrades": []}
    result = OPRDatacard.getUnitUpgrades(unitFromList, {'size': 1, 'weapons': []}, book)
    assert result == {'size': 1, 'weapons': []}, "No upgrades"

    unitFromList = {'id': "dwJg2Bu", "armyId": "TestArmyId", "selectedUpgrades": [
        {"instanceId": "oM5IcF6CY", "upgradeId": "biu0sem", "optionId": "uG08OTq"}]}
    expected = {'size': 1, 'weapons': [{'attacks': 1, 'count': 1, 'name': 'Heavy Pistol',
                                        'range': 12, 'specialRules': [], 'ap': '1'}], 'upgradeCost': [0]}
    result = OPRDatacard.getUnitUpgrades(unitFromList, {'size': 1, 'weapons': []}, book)
    assert result == expected, "Upgrade Heavy Pistol"

    unitFromList = {'id': "dwJg2Bu", "armyId": "TestArmyId", "selectedUpgrades": [
        {"instanceId": "oM5IcF6CY", "upgradeId": "biu0sem", "optionId": "uG08OTq"}, {"instanceId": "QrSaPfNsR", "upgradeId": "KLO_Oyg", "optionId": "8TLlvtc"}, {"instanceId": "29BbXH9Me", "upgradeId": "r5XpHsA", "optionId": "8reDsp0"}]}
    expected = {'size': 1, 'weapons': [{'attacks': 1, 'count': 1, 'name': 'Plasma Pistol', 'range': 12, 'specialRules': [], 'ap': '4'}], 'upgradeCost': [0, 5, 35], 'equipment': [
        {'name': 'Forward Observer', 'specialRules': [{'key': 'take aim', 'name': 'Take Aim', 'type': 'ArmyBookRule', 'label': 'Take Aim', 'modify': False, 'rating': ''}]}]}
    result = OPRDatacard.getUnitUpgrades(unitFromList, {'size': 1, 'weapons': []}, book)
    assert result == expected, "3 Upgrades to (Heavy Pistol, than to Plasma and Take Aim)"


def test_getUnit():
    book = {}
    book['TestArmyId'] = armyBookHdf

    unitFromList = {'id': "dwJg2Bu", "armyId": "TestArmyId", "selectedUpgrades": []}
    result = OPRDatacard.getUnit(unitFromList, book)
    assert result['type'] == 'Storm Leader'
    assert result['name'] == 'Storm Leader'
    assert result['defense'] == 4
    assert result['quality'] == 4
    assert len(result['weapons']) == 2
    assert len(result['specialRules']) == 3
    assert len(result['specialRules']) == 3


def test_unitWithManyUpgrades():
    result = OPRDatacard.parseArmyJsonList(os.path.join(testhelper.TESTDATADIR, 'gf_many_upgrades.json'))
    expected = testhelper.readJsonFile(os.path.join(testhelper.TESTDATADIR, 'gf_many_upgrades_expected.json'))
    assert result == expected
    try:
        OPRDatacard.createDataCard(result)
        assert True
    except Exception:
        assert False, "Error in createDataCard"

def test_gff_hdf():
    result = OPRDatacard.parseArmyJsonList(os.path.join(testhelper.TESTDATADIR, 'army_list_gff_hdf.json'))
    expected = testhelper.readJsonFile(os.path.join(testhelper.TESTDATADIR, 'army_list_gff_hdf_expected.json'))
    assert result == expected
    try:
        OPRDatacard.createDataCard(result)
        assert True
    except Exception:
        assert False, "Error in createDataCard"

def test_gf_pb():
    result = OPRDatacard.parseArmyJsonList(os.path.join(testhelper.TESTDATADIR, 'army_list_gf_pb.json'))
    expected = testhelper.readJsonFile(os.path.join(testhelper.TESTDATADIR, 'army_list_gf_pb_expected.json'))
    assert result == expected
    try:
        OPRDatacard.createDataCard(result)
        assert True
    except Exception:
        assert False, "Error in createDataCard"

def test_gff_prime_brothers():
    result = OPRDatacard.parseArmyJsonList(os.path.join(testhelper.TESTDATADIR, 'army_list_gff_prime_brothers.json'))
    expected = testhelper.readJsonFile(os.path.join(
        testhelper.TESTDATADIR, 'army_list_gff_prime_brothers_expected.json'))
    assert result == expected
    try:
        OPRDatacard.createDataCard(result)
        assert True
    except Exception:
        assert False, "Error in createDataCard"

def test_gf_pb():
    result = OPRDatacard.parseArmyJsonList(os.path.join(testhelper.TESTDATADIR, 'army_list_gff_feudal_guard.json'))
    expected = testhelper.readJsonFile(os.path.join(testhelper.TESTDATADIR, 'army_list_gff_feudal_guard_expected.json'))
    assert result == expected
    try:
        OPRDatacard.createDataCard(result)
        assert True
    except Exception:
        assert False, "Error in createDataCard"

def test_gff_hb():
    result = OPRDatacard.parseArmyJsonList(os.path.join(testhelper.TESTDATADIR, 'army_list_gff_hb.json'))
    expected = testhelper.readJsonFile(os.path.join(testhelper.TESTDATADIR, 'army_list_gff_hb_expected.json'))
    assert result == expected
    try:
        OPRDatacard.createDataCard(result)
        assert True
    except Exception:
        assert False, "Error in createDataCard"