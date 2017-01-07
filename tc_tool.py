import logging
from flask import Flask
from flask_ask import Ask, statement, question, session
import re
from ussgl import tc_lookup
from ussgl import df
import difflib

app = Flask(__name__)

ask = Ask(app, "/")

logging.getLogger("flask_ask").setLevel(logging.DEBUG)

@ask.launch
def hello():
    welcome = "Welcome! What SGLs do you want to look up?"
    return question(welcome).reprompt(welcome + 'You can say something like Debit ten ten and Credit thirteen ten.')


def sglify(sgls_in):
    sgls_list = str(df.Debits + df.Credits)
    sgls_list = set(re.findall(r'(\d\d\d\d)\d\d', sgls_list))
    sgls_out = []
    for sgl in sgls_in:
        try:
            sgls_out.append(difflib.get_close_matches(sgl, sgls_list, cutoff=.7)[0])
        except:
            print('fuck shit up with {}'.format(sgl))

    return sgls_out


def tc_results(drs=None, crs=None):

    result = tc_lookup(drs,crs)

    if drs:
        if len(drs) > 1:
            drs[-1] = 'and {}'.format(drs[-1])
    if crs:
        if len(crs) > 1:
            crs[-1] = 'and {}'.format(crs[-1])

    drs = ' '.join(drs) if drs else None
    crs = ' '.join(crs) if crs else None

    tcs = list(result.index)

    tcslen = len(tcs) if tcs else 0

    if tcslen > 1:
        tcs[-1] = 'and {}'.format(tcs[-1])

    tcs = ', '.join(tcs) if tcs else None

    if tcslen == 0:
        msg = 'There are no transaction codes with debits of {} and credits of {}. '.format(drs, crs)

    elif tcslen == 1:
        msg = 'There is {} transaction code that has debits of {} and credits of {}. '\
               'The transaction code is {}.'.format(len(result), drs, crs, tcs)

    else:
        msg = 'There are {} transaction codes that have debits of {} and credits of {}. '\
               'The transaction codes are {}.'.format(len(result), drs, crs, tcs)

    msg = msg.replace('debits of None', 'no debits specified').replace('credits of None', 'no credits specified')
    return msg

@ask.intent("SGLs")
def sgls(sgl_accts):

    try:

        if not sgl_accts:
            msg = 'I did not hear any SGL accounts. Please try again. You can say something like debit ten ten and credit twenty one ten.'
            return statement(msg).simple_card('TFM Tool', msg)

        sgl_accts = sgl_accts.replace(',','').replace('debits', 'debit')\
                             .replace('credits', 'credit').replace(' 01','01')\
                             .replace(' 801', ' 8801')\
                             .replace(' 802', ' 8802')\
                             .replace(' 803', ' 8803')\
                             .replace(' 804', ' 8804')


        drs = re.findall('\d{3,4}', ''.join(sgl_accts.split('credit')[0]))
        crs = re.findall('\d{3,4}', ''.join(sgl_accts.split('credit')[-1])) if 'credit' in sgl_accts else None

        if drs and crs:
            drs = sglify(drs)
            crs = sglify(crs)
            sgls = list(drs + crs)

        elif drs:
            drs = sglify(drs)
            sgls = list(drs)

        elif crs:
            crs = sglify(crs)
            sgls = list(crs)

        else:
            msg = 'I did not hear any SGL accounts. Please try again. You can say something like debit ten ten and credit twenty one ten.'
            return statement(msg).simple_card('TFM Tool', msg)

        msg = tc_results(drs, crs)

        spoken_msg = str(msg)

        for sgl in sgls:
            print(sgl[:2] + ' ' + sgl[2:])
            spoken_msg = spoken_msg.replace(sgl, sgl[:2]+' '+sgl[2:])

        spoken_msg = spoken_msg.replace(' 00', ' hundred')

        return statement(spoken_msg).simple_card('TFM Tool', msg)

    except Exception as e:
        msg = "Error: {}.".format(e)

        return statement(msg).simple_card('TFM Tool', msg)



@ask.intent('AMAZON.HelpIntent')
def help():
    speech_text = "T F M tool looks up ussgl transaction codes. Ask for one or more debits, one or more credits, or both. "\
                  "You can say something like debit ten ten and credit twenty one ten. "
    reprompt_text = 'What SGLs would you like to lookup?'
    return question(speech_text).reprompt(reprompt_text)


@ask.intent('AMAZON.StopIntent')
def stop():
    msg = 'Bye bye!'
    return statement(msg)


@ask.intent('AMAZON.CancelIntent')
def cancel():
    msg = 'Bye bye!'
    return statement(msg)


if __name__ == '__main__':
    print(sgls('ask t f m tool for debits 801').__dict__)
    # print(sglify(['1,010']))
    # app.run(debug=True)
