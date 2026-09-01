"""
Government Healthcare Schemes & Affordable Medicine Portal Database
===================================================================
Provides verified, structured public health scheme information in:
- English (en)
- Hindi (hi)
- Kannada (kn)
"""

from typing import List, Dict, Any

GOVT_SCHEMES_DB = {
    "en": [
        {
            "id": "pmjay",
            "name": "Ayushman Bharat - PM-JAY",
            "full_name": "Pradhan Mantri Jan Arogya Yojana",
            "category": "Hospitalization & Treatment Cover",
            "coverage_amount": "₹5,00,000 per family per year",
            "summary": "World's largest government-funded healthcare assurance program providing ₹5 Lakhs cashless hospital coverage for secondary and tertiary care.",
            "key_benefits": [
                "100% Cashless and paperless treatment at all empaneled public & private hospitals across India.",
                "Covers up to 3 days of pre-hospitalization and 15 days of post-hospitalization diagnostic and medication costs.",
                "Pre-existing medical conditions (heart disease, diabetes, cancer) covered from Day 1.",
                "No restriction on family size, age, or gender."
            ],
            "eligibility": "Families listed in SECC 2011 database, NFSA ration card holders, and active Ayushman Card holders.",
            "how_to_apply": "Visit your nearest CSC (Common Service Centre) or empaneled hospital with Aadhaar and Ration Card, or apply online on beneficiary.nha.gov.in.",
            "helpline": "14555 / 1800-111-565",
            "official_url": "https://beneficiary.nha.gov.in"
        },
        {
            "id": "pmbjp",
            "name": "PM Jan Aushadhi (PMBJP)",
            "full_name": "Pradhan Mantri Bharatiya Janaushadhi Pariyojana",
            "category": "Affordable Generic Medicines",
            "coverage_amount": "50% to 90% Discount on Medicines",
            "summary": "Government initiative offering high-quality generic medicines, surgical items, and nutraceuticals at a fraction of branded market prices.",
            "key_benefits": [
                "Over 2,047 high-demand generic medicines and 300 surgical consumables available.",
                "Cardiovascular, diabetes, hypertension, and oncology drugs available at 50% to 90% cheaper prices.",
                "All batches certified by NABL-accredited and WHO-GMP compliant testing laboratories.",
                "Over 10,000+ Jan Aushadhi Kendras operating across India."
            ],
            "eligibility": "Open to all Indian citizens with any valid registered doctor's medical prescription.",
            "how_to_apply": "Locate the nearest Jan Aushadhi Kendra using the 'Jan Aushadhi Sugam' Mobile App or website.",
            "helpline": "1800-180-8080",
            "official_url": "https://janaushadhi.gov.in"
        },
        {
            "id": "arogya_karnataka",
            "name": "Arogya Karnataka (AB-ArK)",
            "full_name": "Ayushman Bharat - Arogya Karnataka Scheme",
            "category": "Karnataka State Health Insurance",
            "coverage_amount": "₹5 Lakhs (BPL) / 30% Subsidy (APL)",
            "summary": "State health scheme integrating Ayushman Bharat with Karnataka public health coverage for comprehensive tertiary and emergency care.",
            "key_benefits": [
                "Full cashless coverage up to ₹5 Lakhs for BPL/Eligible (AAY/PHH) ration card holders.",
                "30% subsidized treatment cost (up to ₹1.5 Lakhs) for General/APL card holders.",
                "Covers advanced surgeries, cardiac interventions, cancer therapy, and dialysis.",
                "Emergency 48-hour cashless trauma treatment under Mukhyamantri Santwana Harish Scheme."
            ],
            "eligibility": "All Karnataka residents holding a valid BPL/APL Ration Card and Aadhaar Card.",
            "how_to_apply": "Visit any Taluk/District Government Hospital or KarnatakaOne/GramOne centre with your Ration Card.",
            "helpline": "104 (Karnataka State Health Helpline)",
            "official_url": "https://arogya.karnataka.gov.in"
        },
        {
            "id": "ayushman_arogya_mandir",
            "name": "Ayushman Arogya Mandir",
            "full_name": "Health & Wellness Centres (AAM)",
            "category": "Free Screening & Primary Healthcare",
            "coverage_amount": "100% Free Diagnostics & Consultations",
            "summary": "Upgraded primary health facilities providing free comprehensive screening for chronic Non-Communicable Diseases (NCDs).",
            "key_benefits": [
                "Free screening for Type 2 Diabetes, Hypertension, Breast, Oral, and Cervical Cancers.",
                "Free provision of essential daily chronic medicines at local village/ward level.",
                "Free e-Sanjeevani Teleconsultation with specialist doctors and medical colleges.",
                "Free wellness and yoga sessions for preventive cardiovascular lifestyle health."
            ],
            "eligibility": "Free and universally accessible to all citizens without any documentation requirement.",
            "how_to_apply": "Walk into your local neighborhood Ayushman Arogya Mandir (Sub-Centre / PHC).",
            "helpline": "1075",
            "official_url": "https://ab-aam.nhp.gov.in"
        }
    ],
    "hi": [
        {
            "id": "pmjay",
            "name": "आयुष्मान भारत - पीएम-जय",
            "full_name": "प्रधानमंत्री जन आरोग्य योजना",
            "category": "अस्पताल भर्ती एवं निःशुल्क उपचार",
            "coverage_amount": "प्रति परिवार प्रति वर्ष ₹5,00,000",
            "summary": "विश्व की सबसे बड़ी सरकारी स्वास्थ्य बीमा योजना, जो माध्यमिक और तृतीयक देखभाल के लिए ₹5 लाख तक का कैशलेस इलाज प्रदान करती है।",
            "key_benefits": [
                "देशभर के सभी सूचीबद्ध सरकारी और निजी अस्पतालों में 100% कैशलेस और पेपरलेस इलाज।",
                "अस्पताल में भर्ती होने से 3 दिन पहले और 15 दिन बाद तक की दवाइयों और जांच का पूरा खर्च शामिल।",
                "पहले से मौजूद बीमारियां (हृदय रोग, मधुमेह, कैंसर) पहले दिन से कवर होती हैं।",
                "परिवार के आकार, आयु या लिंग की कोई सीमा नहीं।"
            ],
            "eligibility": "SECC 2011 डेटाबेस में शामिल परिवार, NFSA राशन कार्ड धारक और आयुष्मान कार्ड धारक।",
            "how_to_apply": "अपने नजदीकी सीएससी (जन सेवा केंद्र) या सूचीबद्ध अस्पताल में आधार और राशन कार्ड लेकर जाएं।",
            "helpline": "14555 / 1800-111-565",
            "official_url": "https://beneficiary.nha.gov.in"
        },
        {
            "id": "pmbjp",
            "name": "पीएम जन औषधि (PMBJP)",
            "full_name": "प्रधानमंत्री भारतीय जनऔषधि परियोजना",
            "category": "सस्ती एवं गुणवत्तापूर्ण जेनेरिक दवाइयां",
            "coverage_amount": "दवाइयों पर 50% से 90% तक की छूट",
            "summary": "बाजार के ब्रांडेड मूल्यों की तुलना में 50% से 90% कम कीमत पर उच्च गुणवत्ता वाली जेनेरिक दवाइयां उपलब्ध कराने की सरकारी पहल।",
            "key_benefits": [
                "2,000+ से अधिक आवश्यक जेनेरिक दवाइयां और 300 सर्जिकल उत्पाद उपलब्ध।",
                "हृदय रोग, शुगर, बीपी और कैंसर की दवाइयां 50-90% कम दाम पर।",
                "NABL और WHO-GMP प्रमाणित प्रयोगशालाओं द्वारा गुणवत्ता जांच।",
                "देशभर में 10,000+ से अधिक जन औषधि केंद्र कार्यरत।"
            ],
            "eligibility": "डॉक्टर के वैध पर्चे के साथ सभी भारतीय नागरिकों के लिए खुली है।",
            "how_to_apply": "'जन औषधि सुगम' मोबाइल ऐप या वेबसाइट से नजदीकी केंद्र खोजें।",
            "helpline": "1800-180-8080",
            "official_url": "https://janaushadhi.gov.in"
        },
        {
            "id": "arogya_karnataka",
            "name": "आरोग्य कर्नाटक (AB-ArK)",
            "full_name": "आयुष्मान भारत - आरोग्य कर्नाटक योजना",
            "category": "कर्नाटक राज्य स्वास्थ्य योजना",
            "coverage_amount": "₹5 लाख (BPL) / 30% छूट (APL)",
            "summary": "कर्नाटक के निवासियों के लिए तृतीयक और आपातकालीन स्वास्थ्य सुरक्षा योजना।",
            "key_benefits": [
                "BPL राशन कार्ड धारकों के लिए ₹5 लाख तक का संपूर्ण कैशलेस उपचार।",
                "APL धारकों के लिए उपचार खर्च पर 30% तक की सरकारी सब्सिडी।",
                "हार्ट सर्जरी, कैंसर कीमोथेरेपी और डायलिसिस की सुविधा शामिल।"
            ],
            "eligibility": "कर्नाटक राज्य के वैध राशन कार्ड और आधार कार्ड धारक नागरिक।",
            "how_to_apply": "तालुक/जिला सरकारी अस्पताल या कर्नाटक-वन केंद्र पर संपर्क करें।",
            "helpline": "104 (कर्नाटक स्वास्थ्य हेल्पलाइन)",
            "official_url": "https://arogya.karnataka.gov.in"
        },
        {
            "id": "ayushman_arogya_mandir",
            "name": "आयुष्मान आरोग्य मंदिर",
            "full_name": "हेल्थ एंड वेलनेस सेंटर",
            "category": "मुफ्त जांच एवं प्राथमिक उपचार",
            "coverage_amount": "100% मुफ्त जांच एवं परामर्श",
            "summary": "डायबिटीज, हाई बीपी और कैंसर जैसी बीमारियों की मुफ्त जांच और जरूरी दवाइयों के लिए प्राथमिक स्वास्थ्य केंद्र।",
            "key_benefits": [
                "शुगर, ब्लड प्रेशर और कैंसर की मुफ्त जांच।",
                "ई-संजीवनी के माध्यम से विशेषज्ञ डॉक्टरों से मुफ्त वीडियो परामर्श।",
                "दैनिक जीवनशैली की जरूरी दवाइयां मुफ्त उपलब्ध।"
            ],
            "eligibility": "सभी नागरिकों के लिए बिना किसी दस्तावेज के पूर्णतः मुफ्त।",
            "how_to_apply": "अपने नजदीकी आयुष्मान आरोग्य मंदिर या प्राथमिक स्वास्थ्य केंद्र (PHC) जाएं।",
            "helpline": "1075",
            "official_url": "https://ab-aam.nhp.gov.in"
        }
    ],
    "kn": [
        {
            "id": "pmjay",
            "name": "ಆಯುಷ್ಮಾನ್ ಭಾರತ್ - ಪಿಎಂ-ಜೆಎವೈ",
            "full_name": "ಪ್ರಧಾನ ಮಂತ್ರಿ ಜನ ಆರೋಗ್ಯ ಯೋಜನೆ",
            "category": "ಆಸ್ಪತ್ರೆ ಚಿಕಿತ್ಸೆ ಮತ್ತು ಉಚಿತ ವಿಮೆ",
            "coverage_amount": "ಪ್ರತಿ ಕುಟುಂಬಕ್ಕೆ ವಾರ್ಷಿಕ ₹5,00,000",
            "summary": "ದ್ವಿತೀಯ ಮತ್ತು ತೃತೀಯ ದರ್ಜೆಯ ಗಂಭೀರ ಕಾಯಿಲೆಗಳ ಚಿಕಿತ್ಸೆಗಾಗಿ ₹5 ಲಕ್ಷದವರೆಗೆ ಸಂಪೂರ್ಣ ನಗದು ರಹಿತ ಚಿಕಿತ್ಸೆ ನೀಡುವ ವಿಶ್ವದ ಬೃಹತ್ ಆರೋಗ್ಯ ಯೋಜನೆ.",
            "key_benefits": [
                "ದೇಶದ ಎಲ್ಲಾ ನೋಂದಾಯಿತ ಸರ್ಕಾರಿ ಮತ್ತು ಖಾಸಗಿ ಆಸ್ಪತ್ರೆಗಳಲ್ಲಿ 100% ಉಚಿತ ನಗದುರಹಿತ ಚಿಕಿತ್ಸೆ.",
                "ಆಸ್ಪತ್ರೆಗೆ ದಾಖಲಾಗುವ 3 ದಿನ ಮೊದಲಿನ ಮತ್ತು ಬಿಡುಗಡೆಯಾದ 15 ದಿನಗಳವರೆಗಿನ ಔಷಧಿ ಮತ್ತು ತಪಾಸಣೆ ವೆಚ್ಚ ಒಳಗೊಂಡಿದೆ.",
                "ಹೃದ್ರೋಗ, ಮಧುಮೇಹ ಮತ್ತು ಕ್ಯಾನ್ಸರ್‌ನಂತಹ ಮೊದಲೇ ಇರುವ ಕಾಯಿಲೆಗಳಿಗೂ ಮೊದಲ ದಿನದಿಂದಲೇ ರಕ್ಷಣೆ.",
                "ಕುಟುಂಬದ ಗಾತ್ರ ಅಥವಾ ವಯಸ್ಸಿನ ಯಾವುದೇ ಮಿತಿ ಇರುವುದಿಲ್ಲ."
            ],
            "eligibility": "SECC 2011 ಪಟ್ಟಿಯಲ್ಲಿರುವ ಕುಟುಂಬಗಳು, ಬಿಪಿಎಲ್ ಪಡಿತರ ಚೀಟಿ ಹೊಂದಿರುವವರು ಮತ್ತು ಆಯುಷ್ಮಾನ್ ಕಾರ್ಡ್ ಹೊಂದಿರುವವರು.",
            "how_to_apply": "ನಿಮ್ಮ ಹತ್ತಿರದ ಸಿಎಸ್‌ಸಿ ಕೇಂದ್ರ ಅಥವಾ ನೋಂದಾಯಿತ ಆಸ್ಪತ್ರೆಗೆ ಆಧಾರ್ ಮತ್ತು ರೇಷನ್ ಕಾರ್ಡ್ ಸಮೇತ ಭೇಟಿ ನೀಡಿ.",
            "helpline": "14555 / 1800-111-565",
            "official_url": "https://beneficiary.nha.gov.in"
        },
        {
            "id": "pmbjp",
            "name": "ಪಿಎಂ ಜನೌಷಧಿ (PMBJP)",
            "full_name": "ಪ್ರಧಾನ ಮಂತ್ರಿ ಭಾರತೀಯ ಜನೌಷಧಿ ಪರಿಯೋಜನೆ",
            "category": "ಕೈಗೆಟುಕುವ ದರದ ಗುಣಮಟ್ಟದ ಜೆನೆರಿಕ್ ಔಷಧಿಗಳು",
            "coverage_amount": "ಔಷಧಿಗಳ ಮೇಲೆ 50% ರಿಂದ 90% ರಿಯಾಯಿತಿ",
            "summary": "ಬ್ರಾಂಡೆಡ್ ಔಷಧಿಗಳಿಗಿಂತ 50% ರಿಂದ 90% ಕಡಿಮೆ ಬೆಲೆಗೆ ಉತ್ಕೃಷ್ಟ ಗುಣಮಟ್ಟದ ಜೆನೆರಿಕ್ ಔಷಧಿಗಳನ್ನು ಒದಗಿಸುವ ಕೇಂದ್ರ ಸರ್ಕಾರದ ಮಹತ್ವದ ಯೋಜನೆ.",
            "key_benefits": [
                "2,000ಕ್ಕೂ ಹೆಚ್ಚು ಅಗತ್ಯ ಜೆನೆರಿಕ್ ಔಷಧಿಗಳು ಮತ್ತು 300ಕ್ಕೂ ಹೆಚ್ಚು ಶಸ್ತ್ರಚಿಕಿತ್ಸಾ ಸಾಮಗ್ರಿಗಳು ಲಭ್ಯ.",
                "ಹೃದ್ರೋಗ, ಬಿಪಿ, ಶುಗರ್ ಹಾಗೂ ಕ್ಯಾನ್ಸರ್ ಔಷಧಿಗಳು ಅತ್ಯಂತ ಕಡಿಮೆ ಬೆಲೆಯಲ್ಲಿ ಲಭ್ಯ.",
                "NABL ಮತ್ತು WHO-GMP ಪ್ರಮಾಣೀಕೃತ ಗುಣಮಟ್ಟದ ಪರೀಕ್ಷೆ.",
                "ರಾಜ್ಯಾದ್ಯಂತ ಮತ್ತು ದೇಶಾದ್ಯಂತ 10,000ಕ್ಕೂ ಹೆಚ್ಚು ಜನೌಷಧಿ ಕೇಂದ್ರಗಳು ಲಭ್ಯ."
            ],
            "eligibility": "ವೈದ್ಯರ ಚೀಟಿ (Prescription) ಹೊಂದಿರುವ ಎಲ್ಲಾ ನಾಗರಿಕರಿಗೆ ಲಭ್ಯ.",
            "how_to_apply": "'Jan Aushadhi Sugam' ಮೊಬೈಲ್ ಆಪ್ ಅಥವಾ ವೆಬ್‌ಸೈಟ್ ಮೂಲಕ ಹತ್ತಿರದ ಜನೌಷಧಿ ಕೇಂದ್ರವನ್ನು ಪತ್ತೆಹಚ್ಚಿ.",
            "helpline": "1800-180-8080",
            "official_url": "https://janaushadhi.gov.in"
        },
        {
            "id": "arogya_karnataka",
            "name": "ಆರೋಗ್ಯ ಕರ್ನಾಟಕ (AB-ArK / ಯಶಸ್ವಿನಿ)",
            "full_name": "ಆಯುಷ್ಮಾನ್ ಭಾರತ್ - ಆರೋಗ್ಯ ಕರ್ನಾಟಕ ಮತ್ತು ಯಶಸ್ವಿನಿ ಯೋಜನೆ",
            "category": "ಕರ್ನಾಟಕ ರಾಜ್ಯ ಆರೋಗ್ಯ ರಕ್ಷಣೆ",
            "coverage_amount": "₹5 ಲಕ್ಷದವರೆಗೆ ಉಚಿತ (BPL) / 30% ರಿಯಾಯಿತಿ (APL)",
            "summary": "ಕರ್ನಾಟಕದ ಜನತೆಗಾಗಿ ಸರ್ಕಾರ ರೂಪಿಸಿರುವ ಸಮಗ್ರ ಆರೋಗ್ಯ ರಕ್ಷಣೆ ಮತ್ತು ತುರ್ತು ಚಿಕಿತ್ಸಾ ಯೋಜನೆ.",
            "key_benefits": [
                "ಬಿಪಿಎಲ್ ಕಾರ್ಡ್‌ದಾರರಿಗೆ ವಾರ್ಷಿಕ ₹5 ಲಕ್ಷದವರೆಗೆ ಸಂಪೂರ್ಣ ಉಚಿತ ಚಿಕಿತ್ಸೆ.",
                "ಎಪಿಎಲ್ ಕಾರ್ಡ್‌ದಾರರಿಗೆ ಚಿಕಿತ್ಸಾ ವೆಚ್ಚದಲ್ಲಿ 30% ರಿಯಾಯಿತಿ (ಗರಿಷ್ಠ ₹1.5 ಲಕ್ಷ).",
                "ರೈತರು ಮತ್ತು ಸಹಕಾರ ಸಂಘಗಳ ಸದಸ್ಯರಿಗೆ 'ಯಶಸ್ವಿನಿ' ಆರೋಗ್ಯ ಯೋಜನೆಯ ರಕ್ಷಣೆ.",
                "ಮುಖ್ಯಮಂತ್ರಿ ಸಾಂತ್ವನ ಹರೀಶ್ ಯೋಜನೆಯಡಿ ರಸ್ತೆ ಅಪಘಾತವಾದ ಮೊದಲ 48 ಗಂಟೆಗಳಲ್ಲಿ ಉಚಿತ ತುರ್ತು ಚಿಕಿತ್ಸೆ."
            ],
            "eligibility": "ಕರ್ನಾಟಕದ ನಿವಾಸಿಗಳು, ಬಿಪಿಎಲ್/ಎಪಿಎಲ್ ಪಡಿತರ ಚೀಟಿ ಮತ್ತು ಆಧಾರ್ ಕಾರ್ಡ್ ಹೊಂದಿರುವವರು.",
            "how_to_apply": "ತಾಲೂಕು ಅಥವಾ ಜಿಲ್ಲಾ ಸರ್ಕಾರಿ ಆಸ್ಪತ್ರೆ, ಅಥವಾ ಕರ್ನಾಟಕ ಒನ್ / ಗ್ರಾಮ ಒನ್ ಕೇಂದ್ರಗಳಿಗೆ ಭೇಟಿ ನೀಡಿ.",
            "helpline": "104 (ಕರ್ನಾಟಕ ಆರೋಗ್ಯ ಸಹಾಯವಾಣಿ)",
            "official_url": "https://arogya.karnataka.gov.in"
        },
        {
            "id": "ayushman_arogya_mandir",
            "name": "ಆಯುಷ್ಮಾನ್ ಆರೋಗ್ಯ ಮಂದಿರ",
            "full_name": "ಆರೋಗ್ಯ ಮತ್ತು ಕ್ಷೇಮ ಕೇಂದ್ರಗಳು (AAM)",
            "category": "ಉಚಿತ ತಪಾಸಣೆ ಮತ್ತು ಪ್ರಾಥಮಿಕ ಚಿಕಿತ್ಸೆ",
            "coverage_amount": "100% ಉಚಿತ ತಪಾಸಣೆ ಮತ್ತು ಸಮಾಲೋಚನೆ",
            "summary": "ಮಧುಮೇಹ, ರಕ್ತದೊತ್ತಡ ಮತ್ತು ಕ್ಯಾನ್ಸರ್ ಮುಂತಾದ ದೀರ್ಘಕಾಲಿಕ ಕಾಯಿಲೆಗಳ ಉಚಿತ ತಪಾಸಣೆ ಮತ್ತು ಔಷಧಿ ವಿತರಣಾ ಕೇಂದ್ರಗಳು.",
            "key_benefits": [
                "ಉಚಿತ ರಕ್ತದೊತ್ತಡ, ರಕ್ತದಲ್ಲಿನ ಸಕ್ಕರೆ ಅಂಶ ಮತ್ತು ಕ್ಯಾನ್ಸರ್ ಆರಂಭಿಕ ಹಂತದ ತಪಾಸಣೆ.",
                "ಇ-ಸಂಜೀವನಿ (e-Sanjeevani) ಮೂಲಕ ತಜ್ಞ ವೈದ್ಯರಿಂದ ಉಚಿತ ಟೆಲಿಕನ್ಸಲ್ಟೇಶನ್.",
                "ಗ್ರಾಮ ಮಟ್ಟದಲ್ಲೇ ದೈನಂದಿನ ಅಗತ್ಯ ಔಷಧಿಗಳ ಉಚಿತ ವಿತರಣೆ."
            ],
            "eligibility": "ಎಲ್ಲಾ ಸಾರ್ವಜನಿಕರಿಗೆ ಯಾವುದೇ ದಾಖಲೆಗಳಿಲ್ಲದೆ ಸಂಪೂರ್ಣ ಉಚಿತ.",
            "how_to_apply": "ನಿಮ್ಮ ಊರಿನ ಅಥವಾ ವಾರ್ಡ್‌ನ ಆಯುಷ್ಮಾನ್ ಆರೋಗ್ಯ ಮಂದಿರ / ಪ್ರಾಥಮಿಕ ಆರೋಗ್ಯ ಕೇಂದ್ರಕ್ಕೆ ಭೇಟಿ ನೀಡಿ.",
            "helpline": "1075",
            "official_url": "https://ab-aam.nhp.gov.in"
        }
    ]
}

def get_govt_schemes(language: str = "en") -> List[Dict[str, Any]]:
    lang_key = language.lower() if language.lower() in ("en", "hi", "kn") else "en"
    return GOVT_SCHEMES_DB.get(lang_key, GOVT_SCHEMES_DB["en"])
