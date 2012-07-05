import datetime

def daterange(start_date, end_date, extra=0):
    for n in range((end_date - start_date).days + extra):
        yield start_date + datetime.timedelta(n)

def parseDag(s, jaar):
    dag, maand = s.split('-')
    dag, maand = int(dag), int(maand)
    if maand < 8:
        return datetime.date(jaar+1, maand, dag)
    else:
        return datetime.date(jaar, maand, dag)

def parsePeriode(s,jaar):
    begin, einde = s.split('>')
    return [dag for dag in daterange(parseDag(begin, jaar), parseDag(einde, jaar), extra=1)]

def parseMaand(s,jaar):
    dag, maand = s.split('-')
    assert dag.strip()=='*', 'Verkeerd gebruik van het * formaat.'
    maand = int(maand)
    from calendar import monthrange
    if maand < 8:
       jaar+=1
    einddag = monthrange(jaar,maand)[1]
    return [dag for dag in daterange(datetime.date(jaar, maand, 1), datetime.date(jaar, maand, einddag), extra=1)]

def parseDatum(s, jaar):
    if '*' in s:
        return parseMaand(s, jaar)
    elif '>' in s:
        return parsePeriode(s, jaar)
    else:
        return [parseDag(s, jaar)]

def parseDatumBestand(bestand):
    #de eerste regel moet het jaartal bevatten
    jaar = int(bestand.readline())

    d = {'VAK':set(), 'S':set(), 'VRIJWM':set(), 'VRIJDM':set(), 'PUF':set(), 'VSB': set(), 'WM':set(), 'DM':set()}
    for regel in bestand:
        regel = regel.strip()

        #sla lege regels en commentaar regels over
        if not regel or regel[0]=='#': continue

        #overige commentaar verwijderen
        regel = regel.split('#')[0].strip()

        dagType, datum = regel.split(None, 1)
        
        for dag in parseDatum(datum, jaar):
            d[dagType].add(dag)

    return jaar, d

def verwerkDag(dag, dagen):
    trainingsdagenWM = [0,2,3,5] # maandag, woensdag, donderdag, zaterdag
    trainingsdagenDM = [1,4]     # dinsdag, vrijdag

    if dag in dagen['VAK']:
        s = 'if (equals=%02d-%02d) [black!70]%%\n' % (dag.month, dag.day)
    else:
        s = ''

    if dag in dagen['VRIJWM']:
        s+= 'if (equals=%02d-%02d) {\\oefenWM}%%\n' % (dag.month, dag.day)
    if dag in dagen['VRIJDM']:
        s+= 'if (equals=%02d-%02d) {\\oefenDM}%%\n' % (dag.month, dag.day)
    elif dag in dagen['PUF']:
        s+= 'if (equals=%02d-%02d) {\\puf}%%\n' % (dag.month, dag.day)
    elif dag in dagen['VSB']:
        s+= 'if (equals=%02d-%02d) {\\vsb}%%\n' % (dag.month, dag.day)
    elif dag in dagen['WM']:
        s+= 'if (equals=%02d-%02d) {\\waasmunster}%%\n' % (dag.month, dag.day)
    elif dag in dagen['DM']:
        s+= 'if (equals=%02d-%02d) {\\dendermonde}%%\n' % (dag.month, dag.day)
    elif dag in dagen['S']:
        return s #s teruggeven en stoppen met uitvoeren
    elif dag.weekday() in trainingsdagenWM and not dag in dagen['VAK']:
        s+= 'if (equals=%02d-%02d) {\\waasmunster}%%\n' % (dag.month, dag.day)
    elif dag.weekday() in trainingsdagenDM and not dag in dagen['VAK']:
        s+= 'if (equals=%02d-%02d) {\\dendermonde}%%\n' % (dag.month, dag.day)

    return s
        
f = open('input.txt', 'r')
jaar, dagen = parseDatumBestand(f)
f.close()

start = datetime.date(jaar, 8, 1)
einde = datetime.date(jaar+1, 7, 31)

kalenderDagen = [verwerkDag(dag, dagen) for dag in daterange(start, einde)]

opmaak = ''.join(['if (Sunday) [black!70]%\n'] + kalenderDagen)

f = open('sjabloon.txt', 'r')
sjabloon = f.read()
f.close()

print sjabloon % (jaar, jaar, jaar+1, jaar+1, opmaak, jaar, jaar+1)
