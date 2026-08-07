"""Plain language explanation of each cause of death.

One entry per cause that appears in the DOSM top ten for any age band and
sex, so every row of the statistics graph has somewhere to go.

The numbers are NOT here. Anything measured - share, rank, death count -
comes from core/statistics.py, which reads the mortality_record table. This
module is only the written explanation, keyed by slug.

None of this is diagnostic. It describes what a condition is and what is
generally worth watching for, and every page carries the disclaimer.
"""

DEFAULT_RISK = "heart-disease"

# Fallbacks so a cause with no hand-written entry still renders a real page.
GENERIC = {
    "what_it_is": [
        "This cause appears in the Department of Statistics Malaysia top ten "
        "for your age and sex group. We have not written a full explanation "
        "for it yet.",
    ],
    "warning_signs": [],
    "emergency": "",
    "can_change": [],
    "cannot_change": ["Your age", "Your sex"],
    "change_note": "",
    "next_step": {
        "title": "Talk to a doctor",
        "detail": "A clinic visit is the right place to ask what this means "
                  "for you specifically.",
    },
}

RISK_DETAIL = {
    # -- circulatory ------------------------------------------------
    "heart-disease": {
        "name": "Heart disease",
        "lead": "A narrowing of the arteries that supply the heart. It builds "
                "up quietly over years, often with no symptoms until it is "
                "well advanced.",
        "what_it_is": [
            "Heart disease usually means the arteries supplying the heart have "
            "narrowed, so the heart muscle gets less blood than it needs. It "
            "builds up over years and often causes no symptoms at all until it "
            "is well advanced.",
            "That is what makes it different from most conditions on this list: "
            "the first clear sign is often the serious one.",
        ],
        "warning_signs": [
            "Chest pain, pressure or tightness, especially during exertion",
            "Breathlessness doing things that used to feel easy",
            "Pain spreading to the arm, neck, jaw or back",
            "Unusual fatigue, cold sweats or nausea",
        ],
        "emergency": "Chest pain with sweating, breathlessness or pain "
                     "spreading to the arm or jaw needs emergency help. "
                     "Call 999.",
        "can_change": [
            "How often you exercise",
            "Your blood pressure and cholesterol, once you know the numbers",
            "Smoking",
            "Diet, especially salt and fried food",
        ],
        "cannot_change": ["Your age", "Your sex", "Your family history"],
        "change_note": "Age and sex put you in this group in the first place, "
                       "and neither can be changed. What the left hand list "
                       "decides is where you sit inside that group.",
        "next_step": {
            "title": "Book a screening",
            "detail": "A screening gives you your blood pressure and "
                      "cholesterol numbers, which is the only way to turn this "
                      "from a population statistic into something about you "
                      "specifically. Free under PeKaB40 if you qualify.",
        },
    },
    "stroke": {
        "name": "Stroke",
        "lead": "A sudden loss of blood flow to the brain, and a leading cause "
                "of long term disability in Malaysia.",
        "what_it_is": [
            "A stroke happens when blood flow to part of the brain is cut off, "
            "either by a clot or by a bleed. Brain tissue starts to die within "
            "minutes, which is why treatment speed matters more here than for "
            "almost any other condition.",
            "Most strokes are survivable. What usually determines the outcome "
            "is how quickly the person reaches hospital.",
        ],
        "warning_signs": [
            "Face drooping on one side",
            "Arm weakness or numbness, usually on one side",
            "Speech that is slurred or hard to understand",
            "Sudden vision loss, severe headache or loss of balance",
        ],
        "emergency": "Use the word FAST: Face, Arms, Speech, Time. If any of "
                     "these appear suddenly, call 999 immediately. Do not wait "
                     "to see if it passes.",
        "can_change": [
            "Your blood pressure, once you know it",
            "Smoking",
            "How often you exercise",
            "Salt intake",
        ],
        "cannot_change": ["Your age", "Your sex", "Your family history"],
        "change_note": "Blood pressure does most of the work in this risk, and "
                       "it is both measurable and treatable. That makes stroke "
                       "one of the more changeable causes on the list.",
        "next_step": {
            "title": "Get your blood pressure checked",
            "detail": "It takes about a minute, it is free at any government "
                      "clinic, and it is the single most useful number for "
                      "this particular risk.",
        },
    },
    "high-blood-pressure": {
        "name": "High blood pressure",
        "lead": "Blood pushing too hard against the artery walls. It has no "
                "symptoms, so it is only found by measuring it.",
        "what_it_is": [
            "Blood pressure is the force of blood against the walls of your "
            "arteries. When it stays high for years it damages them, which is "
            "what drives heart disease, stroke and kidney failure.",
            "It is sometimes called the silent killer because it produces no "
            "feeling at all. People often discover it only after the damage it "
            "caused shows up as something else.",
        ],
        "warning_signs": [
            "Usually none at all, which is the point",
            "Very high readings can bring headaches, nosebleeds or blurred vision",
        ],
        "emergency": "Severe headache with confusion, chest pain or "
                     "breathlessness can mean dangerously high pressure. "
                     "Call 999.",
        "can_change": [
            "Salt intake",
            "Weight and activity level",
            "Alcohol",
            "Taking medication consistently if you are prescribed it",
        ],
        "cannot_change": ["Your age", "Your family history"],
        "change_note": "This one is unusual on this list: it is almost entirely "
                       "manageable once you know your numbers. The hard part is "
                       "finding out, because nothing tells you.",
        "next_step": {
            "title": "Have it measured",
            "detail": "Free at any government clinic and most pharmacies. "
                      "There is no way to know without the cuff.",
        },
    },

    # -- metabolic --------------------------------------------------
    "type-2-diabetes": {
        "name": "Type 2 diabetes",
        "lead": "A condition where the body stops responding properly to "
                "insulin, so sugar builds up in the blood instead of being "
                "used. It can be present for years before it is found.",
        "what_it_is": [
            "Type 2 diabetes means your body has stopped responding properly "
            "to insulin, so sugar builds up in the blood instead of being "
            "used. It develops slowly and can be present for years before it "
            "is found.",
            "Its danger is mostly indirect. Long term high blood sugar damages "
            "blood vessels, which raises the risk of heart disease, stroke, "
            "kidney failure and sight loss.",
        ],
        "warning_signs": [
            "Feeling thirsty much more than usual",
            "Passing urine often, particularly at night",
            "Tiredness that does not improve with rest",
            "Blurred vision, or cuts that are slow to heal",
        ],
        "emergency": "",
        "can_change": [
            "How often you exercise",
            "Sugar and refined carbohydrate intake",
            "Weight, if it is currently rising",
        ],
        "cannot_change": ["Your age", "Your family history"],
        "change_note": "Type 2 diabetes responds to daily habits more than "
                       "almost anything else on this list, and early on it can "
                       "sometimes be pushed back into the normal range.",
        "next_step": {
            "title": "Ask for a blood sugar test",
            "detail": "Usually included in the same screening that covers "
                      "blood pressure and cholesterol, so you can cover it in "
                      "one visit.",
        },
    },

    # -- respiratory ------------------------------------------------
    "pneumonia": {
        "name": "Pneumonia",
        "lead": "An infection that inflames the air sacs of the lungs, so they "
                "fill with fluid and breathing becomes hard work.",
        "what_it_is": [
            "Pneumonia is an infection of the lung tissue itself, usually "
            "bacterial or viral. The air sacs fill with fluid, which is why "
            "breathing becomes difficult and oxygen levels drop.",
            "Healthy adults usually recover with treatment. It becomes "
            "dangerous for older people, for anyone with a long term illness, "
            "and when treatment is delayed. That is why it ranks so high in "
            "the older age bands.",
        ],
        "warning_signs": [
            "A cough that brings up phlegm, sometimes rust coloured",
            "Fever, chills and sweating",
            "Sharp chest pain that gets worse when breathing in",
            "Breathlessness, or breathing faster than usual at rest",
        ],
        "emergency": "Difficulty breathing, blue lips or fingertips, or "
                     "confusion in an older person needs emergency care. "
                     "Call 999.",
        "can_change": [
            "Getting a flu or pneumococcal vaccination if you are eligible",
            "Smoking, which damages the lung's defences",
            "Treating chest infections early instead of waiting them out",
        ],
        "cannot_change": ["Your age", "Long term lung or heart conditions"],
        "change_note": "Vaccination is the single most effective thing here, "
                       "and it is the part most often skipped.",
        "next_step": {
            "title": "Ask about vaccination",
            "detail": "Government clinics can advise whether you qualify for "
                      "the pneumococcal or flu vaccine based on your age and "
                      "medical history.",
        },
    },
    "chronic-lung-disease": {
        "name": "Chronic lung disease",
        "lead": "Long term damage to the airways that makes breathing "
                "progressively harder. It does not reverse, but it can be "
                "slowed.",
        "what_it_is": [
            "This covers conditions where the airways are permanently narrowed "
            "or damaged, most commonly chronic obstructive pulmonary disease "
            "and severe asthma. Air moves in and out less easily, so ordinary "
            "activity leaves you short of breath.",
            "The damage already done cannot be undone. What can change is how "
            "fast it progresses from here.",
        ],
        "warning_signs": [
            "Breathlessness during everyday activity",
            "A cough that persists for months, often with phlegm",
            "Wheezing or a tight chest",
            "Repeated chest infections",
        ],
        "emergency": "Sudden severe breathlessness, or lips turning blue, "
                     "needs emergency care. Call 999.",
        "can_change": [
            "Smoking, by far the largest factor",
            "Exposure to smoke, dust and fumes at work or at home",
            "Staying active within your limits",
        ],
        "cannot_change": ["Your age", "Damage already done to the airways"],
        "change_note": "Stopping smoking slows the decline at any stage, "
                       "including after a diagnosis. It is the only thing "
                       "shown to change the course of this condition.",
        "next_step": {
            "title": "Get a breathing test",
            "detail": "A spirometry test at a clinic measures how well your "
                      "lungs move air, and picks this up long before daily "
                      "life is affected.",
        },
    },
    "tuberculosis": {
        "name": "Respiratory tuberculosis",
        "lead": "A bacterial infection of the lungs that spreads through the "
                "air. It is curable, but the treatment must be completed.",
        "what_it_is": [
            "Tuberculosis is caused by bacteria that usually attack the lungs. "
            "It spreads when someone with an active infection coughs or "
            "sneezes. Many people carry it without symptoms and never become "
            "ill.",
            "It is fully curable with a course of antibiotics, but the course "
            "runs for months. Stopping early is the main reason cases become "
            "drug resistant and deaths still occur.",
        ],
        "warning_signs": [
            "A cough lasting more than two weeks",
            "Coughing up blood",
            "Night sweats and unexplained fever",
            "Losing weight without trying",
        ],
        "emergency": "Coughing up blood needs medical attention the same day.",
        "can_change": [
            "Getting tested if you have had a cough for more than two weeks",
            "Finishing the full course of treatment if diagnosed",
            "Ventilation in shared living and working spaces",
        ],
        "cannot_change": ["Past exposure", "A weakened immune system"],
        "change_note": "Testing and treatment are free at government clinics "
                       "in Malaysia. This is one of the few causes on this "
                       "list where the outcome is almost entirely decided by "
                       "whether someone seeks care.",
        "next_step": {
            "title": "Get tested if the cough persists",
            "detail": "Any government clinic can arrange a sputum test and "
                      "chest X-ray. Both are free.",
        },
    },

    # -- cancers ----------------------------------------------------
    "lung-cancer": {
        "name": "Lung cancer",
        "lead": "Cancer of the airways and lung tissue. It usually causes no "
                "symptoms until it is well established.",
        "what_it_is": [
            "Lung cancer starts in the cells lining the airways. Because the "
            "lungs have no pain nerves of their own, a tumour can grow for a "
            "long time before it produces anything noticeable.",
            "It is the cancer most strongly tied to a single risk factor. "
            "Tobacco smoke, including second hand smoke, accounts for the "
            "large majority of cases.",
        ],
        "warning_signs": [
            "A cough that does not go away, or a change in a long standing cough",
            "Coughing up blood",
            "Breathlessness or repeated chest infections",
            "Chest pain, hoarseness, or losing weight without trying",
        ],
        "emergency": "Coughing up blood needs medical attention the same day.",
        "can_change": [
            "Smoking, including quitting after many years",
            "Second hand smoke at home and at work",
            "Exposure to fumes and dust without protection",
        ],
        "cannot_change": ["Your age", "Past exposure", "Family history"],
        "change_note": "Risk starts falling within a few years of stopping "
                       "smoking and keeps falling for a decade or more. "
                       "Quitting later still helps.",
        "next_step": {
            "title": "See a doctor about a persistent cough",
            "detail": "Any cough lasting more than three weeks is worth having "
                      "looked at, particularly if you smoke or used to.",
        },
    },
    "liver-cancer": {
        "name": "Liver cancer",
        "lead": "Cancer of the liver, which in Malaysia most often follows "
                "long term hepatitis B or C infection.",
        "what_it_is": [
            "Liver cancer usually develops in a liver already damaged by long "
            "term inflammation, most often from chronic hepatitis B or C or "
            "from cirrhosis.",
            "That makes it one of the more preventable cancers on this list. "
            "Hepatitis B is vaccine preventable, and both B and C are "
            "treatable once found.",
        ],
        "warning_signs": [
            "Pain or a lump in the upper right abdomen",
            "Losing weight and appetite without trying",
            "Yellowing of the skin or eyes",
            "Swelling of the abdomen",
        ],
        "emergency": "",
        "can_change": [
            "Hepatitis B vaccination",
            "Getting tested and treated for hepatitis B or C",
            "Alcohol intake",
            "Weight, since fatty liver also raises the risk",
        ],
        "cannot_change": ["Existing liver damage", "Family history"],
        "change_note": "If you have never been tested for hepatitis B, that is "
                       "the highest value thing on this page. It is a simple "
                       "blood test and it is treatable.",
        "next_step": {
            "title": "Ask for a hepatitis B test",
            "detail": "A single blood test at a government clinic. If you are "
                      "negative and unvaccinated, vaccination is available.",
        },
    },
    "bowel-cancer": {
        "name": "Bowel cancer",
        "lead": "Cancer of the colon, rectum or anus. It usually starts as a "
                "small growth that is harmless for years.",
        "what_it_is": [
            "Bowel cancer almost always begins as a polyp, a small growth on "
            "the bowel lining that is not cancerous at first. Over years some "
            "polyps turn cancerous.",
            "That slow start is what makes screening so effective here. A "
            "polyp found early can simply be removed, which prevents the "
            "cancer rather than treating it.",
        ],
        "warning_signs": [
            "Blood in your stool, or bleeding from the back passage",
            "A lasting change in bowel habit",
            "Abdominal pain, bloating or a feeling of incomplete emptying",
            "Losing weight or feeling tired without explanation",
        ],
        "emergency": "",
        "can_change": [
            "Taking up screening when offered",
            "Diet, particularly red and processed meat and fibre intake",
            "Activity level and weight",
            "Alcohol and smoking",
        ],
        "cannot_change": ["Your age", "Family history", "Inflammatory bowel disease"],
        "change_note": "Screening changes the outcome here more than for most "
                       "cancers, because it can remove the growth before it "
                       "ever becomes cancer.",
        "next_step": {
            "title": "Ask about bowel screening",
            "detail": "A stool test is usually the first step and can be done "
                      "at home. Government clinics can arrange it.",
        },
    },
    "breast-cancer": {
        "name": "Breast cancer",
        "lead": "The most commonly diagnosed cancer in Malaysian women. "
                "Survival is high when it is found early.",
        "what_it_is": [
            "Breast cancer begins in the cells of the breast, most often in "
            "the ducts. It can occur in men too, though it is far less common.",
            "Outcome depends heavily on stage at diagnosis. Found early, most "
            "cases are treatable. In Malaysia a large share are still found "
            "late, which is what drives the death numbers rather than the "
            "disease being untreatable.",
        ],
        "warning_signs": [
            "A lump or thickening in the breast or armpit",
            "A change in size, shape or skin texture, including dimpling",
            "Nipple discharge, or a nipple turning inward",
            "Skin that becomes red, scaly or looks like orange peel",
        ],
        "emergency": "",
        "can_change": [
            "Checking your own breasts regularly so changes get noticed",
            "Taking up mammogram screening when offered",
            "Alcohol, weight and activity level",
        ],
        "cannot_change": ["Your age", "Your sex", "Family history"],
        "change_note": "Nothing here prevents breast cancer outright. What the "
                       "left hand list changes is how early it gets found, "
                       "which is what decides the outcome.",
        "next_step": {
            "title": "Learn how to check, and ask about screening",
            "detail": "Government clinics can show you what to feel for and "
                      "advise when mammogram screening applies to you.",
        },
    },
    "cervical-cancer": {
        "name": "Cervical cancer",
        "lead": "Cancer of the cervix, almost always caused by long term HPV "
                "infection. It is one of the most preventable cancers there is.",
        "what_it_is": [
            "Nearly all cervical cancer is caused by persistent infection with "
            "human papillomavirus. The virus is common and usually clears on "
            "its own; in a minority of people it persists and slowly changes "
            "the cells of the cervix.",
            "Those changes take years and are detectable long before they "
            "become cancer, which is why vaccination plus screening can very "
            "nearly eliminate it.",
        ],
        "warning_signs": [
            "Bleeding between periods, after sex, or after menopause",
            "Vaginal discharge that is unusual for you",
            "Pain during sex, or persistent pelvic pain",
        ],
        "emergency": "",
        "can_change": [
            "HPV vaccination",
            "Cervical screening, by Pap smear or HPV test",
            "Smoking, which makes persistent infection more likely",
        ],
        "cannot_change": ["Past HPV exposure", "Your age"],
        "change_note": "Vaccination and screening together make this one of "
                       "the few cancers that can be almost entirely prevented. "
                       "Both are available through government clinics.",
        "next_step": {
            "title": "Book a cervical screening",
            "detail": "Free at government clinics. HPV self sampling is also "
                      "available in many places if you would prefer it.",
        },
    },
    "ovarian-cancer": {
        "name": "Ovarian cancer",
        "lead": "Cancer of the ovaries. Its early symptoms are vague and easily "
                "mistaken for ordinary digestive complaints.",
        "what_it_is": [
            "Ovarian cancer starts in the ovaries or fallopian tubes. There is "
            "no reliable screening test for it, and the early symptoms overlap "
            "with common, harmless problems.",
            "Because of that it is often found late. The single most useful "
            "thing is knowing which symptoms are worth acting on when they "
            "persist.",
        ],
        "warning_signs": [
            "Persistent bloating, rather than bloating that comes and goes",
            "Feeling full quickly, or loss of appetite",
            "Pelvic or abdominal pain that does not settle",
            "Needing to pass urine more often or more urgently",
        ],
        "emergency": "",
        "can_change": [
            "Acting on symptoms that persist for more than a few weeks",
            "Discussing family history with a doctor",
        ],
        "cannot_change": ["Your age", "Family history", "Genetic factors"],
        "change_note": "There is no screening programme for this, so the whole "
                       "difference is made by noticing a persistent pattern "
                       "and getting it checked rather than waiting.",
        "next_step": {
            "title": "See a doctor if symptoms persist",
            "detail": "Bloating, feeling full quickly or pelvic pain lasting "
                      "more than three weeks is worth having looked at.",
        },
    },
    "leukaemia": {
        "name": "Leukaemia",
        "lead": "A cancer of the blood forming cells in the bone marrow. It is "
                "one of the few cancers that is common in younger people.",
        "what_it_is": [
            "Leukaemia is a cancer of the cells that make blood. Abnormal white "
            "cells crowd out the healthy ones, which is why it causes anaemia, "
            "infections and bleeding all at once.",
            "It appears in this list partly because it affects children and "
            "young adults, unlike most cancers. Many types respond well to "
            "treatment, particularly in younger patients.",
        ],
        "warning_signs": [
            "Tiredness and paleness that does not improve",
            "Frequent infections, or infections that linger",
            "Bruising or bleeding easily, including nosebleeds and gum bleeding",
            "Bone or joint pain, night sweats, or swollen glands",
        ],
        "emergency": "Heavy unexplained bleeding, or fever with a known blood "
                     "condition, needs urgent medical care.",
        "can_change": [
            "Acting early on unexplained bruising, bleeding or infections",
            "Avoiding unprotected exposure to benzene and similar chemicals",
        ],
        "cannot_change": ["Your age", "Genetic factors", "Past radiation exposure"],
        "change_note": "Most risk factors for leukaemia are outside anyone's "
                       "control. What helps is not dismissing the early signs, "
                       "since a blood test settles the question quickly.",
        "next_step": {
            "title": "Ask for a blood test",
            "detail": "A full blood count is a routine, inexpensive test and "
                      "is the usual first step.",
        },
    },

    # -- other ------------------------------------------------------
    "liver-disease": {
        "name": "Liver disease",
        "lead": "Long term damage to the liver, which keeps working normally "
                "until a great deal of it is already scarred.",
        "what_it_is": [
            "This covers conditions where the liver is progressively damaged, "
            "most often by alcohol, by fat build up, or by chronic hepatitis B "
            "or C. Scar tissue gradually replaces working tissue.",
            "The liver has a large reserve, so it can lose a lot of function "
            "before anything feels wrong. Early damage is often reversible; "
            "late scarring is not.",
        ],
        "warning_signs": [
            "Yellowing of the skin or the whites of the eyes",
            "Swelling in the abdomen or the ankles",
            "Bruising easily, or unusually dark urine",
            "Persistent tiredness and loss of appetite",
        ],
        "emergency": "Vomiting blood, or confusion in someone with known liver "
                     "disease, is a medical emergency. Call 999.",
        "can_change": [
            "Alcohol intake",
            "Weight, since fatty liver is now a leading cause",
            "Getting tested and treated for hepatitis B or C",
            "Being careful with paracetamol and unregulated supplements",
        ],
        "cannot_change": ["Existing scarring", "Genetic conditions"],
        "change_note": "Caught before scarring sets in, liver damage often "
                       "reverses. That window is the reason a blood test is "
                       "worth doing before symptoms appear.",
        "next_step": {
            "title": "Ask for a liver function test",
            "detail": "A routine blood test. Worth requesting alongside a "
                      "hepatitis B check if you have never had one.",
        },
    },
    "transport-accidents": {
        "name": "Transport accidents",
        "lead": "Road traffic deaths. The leading cause of death for young "
                "Malaysian men, and the only one on this list that is not a "
                "disease.",
        "what_it_is": [
            "This covers deaths on the road, which in Malaysia overwhelmingly "
            "involve motorcycles. It sits at the top of the list for younger "
            "men by a wide margin.",
            "It is different from everything else here in one important way: "
            "the risk is immediate rather than accumulated. It does not build "
            "up over decades, and it does not give warning signs.",
        ],
        "warning_signs": [],
        "emergency": "For any serious road crash, call 999. Do not move a "
                     "casualty who may have a head, neck or back injury unless "
                     "they are in immediate danger.",
        "can_change": [
            "Wearing a properly fastened helmet, every trip",
            "Seat belts, in the back as well as the front",
            "Speed, particularly on familiar roads",
            "Never riding or driving after drinking, or while using a phone",
            "Keeping tyres and brakes maintained",
        ],
        "cannot_change": ["The behaviour of other road users", "Road conditions"],
        "change_note": "Unlike every disease on this list, this risk can drop "
                       "sharply today rather than over years. Helmet use and "
                       "speed are the two largest factors.",
        "next_step": {
            "title": "Check your helmet and your habits",
            "detail": "A correctly fastened, undamaged helmet is the single "
                      "most effective protection available for the riders who "
                      "make up most of these deaths.",
        },
    },
    "intentional-self-harm": {
        "name": "Intentional self-harm",
        "lead": "Deaths from suicide. If you are struggling right now, help is "
                "available and free.",
        "what_it_is": [
            "This appears in the statistics for younger age groups in Malaysia. "
            "It is included here because leaving it out would misrepresent what "
            "the data actually shows.",
            "Suicidal feelings are usually temporary, even when they do not "
            "feel that way, and they respond to support. Most people who get "
            "help come through it.",
        ],
        "warning_signs": [
            "Talking about being a burden, feeling trapped, or having no reason to go on",
            "Withdrawing from friends, family and things once enjoyed",
            "Big changes in sleep, appetite or mood",
            "Giving away possessions, or saying goodbye as though for good",
        ],
        "emergency": "If you or someone you know is in immediate danger, call "
                     "999. To talk to someone now: Talian HEAL on 15555, or "
                     "Befrienders KL on 03-7627 2929, which is free, "
                     "confidential and open 24 hours.",
        "can_change": [
            "Telling one person, whether a friend, family member or a helpline",
            "Talking to a doctor, who can refer you at no cost",
            "Staying connected to people, even briefly",
        ],
        "cannot_change": ["Things that have already happened to you"],
        "change_note": "Reaching out is the step that changes this, and it "
                       "does not have to be to someone you know. The helplines "
                       "below exist precisely for that.",
        "next_step": {
            "title": "Talk to someone today",
            "detail": "Talian HEAL 15555, or Befrienders KL 03-7627 2929, open "
                      "24 hours, free and confidential. You do not need to be "
                      "in crisis to call.",
        },
    },
}

# Fill in anything an entry leaves out, so the template never hits a blank.
for _slug, _entry in RISK_DETAIL.items():
    _entry["slug"] = _slug
    for _key, _value in GENERIC.items():
        _entry.setdefault(_key, _value)


def get_risk(slug):
    """Return the written explanation for a slug, or None if we have none."""
    return RISK_DETAIL.get(slug)
