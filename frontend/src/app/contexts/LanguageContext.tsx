import { createContext, useContext, useState, ReactNode } from 'react';

export type Language = 'en' | 'hi' | 'kn';

type Translations = Record<string, Record<Language, string>>;

const translations: Translations = {
  // Login Page
  'web3_credentialing': {
    en: 'Web3 credentialing for artisans',
    hi: 'कारीगरों के लिए Web3 क्रेडेंशियल',
    kn: 'ಕುಶಲಕರ್ಮಿಗಳಿಗೆ Web3 ರುಜುವಾತುಗಳು',
  },
  'welcome': {
    en: 'Welcome',
    hi: 'स्वागत है',
    kn: 'ಸ್ವಾಗತ',
  },
  'back': {
    en: 'back.',
    hi: 'वापस।',
    kn: 'ಮರಳಿ.',
  },
  'sign_in_continue': {
    en: 'Sign in to continue your journey',
    hi: 'अपनी यात्रा जारी रखने के लिए साइन इन करें',
    kn: 'ನಿಮ್ಮ ಪ್ರಯಾಣವನ್ನು ಮುಂದುವರಿಸಲು ಸೈನ್ ಇನ್ ಮಾಡಿ',
  },
  'phone_number': {
    en: 'Phone number',
    hi: 'फ़ोन नंबर',
    kn: 'ಫೋನ್ ಸಂಖ್ಯೆ',
  },
  'send_otp': {
    en: 'Send OTP',
    hi: 'OTP भेजें',
    kn: 'OTP ಕಳುಹಿಸಿ',
  },
  'enter_otp': {
    en: 'Enter OTP sent to',
    hi: 'पर भेजे गए OTP को दर्ज करें',
    kn: 'ಗೆ ಕಳುಹಿಸಲಾದ OTP ನಮೂದಿಸಿ',
  },
  'verify_continue': {
    en: 'Verify & continue',
    hi: 'सत्यापित करें और जारी रखें',
    kn: 'ಪರಿಶೀಲಿಸಿ ಮತ್ತು ಮುಂದುವರಿಸಿ',
  },
  'change_phone': {
    en: 'Change phone number',
    hi: 'फ़ोन नंबर बदलें',
    kn: 'ಫೋನ್ ಸಂಖ್ಯೆ ಬದಲಾಯಿಸಿ',
  },
  'artisan': {
    en: 'Artisan',
    hi: 'कारीगर',
    kn: 'ಕುಶಲಕರ್ಮಿ',
  },
  'nss_validator': {
    en: 'NSS Validator',
    hi: 'NSS वैलिडेटर',
    kn: 'NSS ಮೌಲ್ಯಮಾಪಕ',
  },
  'blockchain_verified': {
    en: 'Blockchain-verified credentials for rural artisans',
    hi: 'ग्रामीण कारीगरों के लिए ब्लॉकचेन-सत्यापित क्रेडेंशियल',
    kn: 'ಗ್ರಾಮೀಣ ಕುಶಲಕರ್ಮಿಗಳಿಗೆ ಬ್ಲಾಕ್‌ಚೈನ್-ಪರಿಶೀಲಿಸಿದ ರುಜುವಾತುಗಳು',
  },
  // Top Navigation
  'upload': {
    en: 'Upload',
    hi: 'अपलोड करें',
    kn: 'ಅಪ್‌ಲೋಡ್ ಮಾಡಿ',
  },
  'profile': {
    en: 'Profile',
    hi: 'प्रोफ़ाइल',
    kn: 'ಪ್ರೊಫೈಲ್',
  },
  'logout': {
    en: 'Logout',
    hi: 'लॉग आउट',
    kn: 'ಲಾಗ್ ಔಟ್',
  },
  // Hub Page
  'step_1_proof': {
    en: 'Step 1 · Proof of skill',
    hi: 'चरण 1 · कौशल का प्रमाण',
    kn: 'ಹಂತ 1 · ಕೌಶಲ್ಯದ ಪುರಾವೆ',
  },
  'show_us_what': {
    en: 'Show us what',
    hi: 'हमें दिखाएं कि',
    kn: 'ನಮಗೆ ತೋರಿಸಿ',
  },
  'you_can_do': {
    en: 'you can do.',
    hi: 'आप क्या कर सकते हैं।',
    kn: 'ನೀವು ಏನು ಮಾಡಬಹುದು.',
  },
  'record_video_desc': {
    en: 'Record a short video of your craft. A validator will review it and mint your verified credential.',
    hi: 'अपने शिल्प का एक छोटा वीडियो रिकॉर्ड करें। एक वैलिडेटर इसकी समीक्षा करेगा और आपका क्रेडेंशियल बनाएगा।',
    kn: 'ನಿಮ್ಮ ಕರಕುಶಲತೆಯ ಸಣ್ಣ ವೀಡಿಯೊವನ್ನು ರೆಕಾರ್ಡ್ ಮಾಡಿ. ಮೌಲ್ಯಮಾಪಕರು ಅದನ್ನು ಪರಿಶೀಲಿಸುತ್ತಾರೆ ಮತ್ತು ನಿಮ್ಮ ರುಜುವಾತು ನೀಡುತ್ತಾರೆ.',
  },
  'select_skill': {
    en: 'Select your skill',
    hi: 'अपना कौशल चुनें',
    kn: 'ನಿಮ್ಮ ಕೌಶಲ್ಯವನ್ನು ಆಯ್ಕೆಮಾಡಿ',
  },
  'choose_skill': {
    en: 'Choose a skill...',
    hi: 'एक कौशल चुनें...',
    kn: 'ಒಂದು ಕೌಶಲ್ಯವನ್ನು ಆರಿಸಿ...',
  },
  'video_proof': {
    en: 'Video proof',
    hi: 'वीडियो प्रमाण',
    kn: 'ವೀಡಿಯೊ ಪುರಾವೆ',
  },
  'drop_video_here': {
    en: 'Drop a video here',
    hi: 'वीडियो यहाँ छोड़ें',
    kn: 'ವೀಡಿಯೊವನ್ನು ಇಲ್ಲಿ ಬಿಡಿ',
  },
  'tap_to_record': {
    en: 'or tap to record / select a file',
    hi: 'या रिकॉर्ड करने / फ़ाइल चुनने के लिए टैप करें',
    kn: 'ಅಥವಾ ರೆಕಾರ್ಡ್ ಮಾಡಲು / ಫೈಲ್ ಆಯ್ಕೆ ಮಾಡಲು ಟ್ಯಾಪ್ ಮಾಡಿ',
  },
  'submit_for_validation': {
    en: 'Submit for validation',
    hi: 'सत्यापन के लिए सबमिट करें',
    kn: 'ಮೌಲ್ಯೀಕರಣಕ್ಕಾಗಿ ಸಲ್ಲಿಸಿ',
  },
  'submission_reviewed': {
    en: 'Your submission will be reviewed by an NSS validator',
    hi: 'आपकी प्रस्तुति की समीक्षा एक NSS वैलिडेटर द्वारा की जाएगी',
    kn: 'ನಿಮ್ಮ ಸಲ್ಲಿಕೆಯನ್ನು NSS ಮೌಲ್ಯಮಾಪಕರು ಪರಿಶೀಲಿಸುತ್ತಾರೆ',
  },
  'tailoring': {
    en: 'Tailoring',
    hi: 'सिलाई',
    kn: 'ಹೊಲಿಗೆ',
  },
  'handicrafts': {
    en: 'Handicrafts',
    hi: 'हस्तशिल्प',
    kn: 'ಕರಕುಶಲ ವಸ್ತುಗಳು',
  },
  'food_prep': {
    en: 'Food Prep',
    hi: 'भोजन की तैयारी',
    kn: 'ಆಹಾರ ತಯಾರಿಕೆ',
  },
  'beauty': {
    en: 'Beauty',
    hi: 'सौंदर्य',
    kn: 'ಸೌಂದರ್ಯ',
  },
  'domestic_work': {
    en: 'Domestic Work',
    hi: 'घरेलू काम',
    kn: 'ಮನೆ ಕೆಲಸ',
  },
  'manufacturing': {
    en: 'Manufacturing',
    hi: 'निर्माण',
    kn: 'ತಯಾರಿಕೆ',
  },
  // Profile Page
  'verified_artisan': {
    en: 'Verified Artisan',
    hi: 'सत्यापित कारीगर',
    kn: 'ಪರಿಶೀಲಿಸಿದ ಕುಶಲಕರ್ಮಿ',
  },
  'my_profile': {
    en: 'My Profile',
    hi: 'मेरी प्रोफ़ाइल',
    kn: 'ನನ್ನ ಪ್ರೊಫೈಲ್',
  },
  'verified_creds_desc': {
    en: 'Your verified credentials and unlocked opportunities',
    hi: 'आपके सत्यापित क्रेडेंशियल और अनलॉक किए गए अवसर',
    kn: 'ನಿಮ್ಮ ಪರಿಶೀಲಿಸಿದ ರುಜುವಾತುಗಳು ಮತ್ತು ಅನ್‌ಲಾಕ್ ಮಾಡಲಾದ ಅವಕಾಶಗಳು',
  },
  'master_tailor': {
    en: 'Master Tailor',
    hi: 'मास्टर दर्जी',
    kn: 'ಮಾಸ್ಟರ್ ಟೈಲರ್',
  },
  'certified_credential': {
    en: 'Certified credential',
    hi: 'प्रमाणित क्रेडेंशियल',
    kn: 'ಪ್ರಮಾಣೀಕೃತ ರುಜುವಾತು',
  },
  'skill_score': {
    en: 'Skill score',
    hi: 'कौशल स्कोर',
    kn: 'ಕೌಶಲ್ಯ ಸ್ಕೋರ್',
  },
  'issued': {
    en: 'Issued',
    hi: 'जारी किया गया',
    kn: 'ನೀಡಲಾಗಿದೆ',
  },
  'certificate_id': {
    en: 'Certificate ID',
    hi: 'प्रमाणपत्र ID',
    kn: 'ಪ್ರಮಾಣಪತ್ರ ID',
  },
  'qr_code': {
    en: 'QR Code',
    hi: 'QR कोड',
    kn: 'QR ಕೋಡ್',
  },
  'hide_jobs': {
    en: 'Hide jobs',
    hi: 'नौकरियां छिपाएं',
    kn: 'ಉದ್ಯೋಗಗಳನ್ನು ಮರೆಮಾಡಿ',
  },
  'view_unlocked_jobs': {
    en: 'View unlocked jobs',
    hi: 'अनलॉक की गई नौकरियां देखें',
    kn: 'ಅನ್‌ಲಾಕ್ ಮಾಡಲಾದ ಉದ್ಯೋಗಗಳನ್ನು ವೀಕ್ಷಿಸಿ',
  },
  'unlocked_local_jobs': {
    en: 'Unlocked local jobs',
    hi: 'अनलॉक की गई स्थानीय नौकरियां',
    kn: 'ಅನ್‌ಲಾಕ್ ಮಾಡಲಾದ ಸ್ಥಳೀಯ ಉದ್ಯೋಗಗಳು',
  },
  'apply': {
    en: 'Apply',
    hi: 'आवेदन करें',
    kn: 'ಅನ್ವಯಿಸು',
  },
  'certificates': {
    en: 'Certificates',
    hi: 'प्रमाणपत्र',
    kn: 'ಪ್ರಮಾಣಪತ್ರಗಳು',
  },
  'jobs_unlocked': {
    en: 'Jobs unlocked',
    hi: 'नौकरियां अनलॉक',
    kn: 'ಉದ್ಯೋಗಗಳು ಅನ್‌ಲಾಕ್ ಆಗಿವೆ',
  },
  // Jobs mock
  'senior_stitcher': {
    en: 'Senior Stitcher',
    hi: 'वरिष्ठ सिलाईकर्मी',
    kn: 'ಹಿರಿಯ ಹೊಲಿಗೆಗಾರ',
  },
  'pattern_designer': {
    en: 'Pattern Designer',
    hi: 'पैटर्न डिज़ाइनर',
    kn: 'ವಿನ್ಯಾಸಕಾರ',
  },
  'tailoring_instructor': {
    en: 'Tailoring Instructor',
    hi: 'सिलाई प्रशिक्षक',
    kn: 'ಹೊಲಿಗೆ ಬೋಧಕ',
  },
  'local_boutique': {
    en: 'Local Boutique',
    hi: 'स्थानीय बुटीक',
    kn: 'ಸ್ಥಳೀಯ ಅಂಗಡಿ',
  },
  'fashion_coop': {
    en: 'Fashion Co-op',
    hi: 'फैशन को-ऑप',
    kn: 'ಫ್ಯಾಷನ್ ಸಹಕಾರ',
  },
  'skill_center': {
    en: 'Skill Center',
    hi: 'कौशल केंद्र',
    kn: 'ಕೌಶಲ್ಯ ಕೇಂದ್ರ',
  },
  'downtown': {
    en: 'Downtown',
    hi: 'शहर का केंद्र',
    kn: 'ಡೌನ್ಟೌನ್',
  },
  'market_district': {
    en: 'Market District',
    hi: 'बाज़ार क्षेत्र',
    kn: 'ಮಾರುಕಟ್ಟೆ ಜಿಲ್ಲೆ',
  },
  'community_hub': {
    en: 'Community Hub',
    hi: 'सामुदायिक केंद्र',
    kn: 'ಸಮುದಾಯ ಕೇಂದ್ರ',
  },
};

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<Language>('en');

  const t = (key: string) => {
    return translations[key]?.[language] || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}
