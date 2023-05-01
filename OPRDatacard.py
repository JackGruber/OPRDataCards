import io
import platform
import subprocess
from PIL import Image, ImageDraw
from reportlab.lib import utils
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
import sys
import os
import urllib.request
import time
import stat
import json
import re
# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    BASEPATH = os.path.dirname(sys.executable)
elif __file__:
    BASEPATH = os.path.dirname(__file__)

DATAFOLDER = os.path.join(BASEPATH, "data")
DATAFOLDERARMYBOOK = os.path.join(DATAFOLDER, "armybook")
FONTFOLDER = os.path.join(DATAFOLDER, "fonts")
DATACARDPDF = os.path.join(DATAFOLDER, "datacard.pdf")
IMAGEFOLDER = os.path.join(DATAFOLDER, "images")


def Main():
    createFolderStructure()
    army = parseArmyTextList()
    createDataCard(army['units'])
    openFile(DATACARDPDF)


def createFolderStructure():
    if not os.path.exists(DATAFOLDER):
        try:
            os.makedirs(DATAFOLDER)
        except Exception as ex:
            print("Data folder creation failed")
            print(ex)
            sys.exit(1)

    if not os.path.exists(DATAFOLDERARMYBOOK):
        try:
            os.makedirs(DATAFOLDERARMYBOOK)
        except Exception as ex:
            print("army book folder creation failed")
            print(ex)
            sys.exit(1)

    if not os.path.exists(FONTFOLDER):
        try:
            os.makedirs(FONTFOLDER)
        except Exception as ex:
            print("font folder creation failed")
            print(ex)
            sys.exit(1)

    if not os.path.exists(IMAGEFOLDER):
        try:
            os.makedirs(IMAGEFOLDER)
        except Exception as ex:
            print("image folder creation failed")
            print(ex)
            sys.exit(1)


def openFile(filePath):
    if platform.system() == 'Darwin':
        subprocess.call(('open', filePath))
    elif platform.system() == 'Windows':
        os.startfile(filePath)
    else:
        subprocess.call(('xdg-open', filePath))


def createDataCard(units):
    print("Create datacards ...")
    try:
        pdfmetrics.registerFont(TTFont('bold', os.path.join(
            FONTFOLDER, "rosa-sans", "hinted-RosaSans-Bold.ttf")))
        pdfmetrics.registerFont(TTFont('regular', os.path.join(
            FONTFOLDER, "rosa-sans", "hinted-RosaSans-Regular.ttf")))
    except Exception as ex:
        print("Font is missing!")
        print(ex)
        sys.exit(1)

    datacardSize = (200.0, 130.0)
    lineColor = [1.00, 0.55, 0.10]
    # creating a pdf object
    pdf = canvas.Canvas(DATACARDPDF, pagesize=datacardSize)
    pdf.setTitle("GDF data card")

    for unit in units:
        # Card Box
        topClearance = 10
        bottomClearance = 10
        sideClearance = 2
        pdf.setStrokeColorRGB(lineColor[0], lineColor[1], lineColor[2])
        path = pdf.beginPath()
        path.moveTo(0 + sideClearance, 0 + bottomClearance)
        path.lineTo(0 + sideClearance, datacardSize[1] - topClearance)
        path.lineTo(datacardSize[0] - sideClearance,
                    datacardSize[1] - topClearance)
        path.lineTo(datacardSize[0] - sideClearance,
                    0 + bottomClearance)
        path.close()
        pdf.setLineJoin(1)
        pdf.drawPath(path, stroke=1, fill=0)
        pdf.line(sideClearance, datacardSize[1] - 45,
                 datacardSize[0]-sideClearance, datacardSize[1] - 45)

        # Bottom Info Box
        pdf.setStrokeColorRGB(lineColor[0], lineColor[1], lineColor[2])
        pdf.setFillColorRGB(1, 1, 1)
        path = pdf.beginPath()
        sideClearance = 20
        sideClearance = 20
        height = 10
        bottomClearance = 5
        path.moveTo(0 + sideClearance, 0 + bottomClearance)
        path.lineTo(datacardSize[0] - sideClearance, 0 + bottomClearance)
        path.lineTo(datacardSize[0] - sideClearance,
                    0 + bottomClearance + height)
        path.lineTo(0 + sideClearance, 0 + bottomClearance + height)
        path.close()
        pdf.setLineJoin(1)
        pdf.drawPath(path, stroke=1, fill=1)
        pdf.setFont('bold', 4)
        pdf.setFillColorRGB(0, 0, 0)
        pdf.drawString(sideClearance+2, bottomClearance +
                       (height/2)-1, ", ".join(unit['specialRules']))

        # Image box
        unitImage = re.sub(r'(?is)([^\w])', '_', unit['name'].lower())
        unitImage = os.path.join(IMAGEFOLDER, unitImage)
        if os.path.exists(unitImage + ".jpg"):
            unitImage = unitImage + ".jpg"
        elif os.path.exists(unitImage + ".jpeg"):
            unitImage = unitImage + ".jpeg"
        elif os.path.exists(unitImage + ".png"):
            unitImage = unitImage + ".png"
        else:
            unitImage = None

        if (unitImage != None):
            with Image.open(unitImage) as img:
                img.load()
                imgSize = img.size
                draw = ImageDraw.Draw(img)
                draw.polygon(((0, 0), (imgSize[0]/2, imgSize[1]),
                              (0, imgSize[1])), fill=(0, 255, 0))
                draw.polygon(((imgSize[0], 0), (imgSize[0]/2, imgSize[1]),
                              (imgSize[0], imgSize[1])), fill=(0, 255, 0))
                imageBuffer = io.BytesIO()
                img.save(imageBuffer, "png")
                imageBuffer.seek(0)

        edgeLength = 60
        offsetTop = 2
        offsetRight = 35
        triangle = [
            [datacardSize[0] - edgeLength - offsetRight,
                datacardSize[1] - offsetTop],
            [datacardSize[0] - offsetRight, datacardSize[1] - offsetTop],
            [datacardSize[0] - (edgeLength/2) - offsetRight,
             datacardSize[1] - offsetTop - edgeLength]
        ]

        pdf.setStrokeColorRGB(lineColor[0], lineColor[1], lineColor[2])
        if (unitImage != None):
            pdf.drawImage(utils.ImageReader(imageBuffer), datacardSize[0] - offsetRight - edgeLength,
                          datacardSize[1] - offsetTop - edgeLength, edgeLength, edgeLength, mask=[0, 0, 255, 255, 0, 0])
            fillPath = 0
        else:
            fillPath = 1
        path = pdf.beginPath()
        path.moveTo(triangle[0][0], triangle[0][1])
        path.lineTo(triangle[1][0], triangle[1][1])
        path.lineTo(triangle[2][0], triangle[2][1])
        path.close()
        pdf.setLineJoin(1)
        pdf.drawPath(path, stroke=1, fill=fillPath)

        # Unit Name
        parts = unit['name'].split(" ")
        nameLines = []
        maxLineCahrs = 20
        lineParts = []
        for part in parts:
            if len(" ".join(lineParts)) + len(part) > maxLineCahrs:
                nameLines.append(" ".join(lineParts))
                lineParts = []
            lineParts.append(part)
        nameLines.append(" ".join(lineParts))

        pdf.setFont('bold', 10)
        pdf.setFillColorRGB(0, 0, 0)
        offset = 0
        for line in nameLines:
            pdf.drawString(5, datacardSize[1] - 25 - offset, line)
            offset += 8

        # Skills
        startX = datacardSize[0] - 25
        startY = datacardSize[1] - 20
        lineHight = 5
        pdf.setFont('bold', lineHight)
        pdf.setFillColorRGB(0, 0, 0)
        pdf.drawCentredString(startX, startY, "Quality")
        pdf.drawCentredString(startX, startY - (lineHight*3), "Defense")
        pdf.setFont('regular', 5)
        pdf.drawCentredString(startX, startY - (lineHight*1), str(unit["quality"]) + "+")
        pdf.drawCentredString(startX, startY - (lineHight*4), str(unit["defense"]) + "+")

        # Weapon
        startX = 5
        startY = datacardSize[1] - 70
        offsetX = [0, 70, 90, 115, 130]
        offsetY = 0
        headers = ['Weapon', 'Range', 'Attacks', 'AP', 'Special rules']
        for i in range(len(headers)):
            pdf.setFont("bold", 5)
            pdf.setFillColorRGB(0, 0, 0)
            pdf.drawString(startX + offsetX[i], startY + offsetY, headers[i])
        offsetY -= 8

        for weapon in unit['weapons']:
            pdf.setFont("regular", 5)
            pdf.setFillColorRGB(0, 0, 0)

            pdf.drawString(startX + offsetX[0],
                           startY + offsetY, weapon['name'])

            if "range" in weapon:
                pdf.drawString(startX + offsetX[1], startY + offsetY, str(weapon['range']) + '"')
            else:
                pdf.drawString(startX + offsetX[1], startY + offsetY, "-")

            pdf.drawString(startX + offsetX[2], startY + offsetY, "A" + str(weapon['attacks']))

            if "ap" in weapon:
                pdf.drawString(startX + offsetX[3], startY +
                               offsetY, weapon['ap'])
            else:
                pdf.drawString(startX + offsetX[3], startY + offsetY, "-")

            if "specialRules" in weapon and len(weapon['specialRules']) > 0:
                label = []
                for specialRule in weapon['specialRules']:
                    label.append(specialRule['label'])

                pdf.drawString(startX + offsetX[4], startY + offsetY, ", ".join(label))
            else:
                pdf.drawString(startX + offsetX[4], startY + offsetY, "-")

            offsetY -= 8

        if 'equipment' in unit and len(unit['equipment']) > 0:
            headers = {'name': 'Equipment', 'specialRules': ['']}
            unit['equipment'].insert(0, headers)
            font = "bold"
            for equipment in unit['equipment']:
                pdf.setFont(font, 5)
                pdf.setFillColorRGB(0, 0, 0)
                pdf.drawString(startX + offsetX[0], startY + offsetY, equipment['name'])
                pdf.drawString(startX + offsetX[4], startY + offsetY, ", ".join(equipment['specialRules']))
                offsetY -= 8
                font = "regular"

        pdf.showPage()
    pdf.save()


def parseArmyTextList(armyListText):
    armyData = {}

    length = len(armyListText[0])
    if (length > 6 and armyListText[0][0] == "+" and armyListText[0][1] == "+" and armyListText[0][2] == " " and armyListText[0][length - 3] == " " and armyListText[0][length - 2] == "+" and armyListText[0][length - 1] == "+"):
        armyData['listName'] = armyListText[0].rstrip(" ++").lstrip("++ ")
    else:
        return False

    unit = False
    armyData['units'] = []
    unitData = {}
    for x in range(1, len(armyListText)):
        if len(armyListText[x]) > 5:
            if unit == False and armyListText[x].count('|') == 2:
                unitData = {}
                unit = True
                data = armyListText[x].split("|")
                unitData['points'] = data[1].strip(" ")
                unitData['specialRules'] = []
                unitData['equipment'] = []
                for specialRules in data[2].split(","):
                    if re.match(r'^\s?(\dx\s|Scopes)', specialRules):
                        regExMatch = re.search(
                            r"(\dx)?([^(]+)(\()(.*)(\))", specialRules.strip(" "))
                        unitData['equipment'].append(
                            {'name': regExMatch.group(2).strip(" "), 'specialRules': regExMatch.group(4).split(",")})
                    else:
                        unitData['specialRules'].append(specialRules)
                regExMatch = re.findall(
                    r"(?P<name>.*)\s\[(?P<unitCount>\d+)\]\sQ(?P<quality>\d+)\+\sD(?P<defense>\d+)\+$", data[0].strip(" "))
                unitData['name'] = regExMatch[0][0]
                unitData['unitCount'] = int(regExMatch[0][1])
                unitData['quality'] = int(regExMatch[0][2])
                unitData['defense'] = int(regExMatch[0][3])
            elif unit == True:
                parts = armyListText[x].strip(" ").split(" ")
                parts = list(armyListText[x].strip(" "))

                weapons = []
                weaponExtract = []
                bracket = 0
                weaponRule = False
                for part in parts:
                    if (part == "("):
                        bracket += 1
                        weaponRule = True
                    elif (part == ")"):
                        bracket -= 1

                    if (part == "," and len(weaponExtract) == 0):
                        continue

                    weaponExtract.append(part)

                    if (weaponRule == True and bracket == 0):
                        weapons.append(''.join(weaponExtract).strip())
                        weaponExtract = []
                        weaponRule = False

                for weapon in weapons:
                    regExMatch = re.search(
                        r"([^(]+)(\()(.*)(\))", weapon.strip(" "))
                    weaponData = {}
                    weaponData['name'] = regExMatch.group(1)
                    weaponRules = regExMatch.group(3).split(",")
                    for weaponRule in weaponRules:
                        weaponRule = weaponRule.strip(" ")
                        if re.match(r'\d+"', weaponRule):
                            weaponData['range'] = int(
                                weaponRule.replace('"', ''))
                        elif re.match(r'A\d+', weaponRule):
                            weaponData['attacks'] = int(
                                weaponRule.replace("A", ""))
                        elif re.match(r'AP\(\d+\)', weaponRule):
                            weaponData['ap'] = int(weaponRule.replace(
                                "AP(", "").replace(")", ""))
                        else:
                            if not "specialRules" in weaponData:
                                weaponData['specialRules'] = []
                            weaponData['specialRules'].append(weaponRule)
                    if not "weapon" in unitData:
                        unitData['weapon'] = []
                    unitData['weapon'].append(weaponData)
        else:
            unit = False
            if "name" in unitData:
                armyData['units'].append(unitData)
            unitData = {}
    return armyData


def readMultipleLines():
    buffer = []
    end = 0
    while end < 2:
        line = sys.stdin.readline()
        buffer.append(line.rstrip("\n"))
        if (line == "\n"):
            end += 1
        else:
            end = 0
    return buffer


def getUnit(unit, jsonArmyBookList):
    data = {}
    for listUnit in jsonArmyBookList[unit['armyId']]['units']:
        if (listUnit['id'] == unit['id']):
            data['type'] = listUnit['name']
            data['name'] = listUnit['name']
            data['armyId'] = unit['armyId']
            data['id'] = listUnit['id']
            data['defense'] = listUnit['defense']
            data['quality'] = listUnit['quality']
            data['upgrades'] = listUnit['upgrades']
            data['weapons'] = []
            for equipment in listUnit['equipment']:
                data['weapons'].append(getWeapon(equipment))

            data['specialRules'] = getSpecialRules(listUnit['specialRules'])
            data = getUnitUpgrades(unit, data, jsonArmyBookList)
            break
    if "customName" in unit:
        data['name'] = unit['customName']
    return data


def getSpecialRules(data):
    specialRules = []
    for specialRule in data:
        rule = specialRule
        if specialRule['rating'] != "":
            rule['label'] = specialRule['name'] + \
                "(" + specialRule['rating'] + ")"
        else:
            rule['label'] = specialRule['name']

        specialRules.append(rule)

    return specialRules


def getWeapon(data):
    weapon = {}
    weapon['attacks'] = data['attacks']

    if "name" in data:
        weapon['name'] = data['name']

    if "range" in data:
        weapon['range'] = data['range']

    weapon['specialRules'] = getSpecialRules(data['specialRules'])

    for i in range(len(weapon['specialRules'])):
        if weapon['specialRules'][i]['key'] == "ap":
            weapon['ap'] = weapon['specialRules'][i]['rating']
            weapon['specialRules'].pop(i)
            break

    return weapon


def removeWeapon(removeWeapon, weapons):
    for remove in removeWeapon:
        for i in range(len(weapons)):
            if weapons[i]['name'].strip() == remove.strip():
                weapons.pop(i)
                break
    return weapons


def getUnitUpgrades(unit, unitData, jsonArmyBookList):
    for upgrade in unit['selectedUpgrades']:
        armyId = unit['armyId']
        upgradeId = upgrade['upgradeId']
        optionId = upgrade['optionId']
        for package in jsonArmyBookList[armyId]['upgradePackages']:
            for section in package['sections']:
                if (section['uid'] == upgradeId):
                    for option in section['options']:
                        if option['uid'] == optionId:
                            for gains in option['gains']:
                                if (gains['type'] == "ArmyBookWeapon"):
                                    unitData['weapons'].append(getWeapon(gains))
                                else:
                                    print("Waring no handling for " +
                                          gains['type'] + " upgradeId " + upgradeId + " optionId " + optionId)

                            if "replaceWhat" in section:
                                if (gains['type'] == "ArmyBookWeapon"):
                                    unitData['weapons'] = removeWeapon(section["replaceWhat"], unitData['weapons'])

    return unitData


def parseArmyJsonList(armyListJsonFile: str):
    print("Parse army list ...")
    armyData = {}
    jsonArmyBookList = {}

    jsonArmyList = loadJsonFile(armyListJsonFile)
    armyData['armyId'] = jsonArmyList['armyId']
    downloadArmyBook(armyData['armyId'])
    jsonArmyBookList[armyData['armyId']] = loadJsonFile(os.path.join(
        DATAFOLDERARMYBOOK, armyData['armyId'] + ".json"))
    armyData['armyName'] = jsonArmyBookList[armyData['armyId']]['name']
    armyData['listPoints'] = jsonArmyList['listPoints']
    armyData['listName'] = jsonArmyList['list']['name']

    armyData['units'] = []
    for unit in jsonArmyList['list']['units']:
        downloadArmyBook(unit['armyId'])
        jsonArmyBookList[armyData['armyId']] = loadJsonFile(os.path.join(
            DATAFOLDERARMYBOOK, unit['armyId'] + ".json"))
        unitData = getUnit(unit, jsonArmyBookList)
        armyData['units'].append(unitData)

    return armyData


def loadJsonFile(jsonFile: str):
    try:
        f = open(jsonFile, encoding="utf8")
        file = f.read()
        f.close()
    except Exception as ex:
        print("file failed to open " + jsonFile)
        print(ex)
        sys.exit(1)

    try:
        jsonObj = json.loads(file)
    except json.decoder.JSONDecodeError as ex:
        print(file + " Json is not valid!")
        print(ex)
        sys.exit(1)
    except Exception as ex:
        print("Unhandeld Exception")
        print(ex)
        sys.exit(1)
    return jsonObj


def downloadArmyBook(id: str):
    armyBookJsonFile = os.path.join(DATAFOLDERARMYBOOK, id + ".json")
    download = True
    if not os.path.exists(DATAFOLDERARMYBOOK):
        try:
            os.makedirs(DATAFOLDERARMYBOOK)
        except Exception as ex:
            print("Error data folder creation failed")
            print(ex)
            return False

    # download only when older than 1 day
    if os.path.exists(armyBookJsonFile):
        if time.time() - os.stat(armyBookJsonFile)[stat.ST_MTIME] < 86400:
            download = False

    if (download == True):
        try:
            print("Download army book ...")
            urllib.request.urlretrieve(
                "https://army-forge-studio.onepagerules.com/api/army-books/" + id + "~3?armyForge=true", armyBookJsonFile)
        except Exception as ex:
            print("Error download of army book failed")
            print(ex)
            return False

    if not os.path.exists(armyBookJsonFile):
        print("Error no aramy book for " + id)
        return False

    return True


def SaveDictToJson(dictData, file):
    try:
        with open(file, 'w') as fp:
            fp.write(json.dumps(dictData, indent=4))
    except Exception as ex:
        print("Error saving dict to json")
        print(ex)
        return False
    return True


if __name__ == "__main__":
    Main()
