# -*- coding: utf-8 -*-
"""
Created on Tue Jun 12 11:15:20 2018
"""

# Copyright 2018 Language Technology, Universität Hamburg (author: Taylan Doganer, Eugen Ruppert, Steffen Remus, Benjamin Milde)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import operator
import re
import time

#Zahlen die am Ende übersetzt werden sollen z.B. 31 ----> ein und dreißig....
einer = ["null","ein","zwei","drei","vier","fünf","sechs","sieben","acht","neun"]
zweier = ["null","zehn","zwanzig","dreißig","vierzig","fünfzig","sechzig","siebzig","achtzig","neunzig"]

millionen = "Millionen"
tausend = "Tausend"
hundert = "Hundert"

# Abkürzungen 
def abbr2text(strabbr):
    neuertext = strabbr.replace("Anordn.","Anordnung")
    neuertext = neuertext.replace("(s. Bild)", "(siehe Bild)")
    neuertext = neuertext.replace("(s. Abbildung)", "(siehe Abbildung)")
    neuertext = neuertext.replace("ausschl.","ausschließlich")
    neuertext = neuertext.replace("Ausschl.","Ausschließlich")
    neuertext = neuertext.replace("Bzw.","Beziehungsweise")
    neuertext = neuertext.replace("bzw.","beziehungsweise")
    neuertext = neuertext.replace("Abb.","Abbildung")
    neuertext = neuertext.replace("Ggf.","Gegebennenfalls")
    neuertext = neuertext.replace("ggf.","gegebennenfalls")
    neuertext = neuertext.replace("Eigtl.","Eigentlich")
    neuertext = neuertext.replace("eigtl.","eigentlich")
    neuertext = neuertext.replace("Scherzh.","Scherzhaft")
    neuertext = neuertext.replace("scherzh.","scherzhaft")
    neuertext = neuertext.replace("Jmd.","Jemand")
    neuertext = neuertext.replace("jmd.","jemand")
    neuertext = neuertext.replace("Jmdm","Jemandem")
    neuertext = neuertext.replace("jmdm","jemandem")
    neuertext = neuertext.replace("Jmdn","Jemanden")
    neuertext = neuertext.replace("jmdn","jemanden")
    neuertext = neuertext.replace("Jmds","Jemandes")
    neuertext = neuertext.replace("jmds","jemandes")
    neuertext = neuertext.replace("Eur.","Euro")
    neuertext = neuertext.replace("€"," Euro")
    neuertext = neuertext.replace("Vllt.","Vielleicht")
    neuertext = neuertext.replace("vllt.","vielleicht")
    neuertext = neuertext.replace("USD","US Dollar")
    neuertext = neuertext.replace("US$","US Dollar")
    neuertext = neuertext.replace("$","Dollar")
    neuertext = neuertext.replace("Proz.","Prozent")
    neuertext = neuertext.replace("proz.","prozent")
    neuertext = neuertext.replace("Prof.","Professor")
    neuertext = neuertext.replace("prof.","professor")
    neuertext = neuertext.replace("Allg.","Allgemein")
    neuertext = neuertext.replace("allg.","allgemein")
    neuertext = neuertext.replace("Bes.","Besonders")
    neuertext = neuertext.replace("bes.","besonders")
    neuertext = neuertext.replace("Erg.","Ergänze")
    neuertext = neuertext.replace("erg.","ergänze")
    neuertext = neuertext.replace("Geb.","Geboren")
    neuertext = neuertext.replace("geb.","geboren")
    neuertext = neuertext.replace("Ggs.","Gegensatz")
    neuertext = neuertext.replace("Übertr.","Übertragen")
    neuertext = neuertext.replace("übertr.","übertragen")
    neuertext = neuertext.replace("wiss.","wissenschaft")
    neuertext = neuertext.replace("Wiss.","Wissenschaft")
    neuertext = neuertext.replace("mio.","millionen")
    neuertext = neuertext.replace("Mio.","Millionen")
    neuertext = neuertext.replace("tech.","technik")
    neuertext = neuertext.replace("Tech.","Technik")
    neuertext = neuertext.replace("U.Dgl","Und Dergleichen")
    neuertext = neuertext.replace("U.dgl","Und dergleichen")
    neuertext = neuertext.replace("u.Dgl","und Dergleichen")
    neuertext = neuertext.replace("u.dgl","und dergleichen")
    neuertext = neuertext.replace("V. Chr.","Vor Christus")
    neuertext = neuertext.replace("v. Chr.","vor Christus")
    neuertext = neuertext.replace("N. Chr.","Nach Christus")
    neuertext = neuertext.replace("n. Chr.","nach Christus")
    neuertext = neuertext.replace("Ugs.","Umgangssprachlich")
    neuertext = neuertext.replace("ugs.","umgangssprachlich")
    neuertext = neuertext.replace("Urspr.","Ursprünglich")
    neuertext = neuertext.replace("urspr.","ursprünglich")
    neuertext = neuertext.replace("Usw.", "Und so weiter")
    neuertext = neuertext.replace("usw.", "und so weiter")
    neuertext = neuertext.replace("z.B.", "zum Beispiel")
    neuertext = neuertext.replace("Z.B.", "Zum Beispiel")
    neuertext = neuertext.replace("D.h.","Das heißt")
    neuertext = neuertext.replace("D.D.","Das Deißt")
    neuertext = neuertext.replace("d.H.","das Heißt")
    neuertext = neuertext.replace("d.h.","das heißt")
    neuertext = neuertext.replace("V.a.","Vor allem")
    neuertext = neuertext.replace("v.A.","vor Allem")
    neuertext = neuertext.replace("V.A.","Vor Allem")
    neuertext = neuertext.replace("v.a.","vor allem")
    neuertext = neuertext.replace("Etc."," et cetera")
    neuertext = neuertext.replace("etc."," et cetera")
    neuertext = neuertext.replace("Zzt.","Zurzeit")
    neuertext = neuertext.replace("zzt.","zurzeit")
    neuertext = neuertext.replace("%", " Prozent")
    neuertext = neuertext.replace("°F"," Grad Fahrenheit")
    neuertext = neuertext.replace("°C"," Grad Celius")
    neuertext = neuertext.replace("°"," Grad")
    neuertext = neuertext.replace("km/h","Kilometer pro Stunde")
    neuertext = neuertext.replace("½","ein halb")
    neuertext = neuertext.replace("⅓","ein drittel")
    neuertext = neuertext.replace("¼","ein viertel")

    ## careful    
    neuertext = neuertext.replace("Op.","Operation")
    neuertext = neuertext.replace("OP.","Operation")
    neuertext = neuertext.replace(" op."," operation")
    neuertext = neuertext.replace("NR.","Nummer")
    neuertext = neuertext.replace("Nr.","Nummer")
    neuertext = neuertext.replace(" nr."," nummer")
    neuertext = neuertext.replace("O.Ä.","Oder Ähnliches")
    neuertext = neuertext.replace("o.Ä.","oder Ähnliches")
    neuertext = neuertext.replace("U.A.","Unter Anderem")
    neuertext = neuertext.replace("u.A.","unter Anderem")
    neuertext = neuertext.replace("u.a.","unter anderem")    
    neuertext = neuertext.replace("U.Ä.","Und Ähnliches")
    neuertext = neuertext.replace("u.Ä.","und Ähnliches")
    neuertext = neuertext.replace("u.ä.","und ähnliches")
    neuertext = neuertext.replace("U.","Und")
    neuertext = neuertext.replace(" u."," und")
    neuertext = neuertext.replace(" zz."," zurzeit")
    neuertext = neuertext.replace("Zz.","Zurzeit")
    neuertext = neuertext.replace("Ca.","Circa")
    neuertext = neuertext.replace(" ca."," circa")
    neuertext = neuertext.replace(" m. "," Meter ")
    neuertext = neuertext.replace(" m "," Meter ")
    neuertext = neuertext.replace(" km "," Kilometer ")
    neuertext = neuertext.replace(" cm "," Zentimeter ")
    neuertext = neuertext.replace(" mm "," Milimeter ")
    neuertext = neuertext.replace("Min.","Minuten")
    neuertext = neuertext.replace(" min."," minuten")
    neuertext = neuertext.replace("M.","Meter")   
    neuertext = neuertext.replace("§", "Paragraf ")
    neuertext = neuertext.replace("†", "gestorben ")
    neuertext = neuertext.replace("π", "Pi") 
    neuertext = neuertext.replace("ϕ", "Phi")
    neuertext = neuertext.replace("α", "Alpha")
    neuertext = neuertext.replace("β", "Beta")
    neuertext = neuertext.replace("γ", "Gamma")
    neuertext = neuertext.replace("ɣ", "Gamma")
    neuertext = neuertext.replace("×", " mal ")
    neuertext = neuertext.replace("…", "...")
    neuertext = neuertext.replace("–", "-")
    neuertext = neuertext.replace("„", '"')
    neuertext = neuertext.replace("“", '"')
    neuertext = neuertext.replace("’", "'")
    neuertext = neuertext.replace("  "," ")  
    neuertext = neuertext.replace(" & ", " und ")
    neuertext = neuertext.replace("\n\n", "\n")

    return neuertext

# Zahlen Normalisator z.B. 3412 --> drei Tausend zwölf 
def num2text(strnum, zehner_trenner='' , trenner=' ', debug=False):

    strnum = strnum.strip()

    if debug:
        print(strnum)
        time.sleep(0.1)

    if "." in strnum:
        return num2text(strnum.replace('.',''), zehner_trenner='' , trenner=' ')

    if "+" in strnum:
        if strnum[-1] == '+':
            return num2text(strnum[:-1], zehner_trenner='' , trenner=' ')
        elif len(strnum) > 0 and strnum[0] == '+':
            return "plus " + num2text(strnum[1:], zehner_trenner='' , trenner=' ')
        else:
            return num2text(strnum.split("+")[0], zehner_trenner='' , trenner=' ') + " plus " + num2text(strnum.split("+")[1], zehner_trenner='' , trenner=' ')

    # note: - kann sowohl 'bis' als auch 'Minus' bedeuten
    if "-" in strnum:
        if strnum[-1] == '-':
            return num2text(strnum[:-1], zehner_trenner='' , trenner=' ')
        elif len(strnum) > 0 and strnum[0] == '-':
            return "minus " + num2text(strnum[1:], zehner_trenner='' , trenner=' ')
        else:
            return num2text(strnum.split("-")[0], zehner_trenner='' , trenner=' ') + " bis " + num2text(strnum.split("-")[1], zehner_trenner='' , trenner=' ')

    if "," in strnum:
        return num2text(strnum.split(",")[0], zehner_trenner='' , trenner=' ') + " Komma " + ' '.join([num2text(elem) for elem in strnum.split(",")[1]])

    # ist strnum eine zahl? wenn nein dann rufe abbr2text auf, falls ja mache einfach weiter
    if not test_number_regex(strnum):
        return abbr2text(strnum)
      
    if len(strnum) == 7 or len(strnum) == 8 or len(strnum) == 9:
        if strnum[0] == "0":
            return (num2text(strnum[1:]))
        if strnum == "1000000":
            return millionen

        return num2text(strnum[:-6]) + trenner + millionen + (trenner + num2text(strnum[-6:]) if strnum[-6:] != '000000' else '')

    # vierstellige und fünfstellige und sechsstellige Zahl
    if len(strnum) == 4 or len(strnum) == 5 or len(strnum) == 6:
        if strnum[0] == "0":
            return (num2text(strnum[1:]))
        if strnum == "1000":
            return tausend

        return num2text(strnum[:-3]) + trenner + tausend + (trenner + num2text(strnum[-3:]) if strnum[-3:] != '000' else '')
                
    # dreistellige Zahl
    if len(strnum) == 3:
        if strnum[0] == '0':
            return (num2text(strnum[1:]))
        if strnum== "100":
            return hundert
        if strnum[1:]=="00": 
             return einer[int(strnum[0])] + trenner+ hundert
             
        return einer[int(strnum[0])] + trenner + hundert + trenner + num2text(strnum[1:])

    # zweistellige Zahl
    if len(strnum) == 2:
        if strnum=='11':
            return 'elf'
        if strnum=="12":
            return "zwölf"
        # zweier Zaheln endet auf einer null
        if strnum[-1]=='0':
            return zweier[int(strnum[0])]
        if strnum[0]=='0':
            return num2text(strnum[1])
        if strnum[1]=='1':
            return "ein" + (zehner_trenner if strnum[0]=='1' else trenner + 'und' + trenner ) + zweier[int(strnum[0])] 
        if strnum[1]=='7':
            return "sieb" + (zehner_trenner if strnum[0]=='1' else trenner + 'und' + trenner ) + zweier[int(strnum[0])] 
        return num2text(strnum[-1]) + (zehner_trenner if strnum[0]=='1' else trenner + 'und' + trenner ) + zweier[int(strnum[0])] 
    # einzahl der Ziffer
    if len(strnum)== 1:
        if strnum=='1':
            return "eins"
        #else:
        #    print(strnum)
        return einer[int(strnum)]

    return ""

# Findet den Ausdruck den man haben will
def finde_ausdruck(ausdruck, text):
    match = re.search(ausdruck, text)
    if not match:
        return None, None
    begin = match.start() ## füll mich aus
    end = match.end()
    return begin, end

# Schreibt die Nummer der Uhrzeiten als Wort auf
def ersetze_uhrzeit(text):
    begin, end = finde_ausdruck("[0-2]?[0-9]:[0-5][0-9]( Uhr)?", text)
    if end:
        text_abschnitt = text[begin:end] 
        if text_abschnitt[1] != ":" and int(text_abschnitt[0:2]) >24:
            return(text)
        #print(text_abschnitt)
        normalisierter_text_abschnitt = text_abschnitt.replace(":00",":")        
        normalisierter_text_abschnitt = normalisierter_text_abschnitt.replace(" Uhr","")
        normalisierter_text_abschnitt = normalisierter_text_abschnitt.replace(":"," Uhr ").strip()
        #print(normalisierter_text_abschnitt)
        normalisierter_text_abschnitt = text_normalization(normalisierter_text_abschnitt)
        #print(normalisierter_text_abschnitt)

        vor_abschnitt= text[:begin]
        nach_abschnitt= text[end:]
        neuer_text = vor_abschnitt + normalisierter_text_abschnitt + nach_abschnitt
        return (neuer_text)
    return text

# Jahreszahlen wie 1999 erkennen => neunzehn Hundert neun und neunzig  
def ersetze_jahre(text):
    text += ' '

    replace_year = False
    pre = False

    begin_t, end_t = finde_ausdruck("((Jahr)|(Jahre)|(Januar)|(Februar)|(März)|(April)|(Mai)|(Juni)|(Juli)|(August)|(September)|(Oktober)|(November)|(Dezember)|(von)|(bis)|(Von)|(Bis)|(um)|(Um)|(seit)|(Seit)|(ab)|(Ab)|(gegründet)|(Gegründet)|(erstmals)|(Erstmals)|(etwa)|(Etwa)|(das)|(Das)|(bereits)|(Bereits)|(erfolgte)|(Erfolgte)|(entstand)|(begann)|(sie)|(nach)|(Nach)|(begann)|(Begann)|(war)|(sich)|(Jänner)|(dem)|(Sommerspielen)|(erst)|(zwischen)|(des)|(gründete)|(Spielen)|(Ende)|(erschien)|(erschienen)|(Sommer)|(fand)|(schon)|(Herbst)|(geboren)|(als)|(kam)|(Frühjahr)|(Anfang)|(ging)|(hielt)|(erhielt)|(entfielen)|(hatte)|(gewann)|(verlor)|(nahm)|(Saison)|(gründeten)|(trat)|(zuerst)|(hat)|(dort)|(promovierte)|(wurde)|(Gründung)|(erst)|(Erst)|(ursprünglich)|(Ursprünglich)|(erwarb)|(welche)|(welches)|(hier)|(seinem)|(fanden)|(spätestens)|(gegründet)|(entstanden)|(ungefähr)|(Mitte)|(vor)|(Vor)|(veröffentlichte)|(veröffentlicht)|(Weltmeisterschaft)|(Fußballmeisterschaft)|(schloss)|(waren)|(vermutlich)|(nahmen)|(stellte)|(noch)|(jedoch)|(Jahreszahl)|(und)) 1[0-9]{3} ", text)
    if end_t: 
        begin, end = begin_t, end_t
        replace_year = True
        pre = True

    if not replace_year:
        begin_t, end_t = finde_ausdruck("1[0-9]{3} ((in)|(bis)|(von)|(und)|(als)|(wurde)|(im)|(durch)|(mit)|(auf)|(war)|(die)|(erstmals)|(gegründet)|(unter)|(bei)|(vom)|(nach)|(an)|(ist)|(eine)|(aus)|(das)|(ein)|(zum)|(wurden)|(gegründete)|(für)|(gegründet)|(der)|(den)|(fand)|(oder)|(wird)|(zur)|(urkundlich)|(zu)|(gehörte)|(am)|(gegründeten)|(errichtet)|(waren)|(hatte)|(kam)|(einen)|(begann)|(Metern)|(statt)|(eröffnet)|(erhielt)|(gab)|(errichtet)|(über)|(erfolgte)|(auch)|(während)|(jährlich)|(fanden)|(gründete)|(dem)|(errichtete)|(eröffnete)|(erbaut)|(beim)|(erwähnt)|(Einwohnern)|(zunächst)|(erbaut)|(eröffnet)|(veröffentlicht)|(zwischen)|(erschienenen)|(gegründeter)|(entstand)|(noch)|(zurück)|(seine)|(verstorbener)|(erbaute)|(zusammen)|(seinen)|(gegründetes)|(trat)|(hat)|(erschien)|(werden)|(ging)|(veröffentlichte)|(sind)|(wieder)|(vor)|(des)|(ins)|(erwarb)|(nahm)|(fertiggestellt)|(bestand)|(offiziell)|(neu)|(bildete)|(ließ)|(erwähnt)|(sein)|(nicht)|(führte)|(veröffentlichten)|(eröffneten)|(gründeten)|(errichteten)|(erschienene)|(um)|(gebaut)|(gebildet)|(gegen)|(anlässlich)|(nur)|(sowie)|(Teil)|(gewann)|(zählte)|(hieß)|(konnte)|(eingeführt)|(stellte)|(gemeinsam)|(ihren)|(fertiggestellt)|(ebenda)|(bestehende)|(entstanden)|(übernahm)|(entdeckte)|(entdeckt)|(begannen)|(vermutlich)|(steht)|(wechselte)|(begonnen)|(ihre)|(entstandene)|(Ritter)|(kaufte)|(eingeweiht)|(gehört)|(gibt)|(lebten)|(wählte)|(ausgetragen)|(folgte)|(fertiggestellte)|(angelegt)|(spielte)|(zwei)|(erschienener)|(bestehenden)|(schriftlich)|(anhand)|(Jahre)|(entstandenen)|(begonnen)|(enthält)|(zeigt)|(erbauten)|(bereits)|(heiratete)|(Mitglied)|(stand)|(alle)|(entwickelte)|(zog)|(statt)|(kamen)|(eingerichtet)|(eröffnet)|(auf)|(Jahren)|(statt)|(eingeweiht)|(definitiv)|(befand)|(errichtet)|(eingeführt)|(wegen)|(starb)|(gestorben)|(geboren)|(heiratete)|(habilitierte)|(promovierte))", text)

     #   begin_t, end_t = finde_ausdruck("1[0-9]{3} ((in)|(im)|(auf)|(bei)|(ab)|(aus)|(mit)|(nach)|(von)|(zu)|(bis)|(durch)|(für)|(gegen)|(ohne)|(um)|(als)|(vor)|(jedoch)|(ein)|(eine)|(war)|(wurde)|(hatte)|(musste)|(gab)|(konnte)|(starb)|(gestorben)|(geboren)|(heiratete)|(habilitierte)|(promovierte)|)", text)
        if end_t:    
            begin, end = begin_t, end_t
            replace_year = True
            pre = False


    if replace_year:

        text_abschnitt = text[begin:end-1]
        vor_abschnitt = text[:begin]
        nach_abschnitt = text[end:]
        text_abschnitt_split = text_abschnitt.split()

        if pre:
            normalisierter_text_abschnitt = text_abschnitt_split[0] + " " + num2text(text_abschnitt_split[1][:2]) + " " + hundert + " " +  num2text(text_abschnitt_split[1][2:])
        else:
            normalisierter_text_abschnitt = num2text(text_abschnitt_split[0][:2]) + " " + hundert + " " +  num2text(text_abschnitt_split[0][2:]) + " " + text_abschnitt_split[1]

        neuer_text = vor_abschnitt + normalisierter_text_abschnitt + text[end-1] + nach_abschnitt

        return neuer_text

    return text[:-1]

# ersetze 1. mit erster 2. mit weiter usw. 
# vorsicht: 1. kann auch erste sein (männl., weibl.)  

# ersetzt Ordnungszahlen oder Positionen von der Ziffer zum Wort
def ersetze_faelle(text, kasus="Nom", debug =False):
    if debug:
        print('ersete Fall in text:', text)
    text += ' '
    #"[0-9]+\.((\?)*(\!)*| )"
    begin, end = finde_ausdruck("[0-9]+\.[ ,.!?:;\"]", text)
    if end:        
        text_abschnitt = text[begin:end-2]
        if debug: 
            print('ersete Fall in:', text_abschnitt)
        if ":00" in text_abschnitt:
            text[:-1]
        if text_abschnitt == "1":
            normalisierter_text_abschnitt = "erste"
        elif text_abschnitt == "3":
            normalisierter_text_abschnitt = "dritte"        
        elif text_abschnitt == "7":
            normalisierter_text_abschnitt = "siebte"
        elif text_abschnitt =="8":
            normalisierter_text_abschnitt = "achte"   
        else:
            zahl = num2text(text_abschnitt)
            if end-begin > 3 and int(text_abschnitt[-2:]) > 19: 
                zahl = zahl + "s"
            normalisierter_text_abschnitt = zahl + "te"
            normalisierter_text_abschnitt = normalisierter_text_abschnitt.strip()
            
        # z.b. Am 23. Mai -> Am drei und zwanzigsten Mai
        begin_am_test, end_am_test = finde_ausdruck("((Den)|(den)|(dem)|(Dem)|(am)|(Am)|(zum)|(Zum)|(im)|(Im)|(vom)|(Vom)|(beim)|(Beim)|(des)|(Des)) [0-9]+\. ", text)
        if end_am_test and end_am_test>=end and begin_am_test <= begin:
            normalisierter_text_abschnitt += "n"
        elif kasus== "akk":
            normalisierter_text_abschnitt += "n"
        elif kasus=="dat":
            normalisierter_text_abschnitt += "n"    
        elif kasus=="gen":
            normalisierter_text_abschnitt += "n"
            
            
        vor_abschnitt = text[:begin]
        nach_abschnitt = text[end:]
        neuer_text = vor_abschnitt + normalisierter_text_abschnitt + text[end-1] + nach_abschnitt
        return ersetze_faelle(neuer_text)[:-1]
    return text[:-1]
    pass   
    
# ersetzt Daten der Form 11.12.2015, 15.01.
def ersetze_datum(text):
    return text
    
# Hauptnormalisierungsfunktion, die andere 
# Z.b. text_normalization("Bis zum 23. Mai 1999 um 23:40 Uhr trafen sich 3.000.000 Menschen um 3,53€ zu spenden")
# => 'Bis zum drei und zwanzigsten Mai neunzehn Hundert neun und neunzig um drei und zwanzig Uhr vierzig trafen sich drei Millionen Menschen um drei Komma fünf drei Euro zu spenden '

def text_normalization(text, tries=3, replace_tries=10, debug=False):
    if tries == 0:
        return text.strip()

    for i in range(replace_tries):
        text = abbr2text(text)
    for i in range(tries):
        text = ersetze_uhrzeit(text)
    for i in range(tries):
        text = ersetze_datum(text)
    for i in range(tries):
        text = ersetze_jahre(text)
    for i in range(tries):
        text = ersetze_faelle(text)
    # print("Im text '%s' wird nach einer Zahl gesucht ." % text )
    begin, end = finde_ausdruck("(-?[0-9]+[\,\.\-\+]?)+", text)
    if end: 
        # normalisieren
        if text[end-1] == ',':
            end -= 1
        text_abschnitt = text[begin:end] # füll mich aus
        if debug:
            print("zahl:", text_abschnitt)
        normalisierter_text_abschnitt = num2text(text_abschnitt)        
        # print("Die gefundene Zahl '%s' wird mit '%s' ersetzt." % (text_abschnitt, normalisierter_text_abschnitt) )
        vor_abschnitt= text[:begin]
        nach_abschnitt= text[end:]
        neuer_text= vor_abschnitt + normalisierter_text_abschnitt + nach_abschnitt 
        return text_normalization(neuer_text, tries-1)
        
    return text.strip()

# zeigt ob die Nummer richtig oder falsch ist
def test_number_iterative(text):
    for character in text:
         if character== "1":
             return True
    return False

# Beispiele zu Abkürzungen + zählz die Wörter und sortiert sie
def test_number_regex(text):
    pattern = re.compile('[0-9]+')
    match = pattern.match(text)
    return match.group() == text if(match) else False
